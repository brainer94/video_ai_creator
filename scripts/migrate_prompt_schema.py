"""Migrate project prompt JSON to the direct English prompt schema.

The migration is deliberately conservative: only known prompt-bearing slots
are rewritten. Metadata, scene settings, references, and non-prompt JSON are
left untouched. On ``--apply`` every changed file is copied to a timestamped
backup before it is written.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from minimax_h3.minimax_h3_prompt import (
    normalize_ref2va_authoring_prompt,
    parse_ref2va_detailed_description,
    unwrap_prompt_value,
    validate_ref2va_prompt,
)
from prompt_localization import (
    GROUP_PROMPT_FIELDS,
    MINIMAX_H3_I2V_PANJANG_PROMPT_FILENAME,
    MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME,
    PROMPT_TOP_LEVEL_FIELDS,
    ADDITIONAL_TOP_LEVEL_PROMPT_FIELDS,
)


PROMPT_TOP_LEVEL_FIELDS = {
    **PROMPT_TOP_LEVEL_FIELDS,
    **ADDITIONAL_TOP_LEVEL_PROMPT_FIELDS,
}

DEFAULT_GEMINI_PROMPT_MODEL = "gemini-3.1-flash-lite"


def _canonicalize_prompt_generation(value) -> dict:
    config = value if isinstance(value, dict) else {}
    model = str(config.get("model", "")).strip()
    if not model or model.startswith(("qwen", "llama", "ollama")):
        model = DEFAULT_GEMINI_PROMPT_MODEL
    return {"model": model}


def _canonical(value):
    """Return the English value from a legacy wrapper, or the value itself."""
    return copy.deepcopy(unwrap_prompt_value(value))


def _canonicalize_r2v(data: dict) -> dict:
    result = copy.deepcopy(data)
    entry = _canonical(result.get("positive_prompt"))
    if not isinstance(entry, dict):
        return result

    # R2V used to persist detailed_description as one prose field. The new
    # authoring contract keeps that prose intact in the shot visual field and
    # only changes its container shape.
    if not isinstance(entry.get("shots"), list):
        try:
            duration = float(result.get("duration", 5.0) or 5.0)
        except (TypeError, ValueError):
            duration = 5.0
        parsed = parse_ref2va_detailed_description(
            entry.get("detailed_description", ""),
            duration=duration,
        )
        entry["style_opening"] = parsed.get("style_opening", "")
        entry["shots"] = parsed.get("shots", [])
        # Preserve even a legacy empty terminal marker without allowing it to
        # invalidate the canonical numeric timeline. The serializer ignores
        # empty shot prose, so the original scene text remains unchanged.
        for shot in entry["shots"]:
            if isinstance(shot, dict):
                try:
                    start = float(shot.get("start", 0.0))
                    end = float(shot.get("end", start))
                except (TypeError, ValueError):
                    start, end = 0.0, 0.001
                if end <= start:
                    shot["end"] = start + 0.001
        entry.pop("detailed_description", None)
    entry.setdefault("mode", "R2VA")
    result["positive_prompt"] = entry

    errors = validate_ref2va_prompt(entry)
    if errors:
        raise ValueError("R2V setelah migrasi tidak valid: " + "; ".join(errors[:3]))
    return result


def canonicalize_json(filename: str, data: dict) -> dict:
    """Canonicalize prompt slots in one JSON document."""
    result = copy.deepcopy(data or {})

    if filename in {
        MINIMAX_H3_I2V_PANJANG_PROMPT_FILENAME,
        MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME,
    }:
        prompts = result.get("prompts")
        if isinstance(prompts, list):
            result["prompts"] = [_canonical(item) for item in prompts]
            if filename == MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME:
                result["prompts"] = [
                    normalize_ref2va_authoring_prompt(item)
                    for item in result["prompts"]
                ]
        return result

    if filename == "minimax_h3_r2v_prompt.json":
        return _canonicalize_r2v(result)

    for key in PROMPT_TOP_LEVEL_FIELDS.get(filename, []):
        if key in result:
            result[key] = _canonical(result[key])

    group_fields = GROUP_PROMPT_FIELDS.get(filename, [])
    groups = result.get("groups")
    if isinstance(groups, list) and group_fields:
        for item in groups:
            if not isinstance(item, dict):
                continue
            for key in group_fields:
                if key in item:
                    item[key] = _canonical(item[key])

    if filename == "project_settings.json":
        # Prompt translation is no longer a project capability. Drop the
        # obsolete configuration block while preserving all active settings.
        result.pop("translate", None)
        result["prompt_generation"] = _canonicalize_prompt_generation(
            result.get("prompt_generation")
        )
        if isinstance(result.get("cover"), dict):
            result["cover"] = canonicalize_json("project_settings_cover.json", result["cover"])

    if filename == "server_config.json":
        result.pop("runtime_controller", None)
        result["prompt_generation"] = _canonicalize_prompt_generation(
            result.get("prompt_generation")
        )

    return result


def _legacy_keys(value, path=()):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"id_new", "id_old", "en"}:
                found.append(".".join((*path, str(key))))
            found.extend(_legacy_keys(child, (*path, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_legacy_keys(child, (*path, f"[{index}]")))
    return found


def _json_files(root: Path):
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def migrate(root: Path, apply: bool, backup_root: Path | None = None) -> int:
    root = root.resolve()
    if root.name.casefold() == "backup_production":
        raise ValueError("backup_production adalah rollback source dan tidak boleh dimigrasikan.")
    if not root.is_dir():
        raise FileNotFoundError(f"Folder project tidak ditemukan: {root}")

    changes = []
    for path in _json_files(root):
        with path.open("r", encoding="utf-8") as handle:
            source = json.load(handle)
        migrated = canonicalize_json(path.name, source)
        remaining = _legacy_keys(migrated)
        if remaining:
            raise ValueError(
                f"Wrapper lama masih ditemukan di {path.relative_to(root)}: "
                + ", ".join(remaining[:8])
            )
        if migrated != source:
            changes.append((path, source, migrated))

    print(f"root={root}")
    print(f"json_files={len(_json_files(root))}")
    print(f"changed_files={len(changes)}")
    if not changes:
        print("status=already_canonical")
        return 0
    if not apply:
        print("status=dry_run")
        for path, _, _ in changes[:20]:
            print(f"would_change={path.relative_to(root)}")
        if len(changes) > 20:
            print(f"would_change_more={len(changes) - 20}")
        return 0

    if backup_root is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = root.parent / ".prompt_migration_backups" / stamp
    backup_root = backup_root.resolve()
    backup_root.mkdir(parents=True, exist_ok=False)

    manifest = {
        "source": str(root),
        "backup": str(backup_root),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "files": [],
    }
    for path, _, migrated in changes:
        relative = path.relative_to(root)
        backup_path = backup_root / relative
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(migrated, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        manifest["files"].append(str(relative))

    with (backup_root / "manifest.json").open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"status=applied")
    print(f"backup={backup_root}")
    print(f"manifest={backup_root / 'manifest.json'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default="api_production",
        help="Folder project yang dimigrasikan (default: api_production).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Tulis perubahan setelah membuat backup file yang berubah.",
    )
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=None,
        help="Lokasi backup eksplisit; folder harus belum ada.",
    )
    args = parser.parse_args()
    return migrate(Path(args.root), apply=args.apply, backup_root=args.backup_root)


if __name__ == "__main__":
    raise SystemExit(main())
