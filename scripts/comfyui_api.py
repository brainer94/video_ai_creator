import json
import re
import uuid

import requests
from scripts.timeout_config import COMFYUI_WORKFLOW_TIMEOUT_SECONDS
import os
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from logging_config import get_logger, write_log

logger = get_logger(__name__)

# ComfyUI can color native log records with ANSI escape sequences.  They are
# useful in a terminal, but become visible control characters in a Qt text
# widget (often rendered as little boxes).
_ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _strip_terminal_control_codes(value) -> str:
    """Return log text suitable for a plain text UI."""
    return _ANSI_ESCAPE_RE.sub("", str(value or "")).replace("\r", "")


def _split_server(server: str) -> tuple[str, str]:
    raw_server = str(server or "").strip()
    if not raw_server:
        raise ValueError("Alamat ComfyUI wajib diisi.")
    if not raw_server.startswith(("http://", "https://")):
        raw_server = "http://" + raw_server
    parsed = urlsplit(raw_server)
    if not parsed.netloc:
        raise ValueError(f"Alamat ComfyUI tidak valid: {server}")
    query = parse_qs(parsed.query, keep_blank_values=True)
    token_values = query.get("token", [])
    token = str(token_values[-1]).strip() if token_values else ""
    path = parsed.path.rstrip("/")
    # Vast.ai's Copy URL may point at the API documentation page. The actual
    # ComfyUI API is rooted at the same tunnel host.
    if path in {"/docs", "/redoc", "/openapi.json"}:
        path = ""
    base = urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
    return base, token


def _normalize_server(server: str) -> str:
    return _split_server(server)[0]


def _open_session(server: str, timeout: float = 20.0):
    """Open a ComfyUI session and bootstrap a Vast.ai tunnel token if present."""
    base, token = _split_server(server)
    session = requests.Session()
    if token:
        response = session.get(f"{base}/", params={"token": token}, timeout=timeout)
        response.raise_for_status()
    return base, session


def get_object_info(server: str, timeout: float = 20.0) -> dict:
    base, session = _open_session(server, timeout=timeout)
    response = session.get(f"{base}/object_info", timeout=timeout)
    response.raise_for_status()
    payload = response.json() if response.content else {}
    return payload if isinstance(payload, dict) else {}


def _manager_response_json(response):
    """Raise a diagnostic HTTP error and decode a Manager response."""
    if response.status_code >= 400:
        body = (response.text or "")[:4000]
        raise requests.HTTPError(
            f"{response.status_code} Client Error for url: {response.url}; response={body}"
        )
    if not response.content:
        return {}
    try:
        payload = response.json()
    except ValueError:
        return {"text": response.text}
    if isinstance(payload, dict):
        if payload.get("success") is False:
            raise RuntimeError(str(payload.get("error") or "ComfyUI Manager request failed."))
        return payload
    return {"value": payload}


def get_manager_queue_status(server: str, timeout: float = 20.0) -> dict:
    """Read the ComfyUI-Manager operation queue status."""
    base, session = _open_session(server, timeout=timeout)
    response = session.get(f"{base}/manager/queue/status", timeout=timeout)
    return _manager_response_json(response)


def start_manager_queue(server: str, timeout: float = 30.0) -> dict:
    """Start processing the ComfyUI-Manager operation queue."""
    base, session = _open_session(server, timeout=timeout)
    response = session.post(f"{base}/manager/queue/start", timeout=timeout)
    return _manager_response_json(response)


def restart_comfyui(server: str, timeout: float = 20.0) -> dict:
    """Request a ComfyUI restart through the Manager endpoint.

    The endpoint may return the temporary ComfyUI loading page instead of
    JSON, because the process starts restarting before the HTTP response is
    fully consumed. The caller should probe the server again before using it.
    """
    base, session = _open_session(server, timeout=timeout)
    response = session.post(f"{base}/manager/reboot", timeout=timeout)
    if response.status_code >= 400:
        return _manager_response_json(response)
    return {
        "status_code": response.status_code,
        "text": (response.text or "")[:200],
    }


def get_installed_custom_nodes(server: str, mode: str = "default", timeout: float = 30.0) -> dict:
    """Return the custom nodes installed on the connected ComfyUI server."""
    base, session = _open_session(server, timeout=timeout)
    response = session.get(
        f"{base}/customnode/installed",
        params={"mode": str(mode or "default")},
        timeout=timeout,
    )
    if response.status_code == 400 and mode:
        response = session.get(f"{base}/customnode/installed", timeout=timeout)
    return _manager_response_json(response)


def get_custom_node_list(
    server: str,
    mode: str = "remote",
    skip_update: bool = True,
    timeout: float = 45.0,
) -> dict:
    """Return the Manager custom-node catalog for the requested DB mode."""
    base, session = _open_session(server, timeout=timeout)
    response = session.get(
        f"{base}/customnode/getlist",
        params={
            "mode": str(mode or "remote"),
            "skip_update": "true" if skip_update else "false",
        },
        timeout=timeout,
    )
    if response.status_code == 400:
        response = session.get(
            f"{base}/customnode/getlist",
            params={"mode": str(mode or "remote")},
            timeout=timeout,
        )
    return _manager_response_json(response)


def queue_manager_custom_node_install(
    server: str,
    node_payload: dict,
    timeout: float = 30.0,
) -> dict:
    """Queue a custom-node installation through the official Manager API."""
    base, session = _open_session(server, timeout=timeout)
    response = session.post(
        f"{base}/manager/queue/install",
        json=dict(node_payload or {}),
        timeout=timeout,
    )
    return _manager_response_json(response)


def get_model_manager_models(server: str, folder: str, timeout: float = 30.0) -> list[dict]:
    """Return model files known by ComfyUI-Model-Manager for one folder."""
    base, session = _open_session(server, timeout=timeout)
    response = session.get(
        f"{base}/model-manager/models/{str(folder).strip()}",
        timeout=timeout,
    )
    payload = _manager_response_json(response)
    data = payload.get("data", []) if isinstance(payload, dict) else []
    return data if isinstance(data, list) else []


def get_model_manager_folders(server: str, timeout: float = 30.0) -> dict[str, list[str]]:
    """Return ComfyUI model roots exposed by ComfyUI-Model-Manager."""
    base, session = _open_session(server, timeout=timeout)
    response = session.get(f"{base}/model-manager/models", timeout=timeout)
    payload = _manager_response_json(response)
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    return data if isinstance(data, dict) else {}


def create_model_manager_download_task(
    server: str,
    task_payload: dict,
    timeout: float = 30.0,
) -> dict:
    """Create a download task in ComfyUI-Model-Manager.

    The custom node intentionally expects form data rather than JSON.  Its
    backend starts the task immediately and returns a task id.
    """
    base, session = _open_session(server, timeout=timeout)
    response = session.post(
        f"{base}/model-manager/model",
        data={str(key): str(value) for key, value in dict(task_payload or {}).items()},
        timeout=timeout,
    )
    return _manager_response_json(response)


def get_model_manager_download_tasks(server: str, timeout: float = 20.0) -> list[dict]:
    """Return active and resumable download tasks from the custom node."""
    base, session = _open_session(server, timeout=timeout)
    response = session.get(f"{base}/model-manager/download/task", timeout=timeout)
    payload = _manager_response_json(response)
    data = payload.get("data", []) if isinstance(payload, dict) else []
    return data if isinstance(data, list) else []


def _redact_url(url: str) -> str:
    try:
        parsed = urlsplit(str(url))
        query = parse_qs(parsed.query, keep_blank_values=True)
        if "token" in query:
            query["token"] = ["***"]
            redacted_query = urlencode(query, doseq=True)
            return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, redacted_query, parsed.fragment))
    except Exception:
        pass
    return str(url)


def get_recent_logs(server: str, limit: int = 200, timeout: float = 10.0) -> dict:
    """Return the latest ComfyUI log lines through its native log endpoint."""
    try:
        requested_limit = int(limit)
    except (TypeError, ValueError):
        requested_limit = 200
    requested_limit = max(1, requested_limit)
    base, session = _open_session(server, timeout=timeout)
    url = f"{base}/internal/logs/raw"
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json() if response.content else {}
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    if not isinstance(entries, list):
        raise ValueError("Respons log ComfyUI tidak memiliki entries yang valid.")

    lines = []
    for entry in entries:
        if isinstance(entry, dict):
            timestamp = str(entry.get("t", "")).strip()
            message = _strip_terminal_control_codes(entry.get("m", ""))
            # The native endpoint includes standalone newline/empty records.
            # Do not turn those records into misleading timestamp-only lines.
            message_lines = [line for line in message.splitlines() if line.strip()]
            if not message_lines:
                continue
            formatted_lines = [
                f"{timestamp} - {line}" if timestamp else line
                for line in message_lines
            ]
        else:
            message_lines = [
                line for line in _strip_terminal_control_codes(entry).splitlines()
                if line.strip()
            ]
            if not message_lines:
                continue
            formatted_lines = message_lines
        lines.extend(formatted_lines)

    return {
        "lines": lines[-requested_limit:],
        "count": len(lines),
        "endpoint": url,
    }



def post_workflow_api(workflow_json: dict, server: str):
    server, session = _open_session(server)
    # Keep the official request identifiers for ComfyUI compatibility.  The
    # optional WebSocket progress listener is isolated in scripts/comfyui_ws.py
    # and is intentionally not imported or started by the active path.
    client_id = uuid.uuid4().hex
    requested_prompt_id = str(uuid.uuid4())
    url_prompt = f"{server}/prompt"
    resp = session.post(
        url_prompt,
        json={
            "prompt": workflow_json,
            "client_id": client_id,
            "prompt_id": requested_prompt_id,
        },
    )
    if resp.status_code in {404, 405}:
        # Keep compatibility with older/custom deployments that expose only
        # the project's previous endpoint.
        url_api = f"{server}/api/workflow"
        resp = session.post(url_api, json=workflow_json)
        if resp.status_code >= 400:
            raise requests.HTTPError(
                f"{resp.status_code} Client Error for url: {url_api}; response={resp.text[:4000]}"
            )
        return resp.json()
    if resp.status_code >= 400:
        raise requests.HTTPError(
            f"{resp.status_code} Client Error for url: {url_prompt}; response={resp.text[:4000]}"
        )
    return resp.json()


def upload_file(server: str, file_path: str, file_type: str = "image"):
    server, session = _open_session(server)
    basename = os.path.basename(file_path)
    attempts = []
    if file_type == "image":
        attempts = [
            (f"{server}/upload/image", "image"),
            (f"{server}/api/upload/image", "image"),
            (f"{server}/upload/image", "file"),
            (f"{server}/api/upload/image", "file"),
        ]
    else:
        attempts = [
            (f"{server}/upload/{file_type}", file_type),
            (f"{server}/upload/{file_type}", "file"),
            (f"{server}/api/upload/{file_type}", file_type),
            (f"{server}/api/upload/{file_type}", "file"),
            # Some ComfyUI servers accept non-image inputs through the standard image upload endpoint.
            (f"{server}/upload/image", "image"),
            (f"{server}/api/upload/image", "image"),
        ]
    errors = []
    for url, field in attempts:
        try:
            with open(file_path, 'rb') as f:
                files = {field: (basename, f)}
                resp = session.post(url, files=files)
                # Collect response text for diagnostics if status >= 400
                if resp.status_code >= 400:
                    errors.append({'url': url, 'field': field, 'status': resp.status_code, 'text': resp.text[:1000]})
                    continue
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            errors.append({'url': url, 'field': field, 'error': str(e)})

    # All attempts failed; raise with diagnostic info
    raise Exception(f"Upload to /upload/{file_type} failed for {file_path}; attempts: {errors}")


def download_file_url(file_url: str, out_path: str):
    safe_url = _redact_url(file_url)
    write_log(f"download_file_url called: url={safe_url} out_path={out_path}", level='debug')
    resp = requests.get(file_url, stream=True)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    write_log(f"download_file_url succeeded: out_path={out_path}", level='debug')
    return out_path


def get_file_url(server: str, filename: str, subfolder: str = None, type_: str = None) -> str:
    server, token = _split_server(server)
    # If a full URL was passed as filename, return it unchanged
    if not filename:
        raise ValueError("filename must be provided")
    if filename.startswith('http://') or filename.startswith('https://'):
        return filename
    # URL-encode filename and optional subfolder to ensure valid query params.
    params = [("filename", filename)]
    if subfolder:
        params.append(("subfolder", subfolder))
    if type_:
        params.append(("type", type_))
    if token:
        params.append(("token", token))
    return f"{server}/view?{urlencode(params)}"


def get_history_for_prompt(
    server: str,
    prompt_id: str,
    timeout: int = COMFYUI_WORKFLOW_TIMEOUT_SECONDS,
    interval: float = 10.0,
    _session=None,
):
    """Poll the server's /history/{prompt_id} until the workflow produces outputs.

    This function repeatedly GETs the history URL every `interval` seconds until either
    a non-empty `outputs` entry appears in the returned JSON (indicating image/video
    outputs are available), or `timeout` seconds elapse. Returns the last JSON object
    received (or an empty dict if none).
    """
    if _session is None:
        server, session = _open_session(server, timeout=min(max(float(interval), 0.1), 30.0))
    else:
        server = _normalize_server(server)
        session = _session
    url = f"{server}/history/{prompt_id}"
    import time

    deadline = time.time() + timeout
    last_json = None
    # Simpler behavior: only consider top-level 'outputs' key as a signal
    while time.time() < deadline:
        # A temporary connection timeout must not fail the workflow outright:
        # ComfyUI can continue processing the prompt while its history endpoint
        # is briefly unreachable.  Bound each request so the outer workflow
        # deadline remains authoritative, then retry on the next poll.
        request_timeout = max(min(float(interval), 30.0), 0.1)
        try:
            resp = session.get(url, timeout=request_timeout)
            resp.raise_for_status()
        except (requests.Timeout, requests.ConnectionError) as exc:
            logger.debug("Temporary ComfyUI history polling failure for %s: %s", prompt_id, exc)
            remaining = deadline - time.time()
            if remaining > 0:
                time.sleep(min(max(float(interval), 0.1), remaining))
            continue
        try:
            j = resp.json()
        except Exception:
            j = None

        if isinstance(j, dict):
            # Direct outputs at top-level
            if 'outputs' in j and j.get('outputs'):
                return j
            # Some servers return a mapping keyed by prompt_id -> { ... , outputs: {...} }
            # handle the common case where the response is {prompt_id: {...}}
            if len(j) == 1:
                sole_val = next(iter(j.values()))
                if isinstance(sole_val, dict) and 'outputs' in sole_val and sole_val.get('outputs'):
                    return sole_val

        last_json = j
        time.sleep(interval)

    return last_json or {}


def wait_for_output(
    server: str,
    prompt_id: str,
    output_type: str = 'image',
    timeout: int = COMFYUI_WORKFLOW_TIMEOUT_SECONDS,
    interval: float = 2.0,
    output_node_ids=None,
    require_output_type: bool = False,
):
    """Poll history for a specific prompt_id until an output of type `output_type` appears.
    ``output_node_ids`` restricts matching to known output nodes in workflows
    that also expose input media as history items. ``require_output_type``
    rejects items explicitly marked as ``type=input``.
    """
    import time
    deadline = time.time() + timeout
    server_base, session = _open_session(
        server,
        timeout=min(max(float(interval), 0.1), 30.0),
    )
    output_node_ids = {
        str(node_id).strip()
        for node_id in (output_node_ids or [])
        if str(node_id).strip()
    }

    def _collect_from_outputs(outputs):
        """Collect a matching media item from the selected history nodes."""
        if not isinstance(outputs, dict):
            return None
        # outputs: node_id -> {kind: [items]}
        for node_id, node_val in outputs.items():
            if output_node_ids and str(node_id) not in output_node_ids:
                continue
            if not isinstance(node_val, dict):
                continue
            for kind, items in node_val.items():
                if not isinstance(items, list):
                    continue
                for it in items:
                    if isinstance(it, dict) and 'filename' in it:
                        fn = it.get('filename')
                        sub = it.get('subfolder')
                        typ = it.get('type') or kind
                        explicit_type = str(it.get('type') or '').strip().lower()
                        if require_output_type and explicit_type and explicit_type not in {'output', 'outputs'}:
                            continue
                        if fn and _matches_type_by_ext(fn, output_type):
                            return {
                                'filename': fn,
                                'subfolder': sub,
                                'type': typ,
                                'node_id': str(node_id),
                            }
        return None

    while time.time() < deadline:
        # Do not nest the default 500-second history wait inside this timeout.
        # Poll history for at most one interval so the caller's deadline remains
        # authoritative (previously a 600-second wait could last ~17 minutes).
        remaining = max(0.0, deadline - time.time())
        history_timeout = min(max(float(interval), 0.1), remaining)
        hist = get_history_for_prompt(
            server_base,
            prompt_id,
            timeout=history_timeout,
            interval=min(max(float(interval), 0.1), history_timeout),
            _session=session,
        )
        if not isinstance(hist, dict):
            continue

        outputs = hist.get('outputs')
        if outputs:
            info = _collect_from_outputs(outputs)
            if info:
                return info

        remaining = deadline - time.time()
        if remaining > 0 and outputs:
            time.sleep(min(float(interval), remaining))
    return None


def _matches_type_by_ext(filename: str, output_type: str) -> bool:
    filename = filename.lower()
    image_ext = ('.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp')
    video_ext = ('.mp4', '.mov', '.webm', '.avi', '.mkv')
    if output_type == 'image':
        return filename.endswith(image_ext)
    if output_type == 'video':
        return filename.endswith(video_ext)
    return False
