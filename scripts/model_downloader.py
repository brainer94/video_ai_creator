"""Download project model requirements through ComfyUI-Model-Manager.

The project owns the small list of model URLs in :mod:`model_catalog`, while
the custom node owns file transfer, model-folder resolution, progress and
resume support. No SSH connection is required.
"""

from __future__ import annotations

import os
from copy import deepcopy
from scripts import comfyui_api
from scripts.model_catalog import expand_model_groups, get_model_groups


# ---------------------------------------------------------------------------
# ComfyUI-Model-Manager implementation
# ---------------------------------------------------------------------------
MODEL_MANAGER_NODE_ID = "modelmanager"
MODEL_MANAGER_REPOSITORY = "https://github.com/hayden-fr/ComfyUI-Model-Manager"
MODEL_MANAGER_INSTALL_MODES = ("remote", "default", "local")
_MODEL_MANAGER_NAMES = {
    "modelmanager",
    "comfyui-model-manager",
    "hayden-fr/comfyui-model-manager",
    "hayden-cn/comfyui-model-manager",
}


def _normalize_path(value) -> str:
    return str(value or "").strip().replace("\\", "/").strip("/")


def _node_text(value) -> str:
    if isinstance(value, str):
        return value.strip().lower().replace("_", "-")
    return ""


def _collect_strings(value, output: set[str]):
    if isinstance(value, str):
        output.add(_node_text(value))
    elif isinstance(value, dict):
        for child in value.values():
            _collect_strings(child, output)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _collect_strings(child, output)


def _is_model_manager_text(value) -> bool:
    text = _node_text(value)
    if text.endswith(".git"):
        text = text[:-4]
    return text in _MODEL_MANAGER_NAMES or text.endswith("/comfyui-model-manager")


def is_model_manager_installed(payload: dict) -> bool:
    """Return whether Manager reports ComfyUI-Model-Manager as installed."""
    if not isinstance(payload, dict):
        return False
    strings: set[str] = set()
    _collect_strings(payload, strings)
    return any(_is_model_manager_text(value) for value in strings)


def _is_model_manager_conflict_text(value) -> bool:
    text = _node_text(value)
    return (
        ("model-manager" in text or "modelmanager" in text)
        and not _is_model_manager_text(text)
    )


def _installed_node_conflicts(payload: dict) -> list[str]:
    if not isinstance(payload, dict):
        return []
    conflicts = []
    for key, value in payload.items():
        if isinstance(value, dict) and value.get("enabled") is False:
            continue
        candidates = [key]
        if isinstance(value, dict):
            candidates.extend(
                value.get(field)
                for field in ("id", "name", "title", "cnr_id", "aux_id", "repository")
            )
        if any(_is_model_manager_conflict_text(candidate) for candidate in candidates):
            label = str(key).strip()
            if label and label not in conflicts:
                conflicts.append(label)
    return conflicts


def get_model_manager_conflicts(server: str) -> list[str]:
    """Return installed custom nodes that collide with Model Manager routes."""
    for mode in ("default", "remote", "local"):
        try:
            payload = comfyui_api.get_installed_custom_nodes(server, mode=mode, timeout=30)
        except Exception:
            continue
        conflicts = _installed_node_conflicts(payload)
        if conflicts:
            return conflicts
    return []


def _get_installed_custom_nodes(server: str) -> bool:
    for mode in ("default", "remote", "local"):
        try:
            if is_model_manager_installed(
                comfyui_api.get_installed_custom_nodes(server, mode=mode, timeout=30)
            ):
                return True
        except Exception:
            continue
    return False


def check_model_manager_installed(server: str) -> bool:
    """Check installation across Manager database modes."""
    return _get_installed_custom_nodes(server)


def _iter_catalog_entries(payload: dict):
    """Yield custom-node catalog rows across Manager response variants."""
    if not isinstance(payload, dict):
        return
    node_packs = payload.get("node_packs", payload.get("custom_nodes", {}))
    if isinstance(node_packs, dict):
        for key, value in node_packs.items():
            if isinstance(value, dict):
                row = dict(value)
                row.setdefault("id", key)
                yield row
            elif isinstance(value, list):
                for child in value:
                    if isinstance(child, dict):
                        row = dict(child)
                        row.setdefault("id", key)
                        yield row
    elif isinstance(node_packs, list):
        for value in node_packs:
            if isinstance(value, dict):
                yield dict(value)


def _is_model_manager_entry(entry: dict) -> bool:
    if not isinstance(entry, dict):
        return False
    candidates = [
        entry.get("id"),
        entry.get("name"),
        entry.get("title"),
        entry.get("reference"),
        entry.get("repository"),
    ]
    if isinstance(entry.get("files"), list):
        candidates.extend(entry["files"])
    return any(_is_model_manager_text(value) for value in candidates)


def _find_model_manager_catalog_entry(payload: dict) -> dict | None:
    return next(
        (entry for entry in _iter_catalog_entries(payload) if _is_model_manager_entry(entry)),
        None,
    )


def _prepare_install_payload(entry: dict, catalog_payload: dict, mode: str) -> dict:
    """Normalize one catalog row for ``POST /manager/queue/install``."""
    payload = deepcopy(entry) if isinstance(entry, dict) else {}
    payload["id"] = str(payload.get("id") or MODEL_MANAGER_NODE_ID)
    payload.setdefault("title", "ComfyUI-Model-Manager")
    payload.setdefault("reference", MODEL_MANAGER_REPOSITORY)
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        payload["files"] = [MODEL_MANAGER_REPOSITORY]
    payload.setdefault("version", payload.get("active_version") or "unknown")
    payload.setdefault("selected_version", payload.get("version") or "unknown")
    payload.setdefault("channel", catalog_payload.get("channel", "default"))
    # Manager 3.x/legacy calls the locally cached default database ``cache``.
    # The catalog endpoint calls the same source ``remote``; sending that
    # catalog label back to the legacy worker makes the queued task fail.
    payload["mode"] = "local" if mode == "local" else "cache"
    payload.setdefault("ui_id", "video_ai_creator_model_manager")
    payload.setdefault("skip_post_install", False)
    return payload


def ensure_model_manager_installed(server: str) -> dict:
    """Install the custom node through Manager, without silently restarting."""
    conflicts = get_model_manager_conflicts(server)
    if conflicts:
        raise RuntimeError(
            "Custom node Model Manager lain masih terpasang dan memakai endpoint "
            "yang sama: " + ", ".join(conflicts) + ". Hapus atau nonaktifkan node "
            "tersebut melalui ComfyUI Manager, lalu restart ComfyUI."
        )
    if _get_installed_custom_nodes(server):
        return {
            "installed": True,
            "already_installed": True,
            "install_queued": False,
            "restart_required": False,
        }

    catalog_entry = None
    catalog_payload = None
    selected_mode = None
    errors = []
    for mode in MODEL_MANAGER_INSTALL_MODES:
        try:
            payload = comfyui_api.get_custom_node_list(
                server, mode=mode, skip_update=True, timeout=45
            )
            entry = _find_model_manager_catalog_entry(payload)
            if entry is not None:
                catalog_entry = entry
                catalog_payload = payload
                selected_mode = mode
                break
        except Exception as exc:
            errors.append(f"{mode}: {exc}")

    if catalog_entry is None or not isinstance(catalog_payload, dict):
        detail = f" Detail: {'; '.join(errors[:2])}" if errors else ""
        raise RuntimeError(
            "ComfyUI-Model-Manager belum ditemukan pada katalog ComfyUI Manager "
            "instance ini. Buka Manager, perbarui/fetch database custom node, "
            "lalu coba lagi." + detail
        )

    install_payload = _prepare_install_payload(
        catalog_entry, catalog_payload, selected_mode or "remote"
    )
    install_response = comfyui_api.queue_manager_custom_node_install(
        server, install_payload, timeout=30
    )
    start_response = comfyui_api.start_manager_queue(server, timeout=30)
    return {
        "installed": False,
        "already_installed": False,
        "install_queued": True,
        "restart_required": True,
        "catalog_mode": selected_mode,
        "manager_mode": install_payload.get("mode"),
        "install_response": install_response,
        "start_response": start_response,
    }


def _split_target(spec: dict) -> tuple[str, str, str]:
    save_path = _normalize_path(spec.get("save_path"))
    if "/" not in save_path:
        raise ValueError(f"Save path model tidak valid: {save_path}")
    folder, prefix = save_path.split("/", 1)
    filename = os.path.basename(_normalize_path(spec.get("runtime_name")))
    if not filename:
        raise ValueError(f"Nama file model tidak valid: {spec.get('runtime_name')}")
    fullname = "/".join(part for part in (prefix, filename) if part)
    # ``save_path`` already carries the ComfyUI folder name used by the
    # workflow (for example ``text_encoders``). Prefer it over the older
    # Manager model-type label such as ``clip``.
    return folder, fullname, filename


def _entry_fullname(item: dict) -> str:
    sub_folder = _normalize_path(item.get("subFolder", item.get("subfolder", "")))
    basename = _normalize_path(item.get("basename", ""))
    extension = str(item.get("extension", "") or "").strip()
    if basename and extension and not basename.lower().endswith(extension.lower()):
        basename = f"{basename}{extension}"
    if not basename:
        basename = _normalize_path(item.get("fullname", item.get("filename", "")))
    return "/".join(part for part in (sub_folder, basename) if part)


def _task_fullname(task: dict) -> str:
    return _normalize_path(task.get("fullname", ""))


def _task_type(task: dict) -> str:
    return _normalize_path(task.get("type", ""))


def _build_download_payload(spec: dict, folder: str, fullname: str) -> dict:
    return {
        "type": folder,
        "pathIndex": 0,
        "fullname": fullname,
        "description": str(spec.get("label", "")),
        # This custom node currently treats an omitted previewFile as an
        # uploaded file and rejects it before writing the .task file. An empty
        # string selects its harmless URL-preview path; the node logs and
        # ignores the empty preview URL, then creates the download task.
        "previewFile": "",
        "downloadPlatform": "huggingface",
        "downloadUrl": str(spec.get("url", "")),
        "sizeBytes": 0,
    }


def _load_model_state(server: str, specs: list[dict]) -> tuple[dict, dict[str, set[str]], dict[tuple[str, str], dict]]:
    """Load model roots, inventory, and active tasks in one consistent snapshot."""
    try:
        folders = comfyui_api.get_model_manager_folders(server, timeout=30)
    except Exception as exc:
        raise RuntimeError(
            "ComfyUI-Model-Manager belum aktif. Pasang melalui ComfyUI Manager "
            "dan restart ComfyUI, lalu coba lagi."
        ) from exc

    model_inventory: dict[str, set[str]] = {}
    for spec in specs:
        folder, _, _ = _split_target(spec)
        if folder in model_inventory:
            continue
        if folder not in folders:
            raise RuntimeError(
                f"Folder model ComfyUI '{folder}' tidak tersedia pada instance ini."
            )
        try:
            rows = comfyui_api.get_model_manager_models(server, folder, timeout=30)
        except Exception as exc:
            raise RuntimeError(
                f"Daftar model ComfyUI untuk folder '{folder}' tidak dapat dibaca."
            ) from exc
        model_inventory[folder] = {
            _entry_fullname(row)
            for row in rows
            if isinstance(row, dict) and not row.get("isFolder")
        }

    try:
        active_tasks = comfyui_api.get_model_manager_download_tasks(server, timeout=20)
    except Exception as exc:
        raise RuntimeError(
            "Daftar task ComfyUI-Model-Manager tidak dapat dibaca. Pastikan "
            "ComfyUI sudah selesai restart setelah pemasangan custom node."
        ) from exc

    task_inventory = {
        (_task_type(task), _task_fullname(task)): task
        for task in active_tasks
        if isinstance(task, dict)
    }
    return folders, model_inventory, task_inventory


def inspect_model_groups(server: str) -> dict[str, dict]:
    """Return completeness of every catalog group for dialog initialization.

    A group is complete only when every file in that group exists. A partially
    downloaded group remains selectable so the normal plan can skip its files
    that already exist and queue only the missing files.
    """
    groups = get_model_groups()
    all_specs = []
    specs_by_group: dict[str, list[dict]] = {}
    for group in groups:
        specs = expand_model_groups([group["id"]])
        specs_by_group[group["id"]] = specs
        all_specs.extend(specs)
    _, model_inventory, task_inventory = _load_model_state(server, all_specs)

    result = {}
    for group in groups:
        entries = []
        for spec in specs_by_group[group["id"]]:
            folder, fullname, _ = _split_target(spec)
            exists = fullname in model_inventory.get(folder, set())
            task = task_inventory.get((folder, fullname))
            entries.append({
                **spec,
                "target_type": folder,
                "target_fullname": fullname,
                "exists": exists,
                "task": task,
            })
        complete = bool(entries) and all(entry["exists"] for entry in entries)
        result[group["id"]] = {
            "group_id": group["id"],
            "label": group["label"],
            "entries": entries,
            "complete": complete,
            "present_count": sum(1 for entry in entries if entry["exists"]),
            "total_count": len(entries),
            "active_count": sum(1 for entry in entries if entry["task"]),
        }
    return result


def build_download_plan(server: str, group_ids) -> dict:
    """Build a plan using the custom node's real inventory and task list."""
    specs = expand_model_groups(group_ids)
    if not specs:
        raise ValueError("Pilih minimal satu kelompok model.")

    conflicts = get_model_manager_conflicts(server)
    if conflicts:
        raise RuntimeError(
            "Custom node Model Manager lain masih terpasang dan memakai endpoint "
            "yang sama: " + ", ".join(conflicts) + ". Hapus atau nonaktifkan node "
            "tersebut melalui ComfyUI Manager, lalu restart ComfyUI."
        )

    _, model_inventory, task_inventory = _load_model_state(server, specs)
    entries = []
    for spec in specs:
        folder, fullname, _ = _split_target(spec)
        # ComfyUI searches every configured model root. If the exact relative
        # path already exists on any root, do not create a duplicate download
        # into pathIndex 0.
        existing = fullname in model_inventory.get(folder, set())
        task = task_inventory.get((folder, fullname))
        if existing:
            status = "skipped"
        elif task:
            status = "queued"
        else:
            status = "pending"
        entry = {
            **spec,
            "status": status,
            "target_type": folder,
            "target_fullname": fullname,
            "path_index": 0,
            "payload": _build_download_payload(spec, folder, fullname),
            "error": "",
        }
        if task:
            entry["task_id"] = task.get("taskId")
            entry["task"] = task
        entries.append(entry)

    return {
        "entries": entries,
        "skipped": [entry for entry in entries if entry["status"] == "skipped"],
        "queued": [entry for entry in entries if entry["status"] == "queued"],
        "pending": [entry for entry in entries if entry["status"] == "pending"],
    }


def _response_task_id(response: dict) -> str:
    if not isinstance(response, dict):
        return ""
    data = response.get("data", response)
    if isinstance(data, dict):
        return str(data.get("taskId", data.get("task_id", "")) or "").strip()
    return ""


def queue_download_plan(server: str, plan: dict) -> dict:
    """Create missing custom-node tasks; each task starts immediately."""
    entries = list(plan.get("entries", [])) if isinstance(plan, dict) else []
    queued = [entry for entry in entries if entry.get("status") == "queued"]
    failed = [entry for entry in entries if entry.get("status") == "failed"]
    for entry in entries:
        if entry.get("status") != "pending":
            continue
        try:
            response = comfyui_api.create_model_manager_download_task(
                server, entry["payload"], timeout=30
            )
            task_id = _response_task_id(response)
            if not task_id:
                raise RuntimeError("ComfyUI-Model-Manager tidak mengembalikan taskId.")
            entry["queue_route"] = "model_manager"
            entry["task_id"] = task_id
            entry["status"] = "queued"
            entry["manager_response"] = response
            queued.append(entry)
        except Exception as exc:
            entry["status"] = "failed"
            entry["error"] = str(exc)
            failed.append(entry)
    return {
        "entries": entries,
        "queued": queued,
        "failed": failed,
        "skipped": [entry for entry in entries if entry.get("status") == "skipped"],
        "start_response": None,
    }


def get_model_manager_download_state(server: str, entries: list[dict]) -> dict:
    """Match custom-node task progress to the entries started by this dialog."""
    tasks = comfyui_api.get_model_manager_download_tasks(server, timeout=20)
    by_id = {
        str(task.get("taskId", "")).strip(): task
        for task in tasks
        if isinstance(task, dict) and task.get("taskId")
    }
    active = []
    failed = []
    for entry in entries:
        task_id = str(entry.get("task_id", "")).strip()
        task = by_id.get(task_id)
        if task is None:
            continue
        entry["task"] = task
        task_status = str(task.get("status", "")).lower()
        if task_status == "pause":
            entry["status"] = "failed"
            entry["error"] = str(
                task.get("error")
                or "Task ComfyUI-Model-Manager berhenti atau dijeda sebelum selesai."
            )
            failed.append(entry)
        else:
            entry["status"] = "downloading" if task_status == "doing" else "queued"
            active.append(entry)
    return {
        "entries": entries,
        "tasks": tasks,
        "active": active,
        "failed": failed,
        "finished_candidates": [
            entry for entry in entries if entry not in active and entry not in failed
        ],
    }


def verify_downloaded_models(server: str, entries: list[dict]) -> dict:
    """Verify final files through ComfyUI-Model-Manager's model inventory."""
    by_folder: dict[str, list[dict]] = {}
    for entry in entries:
        if entry.get("status") == "skipped":
            continue
        by_folder.setdefault(str(entry.get("target_type", "")), []).append(entry)

    verified = [entry for entry in entries if entry.get("status") == "skipped"]
    missing = []
    for folder, folder_entries in by_folder.items():
        try:
            rows = comfyui_api.get_model_manager_models(server, folder, timeout=30)
            inventory = {
                _entry_fullname(row)
                for row in rows
                if isinstance(row, dict) and not row.get("isFolder")
            }
        except Exception as exc:
            for entry in folder_entries:
                entry["status"] = "missing"
                entry["error"] = str(exc)
                missing.append(entry)
            continue
        for entry in folder_entries:
            if entry.get("target_fullname") in inventory:
                entry["status"] = "complete"
                verified.append(entry)
            else:
                if entry.get("status") != "failed":
                    entry["status"] = "missing"
                missing.append(entry)
    return {"entries": entries, "verified": verified, "missing": missing}

