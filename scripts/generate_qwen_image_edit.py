import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from qwen_image_edit.qwen_image_edit import (
    ENGINE_MINIMAX_H3_IMAGE,
    MAX_REFERENCE_IMAGES,
    MINIMAX_SAMPLER_NODE,
    build_qwen_image_edit_workflow,
    engine_label,
    normalize_engine,
)
from logging_config import setup_logging, write_log
from prompt_localization import read_json_for_runtime
from scripts import comfyui_api
from scripts.server_config import get_server_address
from scripts.timeout_config import COMFYUI_WORKFLOW_TIMEOUT_SECONDS, SHORT_POLL_INTERVAL_SECONDS


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def _extract_uploaded_name(upload_info: dict, fallback_name: str) -> str:
    for key in ("name", "filename", "file"):
        value = str(upload_info.get(key, "")).strip()
        if value:
            return value
    return fallback_name


def _resolve_scene_image(scene_dir: Path, image_name: str) -> Path:
    name = str(image_name or "").strip()
    if not name:
        raise RuntimeError("Nama gambar referensi kosong.")
    scene_root = scene_dir.resolve()
    image_path = (scene_dir / name).resolve()
    try:
        image_path.relative_to(scene_root)
    except ValueError as exc:
        raise RuntimeError(f"Path gambar referensi tidak valid: {name}") from exc
    if not image_path.is_file():
        raise RuntimeError(f"Gambar referensi tidak ditemukan: {name}")
    if image_path.suffix.lower() not in IMAGE_EXTS:
        raise RuntimeError(f"File gambar referensi tidak didukung: {name}")
    return image_path


def _download_comfy_image(server: str, image_out: dict, output_dir: Path) -> Path:
    image_filename = image_out.get("filename") or image_out.get("name") or image_out.get("file")
    if not image_filename:
        raise RuntimeError(f"Tidak bisa membaca filename output image: {json.dumps(image_out)}")
    image_url = comfyui_api.get_file_url(
        server,
        image_filename,
        subfolder=image_out.get("subfolder"),
        type_=image_out.get("type"),
    )
    output_path = output_dir / image_filename
    comfyui_api.download_file_url(image_url, str(output_path))
    if not output_path.exists() or output_path.stat().st_size <= 0:
        raise RuntimeError(f"File hasil download kosong/tidak ada: {output_path}")
    return output_path


def _load_prompt(scene_dir: Path, prompt_file: str, resolve_runtime: bool = True) -> dict:
    filename = str(prompt_file or "qwen_image_edit_prompt.json").strip() or "qwen_image_edit_prompt.json"
    prompt_path = scene_dir / filename
    if not prompt_path.exists():
        raise RuntimeError(f"File prompt tidak ditemukan: {filename}")
    if resolve_runtime:
        payload = read_json_for_runtime(str(prompt_path), required=True, log_fn=write_log)
    else:
        with prompt_path.open("r", encoding="utf-8") as prompt_handle:
            payload = json.load(prompt_handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Format file prompt tidak valid: {filename}")
    payload["engine"] = normalize_engine(payload.get("engine"))
    if not str(payload.get("positive_prompt", "")).strip():
        raise RuntimeError("Prompt positif Image Edit wajib diisi.")
    images = payload.get("images", [])
    if not isinstance(images, list):
        images = []
    payload["images"] = [str(images[index] if index < len(images) else "").strip() for index in range(MAX_REFERENCE_IMAGES)]
    return payload


def process_scene(scene_dir: Path, server: str, prompt: dict) -> Path:
    prompt = dict(prompt or {})
    prompt["engine"] = normalize_engine(prompt.get("engine"))
    try:
        number_of_edits = int(prompt.get("number_of_edits", 1))
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Jumlah Edit harus berupa bilangan bulat lebih besar dari 0.") from exc
    if number_of_edits <= 0:
        raise RuntimeError("Jumlah Edit harus lebih besar dari 0.")
    configured_images = prompt.get("images", [])
    uploaded_images = []
    for image_name in configured_images[:MAX_REFERENCE_IMAGES]:
        image_name = str(image_name or "").strip()
        if not image_name:
            uploaded_images.append("")
            continue
        source_path = _resolve_scene_image(scene_dir, image_name)
        upload_info = comfyui_api.upload_file(server, str(source_path), file_type="image")
        uploaded_images.append(_extract_uploaded_name(upload_info, source_path.name))
    uploaded_images.extend([""] * (MAX_REFERENCE_IMAGES - len(uploaded_images)))

    if prompt["engine"] == ENGINE_MINIMAX_H3_IMAGE and not any(uploaded_images):
        raise RuntimeError("MiniMax H3 Image membutuhkan minimal satu gambar referensi.")

    used_random_seeds = set()
    last_output_path = None
    for edit_index in range(number_of_edits):
        workflow = build_qwen_image_edit_workflow(prompt, uploaded_images=uploaded_images)
        seed_node_id = MINIMAX_SAMPLER_NODE if prompt["engine"] == ENGINE_MINIMAX_H3_IMAGE else "507"
        seed = workflow.get(seed_node_id, {}).get("inputs", {}).get("seed")
        if bool(prompt.get("use_random_seed", True)):
            while seed in used_random_seeds:
                workflow = build_qwen_image_edit_workflow(prompt, uploaded_images=uploaded_images)
                seed = workflow.get(seed_node_id, {}).get("inputs", {}).get("seed")
            used_random_seeds.add(seed)
        write_log(
            f"{engine_label(prompt['engine'])} {edit_index + 1}/{number_of_edits}: "
            f"mengirim workflow baru, seed={seed}"
        )
        result = comfyui_api.post_workflow_api(workflow, server)
        prompt_id = result.get("prompt_id") or result.get("id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI tidak mengembalikan prompt_id: {json.dumps(result)}")
        write_log(f"{engine_label(prompt['engine'])} workflow terkirim, prompt_id={prompt_id}")

        image_out = comfyui_api.wait_for_output(
            server,
            prompt_id,
            output_type="image",
            timeout=COMFYUI_WORKFLOW_TIMEOUT_SECONDS,
            interval=SHORT_POLL_INTERVAL_SECONDS,
        )
        if not image_out:
            raise RuntimeError(f"Output image tidak ditemukan (prompt_id={prompt_id})")
        last_output_path = _download_comfy_image(server, image_out, scene_dir)
        write_log(f"{engine_label(prompt['engine'])} {edit_index + 1}/{number_of_edits} selesai: {last_output_path}")
    return last_output_path


def main():
    parser = argparse.ArgumentParser(description="Generate Image Edit for one scene")
    parser.add_argument("--server", "-s", default=get_server_address("comfyui"), help="ComfyUI server host:port")
    parser.add_argument("--project", "-p", required=True, help="Nama project di dalam folder api_production")
    parser.add_argument("--scene", "-S", required=True, help="Nama scene, contoh scene_1")
    parser.add_argument("--prompt-file", default="qwen_image_edit_prompt.json", help="Nama file prompt scene")
    parser.add_argument("--number-of-edits", type=int, default=1, help="Jumlah workflow Image Edit yang dikirim")
    args = parser.parse_args()

    setup_logging()
    scene_dir = Path(PROJECT_ROOT) / "api_production" / str(args.project).strip() / str(args.scene).strip()
    if not scene_dir.is_dir():
        write_log(f"Folder scene tidak ditemukan: {scene_dir}", level="error")
        print("Scene folder not found")
        return 1

    try:
        if args.number_of_edits <= 0:
            raise RuntimeError("Jumlah Edit harus lebih besar dari 0.")
        prompt = _load_prompt(scene_dir, args.prompt_file)
        write_log(f"[{engine_label(prompt['engine'])}] Mengirim workflow ke ComfyUI")
        prompt["number_of_edits"] = args.number_of_edits

        output_path = process_scene(scene_dir, args.server, prompt)
        print(f"OK: {output_path}")
        return 0
    except Exception as exc:
        write_log(f"Gagal generate Image Edit: {exc}", level="error")
        print(f"Failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
