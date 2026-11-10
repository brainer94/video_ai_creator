"""Download user-provided LoRA files through ComfyUI-Model-Manager."""

from __future__ import annotations

import os
from copy import deepcopy
from urllib.parse import urlsplit

from scripts import comfyui_api


LORA_CATEGORIES = (
    {
        "id": "minimax_h3",
        "label": "MiniMax H3",
        "prefix": "MINIMAX-H3",
        "save_path": "loras/MINIMAX-H3",
    },
    {
        "id": "flux2",
        "label": "Flux 2",
        "prefix": "FLUX.2",
        "save_path": "loras/FLUX.2",
    },
    {
        "id": "z_image",
        "label": "Z Image",
        "prefix": "Z-IMAGE",
        "save_path": "loras/Z-IMAGE",
    },
)


def get_lora_categories() -> list[dict]:
    return deepcopy(list(LORA_CATEGORIES))


def get_lora_category(category_id: str) -> dict:
    key = str(category_id or "").strip()
    for category in LORA_CATEGORIES:
        if category["id"] == key:
            return deepcopy(category)
    raise ValueError("Kategori LoRA tidak valid.")


def detect_lora_platform(url: str) -> str:
    value = str(url or "").strip()
    parsed = urlsplit(value)
    host = str(parsed.hostname or "").casefold()
    if host == "huggingface.co" or host.endswith(".huggingface.co"):
        return "huggingface"
    if host == "civitai.com" or host.endswith(".civitai.com"):
        return "civitai"
    raise ValueError("URL LoRA harus berasal dari Hugging Face atau Civitai.")


def validate_lora_filename(filename: str) -> str:
    normalized = str(filename or "").strip().replace("\\", "/")
    value = os.path.basename(normalized)
    if not value or value in {".", ".."} or "/" in normalized:
        raise ValueError("Nama file LoRA harus berupa satu nama file tanpa subfolder.")
    if ".." in value or value.startswith("."):
        raise ValueError("Nama file LoRA tidak valid.")
    if not value.casefold().endswith((".safetensors", ".ckpt", ".pt", ".pth", ".bin")):
        raise ValueError("Nama file LoRA harus berakhiran .safetensors, .ckpt, .pt, .pth, atau .bin.")
    return value


def _normalize_path(value) -> str:
    return str(value or "").strip().replace("\\", "/").strip("/")


def _entry_fullname(item: dict) -> str:
    subfolder = _normalize_path(item.get("subFolder", item.get("subfolder", "")))
    basename = _normalize_path(item.get("basename", ""))
    extension = str(item.get("extension", "") or "").strip()
    if basename and extension and not basename.casefold().endswith(extension.casefold()):
        basename = f"{basename}{extension}"
    if not basename:
        basename = _normalize_path(item.get("fullname", item.get("filename", "")))
    return "/".join(part for part in (subfolder, basename) if part)


def _task_fullname(task: dict) -> str:
    return _normalize_path(task.get("fullname", ""))


def _task_type(task: dict) -> str:
    return _normalize_path(task.get("type", ""))


def build_lora_entry(server: str, url: str, category_id: str, filename: str) -> dict:
    value = str(url or "").strip()
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL LoRA harus berupa URL HTTP(S) yang valid.")
    category = get_lora_category(category_id)
    platform = detect_lora_platform(value)
    safe_filename = validate_lora_filename(filename)
    fullname = f"{category['prefix']}/{safe_filename}"
    return {
        "server": str(server or "").strip(),
        "url": value,
        "platform": platform,
        "category_id": category["id"],
        "category_label": category["label"],
        "prefix": category["prefix"],
        "target_type": "loras",
        "save_path": category["save_path"],
        "filename": safe_filename,
        "fullname": fullname,
        "payload": {
            "type": "loras",
            "pathIndex": 0,
            "fullname": fullname,
            "description": f"{category['label']} LoRA",
            "previewFile": "",
            "downloadPlatform": platform,
            "downloadUrl": value,
            "sizeBytes": 0,
        },
        "status": "pending",
        "task_id": "",
        "task": None,
        "error": "",
    }


def plan_lora_download(server: str, url: str, category_id: str, filename: str) -> dict:
    entry = build_lora_entry(server, url, category_id, filename)
    folders = comfyui_api.get_model_manager_folders(server, timeout=30)
    if "loras" not in folders:
        raise RuntimeError("Folder loras tidak tersedia pada ComfyUI-Model-Manager.")

    rows = comfyui_api.get_model_manager_models(server, "loras", timeout=30)
    inventory = {
        _entry_fullname(row)
        for row in rows
        if isinstance(row, dict) and not row.get("isFolder")
    }
    tasks = comfyui_api.get_model_manager_download_tasks(server, timeout=20)
    active_tasks = {
        (_task_type(task), _task_fullname(task)): task
        for task in tasks
        if isinstance(task, dict)
    }
    if entry["fullname"] in inventory:
        entry["status"] = "skipped"
    else:
        task = active_tasks.get(("loras", entry["fullname"]))
        if task:
            entry["status"] = "queued"
            entry["task"] = task
            entry["task_id"] = str(task.get("taskId", "")).strip()
    return entry


def queue_lora_download(entry: dict) -> dict:
    if entry.get("status") != "pending":
        return entry
    try:
        response = comfyui_api.create_model_manager_download_task(
            entry["server"], entry["payload"], timeout=30
        )
        data = response.get("data", response) if isinstance(response, dict) else {}
        task_id = str(data.get("taskId", data.get("task_id", "")) or "").strip()
        if not task_id:
            raise RuntimeError("ComfyUI-Model-Manager tidak mengembalikan taskId.")
        entry["status"] = "queued"
        entry["task_id"] = task_id
        entry["manager_response"] = response
    except Exception as exc:
        entry["status"] = "failed"
        entry["error"] = str(exc)
    return entry


def get_lora_download_state(entry: dict) -> dict:
    tasks = comfyui_api.get_model_manager_download_tasks(entry["server"], timeout=20)
    task_id = str(entry.get("task_id", "")).strip()
    task = next(
        (
            item for item in tasks
            if isinstance(item, dict) and str(item.get("taskId", "")).strip() == task_id
        ),
        None,
    )
    if task is None:
        return {"status": "finished", "task": None, "tasks": tasks}
    entry["task"] = task
    task_status = str(task.get("status", "")).casefold()
    if task_status == "pause":
        entry["status"] = "failed"
        entry["error"] = str(task.get("error") or "Task download LoRA berhenti atau dijeda.")
    elif task_status == "doing":
        entry["status"] = "downloading"
    else:
        entry["status"] = "queued"
    return {"status": entry["status"], "task": task, "tasks": tasks}


def verify_lora_download(entry: dict) -> dict:
    rows = comfyui_api.get_model_manager_models(entry["server"], "loras", timeout=30)
    inventory = {
        _entry_fullname(row)
        for row in rows
        if isinstance(row, dict) and not row.get("isFolder")
    }
    verified = entry["fullname"] in inventory
    entry["status"] = "complete" if verified else "missing"
    return {"verified": verified, "entry": entry}
