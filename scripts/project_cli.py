import argparse
import copy
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scene_manager_ui import (
    API_PRODUCTION,
    DEFAULT_PROJECT_SETTINGS,
    DEFAULT_Z_IMAGE_PROMPT,
    create_project_on_disk,
    create_scene_in_project,
    list_scene_dirs_in_project,
)

SCENE_TYPE_CHOICES = [
    "minimax-h3_t2v",
    "minimax-h3_i2v",
    "minimax-h3_i2v-panjang",
    "minimax-h3_s2v",
    "minimax-h3_r2v",
    "minimax-h3_r2v-panjang",
    "i2v",
    "image_pan",
    "image_zoom",
]


def parse_duration(value: str) -> int | float:
    """Parse seconds while preserving integer values for existing CLI output."""
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("Durasi harus berupa angka.") from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise argparse.ArgumentTypeError("Durasi harus berupa angka finite yang tidak negatif.")
    return int(parsed) if parsed.is_integer() else parsed
VOICE_PROVIDER_CHOICES = [
    "gemini",
]


def str_to_bool(value: str) -> bool:
    normalized = str(value or "").strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError("Gunakan true/false, yes/no, atau 1/0.")


def build_project_settings(args) -> dict:
    settings = copy.deepcopy(DEFAULT_PROJECT_SETTINGS)
    settings["project_description"] = args.description or ""
    settings["video_size"] = {
        "width": int(args.width),
        "height": int(args.height),
    }
    settings["prompt_generation"] = {
        "model": str(args.prompt_generation_model or settings["prompt_generation"]["model"]).strip(),
    }
    settings["voice"] = {
        "voice_provider": str(args.voice_provider or settings["voice"]["voice_provider"]).strip(),
    }
    settings["caption"] = {
        "generate_caption": bool(args.generate_caption),
    }
    settings["cover"] = copy.deepcopy(DEFAULT_Z_IMAGE_PROMPT)
    settings["cover"]["width"] = int(args.width)
    settings["cover"]["height"] = int(args.height)
    return settings


def command_create_project(args) -> int:
    project_settings = build_project_settings(args)
    project_dir, _saved_settings = create_project_on_disk(
        args.project,
        create_default_scene=bool(args.with_default_scene),
        project_settings=project_settings,
    )
    scene_count = len(list_scene_dirs_in_project(project_dir))
    print(f"Project created: {project_dir}")
    print(f"Scenes created: {scene_count}")
    return 0


def command_create_scene(args) -> int:
    project_dir = API_PRODUCTION / args.project
    scene_dir = create_scene_in_project(
        project_dir,
        scene_type=args.scene_type,
        scene_title=args.title or "",
        scene_description=args.scene_description or "",
        voice_text=args.voice_text or "",
        duration=args.duration,
    )
    print(f"Scene created: {scene_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI helper untuk membuat project dan scene dengan jalur yang sama seperti UI."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_project_parser = subparsers.add_parser(
        "create-project",
        help="Buat project baru. Default-nya project kosong tanpa scene.",
    )
    create_project_parser.add_argument("--project", "-p", required=True, help="Nama project di api_production.")
    create_project_parser.add_argument("--description", default="", help="Deskripsi project.")
    create_project_parser.add_argument("--width", type=int, default=480, help="Lebar video project.")
    create_project_parser.add_argument("--height", type=int, default=848, help="Tinggi video project.")
    create_project_parser.add_argument(
        "--prompt-generation-model",
        default=DEFAULT_PROJECT_SETTINGS["prompt_generation"]["model"],
        help="Model untuk prompt generation project.",
    )
    create_project_parser.add_argument(
        "--voice-provider",
        choices=VOICE_PROVIDER_CHOICES,
        default=DEFAULT_PROJECT_SETTINGS["voice"]["voice_provider"],
        help="Provider voice default project.",
    )
    create_project_parser.add_argument(
        "--generate-caption",
        type=str_to_bool,
        default=DEFAULT_PROJECT_SETTINGS["caption"]["generate_caption"],
        help="Aktifkan caption otomatis: true/false.",
    )
    create_project_parser.add_argument(
        "--with-default-scene",
        action="store_true",
        help="Ikuti perilaku tombol UI dan buat scene_1 default.",
    )
    create_project_parser.set_defaults(func=command_create_project)

    create_scene_parser = subparsers.add_parser(
        "create-scene",
        help="Tambah scene baru ke project yang sudah ada.",
    )
    create_scene_parser.add_argument("--project", "-p", required=True, help="Nama project di api_production.")
    create_scene_parser.add_argument(
        "--scene-type",
        required=True,
        choices=SCENE_TYPE_CHOICES,
        help="Tipe scene.",
    )
    create_scene_parser.add_argument("--title", default="", help="Judul scene.")
    create_scene_parser.add_argument("--scene-description", default="", help="Deskripsi scene.")
    create_scene_parser.add_argument("--voice-text", default="", help="Voice text scene.")
    create_scene_parser.add_argument(
        "--duration",
        type=parse_duration,
        default=10,
        help="Durasi scene dalam detik; scene MiniMax dapat memakai hingga 4 angka desimal.",
    )
    create_scene_parser.set_defaults(func=command_create_scene)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
