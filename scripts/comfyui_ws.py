"""Optional ComfyUI WebSocket progress support.

This module is intentionally disabled and is not imported by the active
ComfyUI request path.  The official ComfyUI log endpoint remains the single
active source used by the UI.  The code is kept isolated here for a future
deployment that explicitly needs WebSocket progress events.
"""

import json
import re
import threading
import time
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from logging_config import get_logger, write_log

logger = get_logger(__name__)

# Keep this false until WebSocket progress is explicitly reintroduced and
# verified against the target ComfyUI deployment.
ENABLE_WEBSOCKET_PROGRESS_LOG = False


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
    token = str(token_values[0]).strip() if token_values else ""
    path = parsed.path.rstrip("/")
    if path in {"/docs", "/redoc", "/openapi.json"}:
        path = ""
    clean_base = urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
    return clean_base, token


def _websocket_url(server: str, client_id: str) -> str:
    """Build ComfyUI's WebSocket URL while preserving a tunnel token."""
    base, token = _split_server(server)
    parsed = urlsplit(base)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    path = parsed.path.rstrip("/") + "/ws"
    query = [("clientId", str(client_id))]
    if token:
        query.append(("token", token))
    return urlunsplit((scheme, parsed.netloc, path, urlencode(query), ""))


_FRIENDLY_NODE_TYPES = {
    "CLIPLoader": "Load CLIP",
    "CreateVideo": "Create Video",
    "KSampler": "Generate Image",
    "LoraLoaderModelOnly": "Load LoRA",
    "LoadImage": "Load Image",
    "LoadVideo": "Load Video",
    "MiniMaxH3ImageToVideo": "MiniMax H3 Image to Video",
    "MiniMaxH3ReferenceToVideo": "MiniMax H3 Reference to Video",
    "SaveImage": "Save Image",
    "SaveVideo": "Save Video",
    "SamplerCustomAdvanced": "Generate Video",
    "UNETLoader": "Load Diffusion Model",
    "VAEDecode": "Decode VAE",
    "VAEDecodeAudio": "Decode Audio VAE",
    "VAELoader": "Load VAE",
}


def _humanize_node_type(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "ComfyUI node"
    if text in _FRIENDLY_NODE_TYPES:
        return _FRIENDLY_NODE_TYPES[text]
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = text.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def build_node_labels(workflow_json: dict) -> dict[str, str]:
    """Build display labels from a workflow for a future WS consumer."""
    labels: dict[str, str] = {}
    if not isinstance(workflow_json, dict):
        return labels
    for node_id, node in workflow_json.items():
        if not isinstance(node, dict):
            continue
        node_key = str(node_id)
        inputs_meta = node.get("_meta")
        title = inputs_meta.get("title") if isinstance(inputs_meta, dict) else ""
        class_type = str(node.get("class_type") or "").strip()
        title = str(title or "").strip()
        if title and title.lower() != class_type.lower():
            labels[node_key] = title
        else:
            labels[node_key] = _humanize_node_type(class_type or title)
    return labels


def _format_elapsed(seconds: float) -> str:
    seconds = max(0, int(round(float(seconds or 0))))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def _format_progress_bar(percent: float, width: int = 10) -> str:
    percent = max(0.0, min(100.0, float(percent or 0.0)))
    scaled = (percent / 100.0) * width
    full_cells = min(width, int(scaled))
    return "#" * full_cells + "-" * max(0, width - full_cells)


class ComfyUIProgressListener:
    """Read progress events for one ComfyUI prompt on an optional WS thread."""

    def __init__(self, server: str, client_id: str, prompt_id: str, node_labels=None):
        self.server = server
        self.client_id = str(client_id)
        self.prompt_id = str(prompt_id)
        self.node_labels = {
            str(key): str(value)
            for key, value in dict(node_labels or {}).items()
            if str(value).strip()
        }
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name=f"comfyui-ws-{self.prompt_id[:8]}",
            daemon=True,
        )
        self._socket = None
        self._last_progress = {}
        self._node_started_at = {}
        self._announced_nodes = set()
        self._last_executing_node = None
        self._failure_logged = False

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        socket = self._socket
        if socket is not None:
            try:
                socket.close()
            except Exception:
                pass
        if self._thread.is_alive() and threading.current_thread() is not self._thread:
            self._thread.join(timeout=1.5)

    def update_prompt_id(self, prompt_id: str):
        if prompt_id:
            self.prompt_id = str(prompt_id)

    def _log_failure(self, message: str):
        if self._failure_logged:
            return
        self._failure_logged = True
        write_log(
            f"[ComfyUI] WebSocket progres tidak tersedia; render tetap dipantau melalui history. {message}",
            level="warning",
        )

    def _matches_prompt(self, data: dict) -> bool:
        event_prompt_id = data.get("prompt_id")
        return not event_prompt_id or str(event_prompt_id) == self.prompt_id

    @staticmethod
    def _number(value, default=0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def _node_label(self, node_id, metadata=None) -> str:
        metadata = metadata if isinstance(metadata, dict) else {}
        candidates = [
            node_id,
            metadata.get("display_node_id"),
            metadata.get("display_node"),
            metadata.get("real_node_id"),
            metadata.get("parent_node_id"),
        ]
        for candidate in candidates:
            key = str(candidate or "").strip()
            if key in self.node_labels:
                return self.node_labels[key]
        display_node = str(metadata.get("display_node") or "").strip()
        if display_node and not display_node.isdigit():
            return display_node
        node_key = str(node_id or "").strip()
        return self.node_labels.get(node_key) or f"Node {node_key or '?'}"

    def _emit_progress(self, node_id, value, maximum, state=None, metadata=None):
        maximum = self._number(maximum, 0.0)
        value = self._number(value, 0.0)
        if maximum <= 0:
            return
        percent = max(0.0, min(100.0, (value / maximum) * 100.0))
        node_key = str(node_id or "?")
        key = (value, maximum)
        if self._last_progress.get(node_key) == key:
            return
        self._last_progress[node_key] = key
        if node_key not in self._announced_nodes:
            write_log(f"[ComfyUI] Node: {self._node_label(node_id, metadata)}")
            self._announced_nodes.add(node_key)
        started_at = self._node_started_at.setdefault(node_key, time.monotonic())
        elapsed = max(0.0, time.monotonic() - started_at)
        if value > 0:
            seconds_per_step = elapsed / value
            remaining = max(0.0, (maximum - value) * seconds_per_step)
            timing = (
                f"[{_format_elapsed(elapsed)}<{_format_elapsed(remaining)}, "
                f"{seconds_per_step:.2f}s/it]"
            )
        else:
            timing = f"[{_format_elapsed(elapsed)}<?, ?it/s]"
        write_log(
            f"[ComfyUI] {percent:3.0f}%|{_format_progress_bar(percent)}| "
            f"{value:g}/{maximum:g} {timing}"
        )

    def _handle_message(self, message: dict) -> bool:
        message_type = str(message.get("type") or "")
        data = message.get("data")
        if not isinstance(data, dict) or not self._matches_prompt(data):
            return False

        if message_type == "progress":
            self._emit_progress(
                data.get("node"),
                data.get("value"),
                data.get("max"),
                metadata=data,
            )
        elif message_type == "progress_state":
            nodes = data.get("nodes")
            if isinstance(nodes, dict):
                for node_id, node_state in nodes.items():
                    if isinstance(node_state, dict):
                        self._emit_progress(
                            node_state.get("node_id") or node_id,
                            node_state.get("value"),
                            node_state.get("max"),
                            node_state.get("state"),
                            metadata=node_state,
                        )
        elif message_type == "executing":
            node_id = data.get("node")
            if node_id is None:
                write_log("[ComfyUI] Inferensi selesai.")
                return True
            node_key = str(node_id)
            self._node_started_at.setdefault(node_key, time.monotonic())
            if node_key != self._last_executing_node:
                if node_key not in self._announced_nodes:
                    write_log(f"[ComfyUI] Node: {self._node_label(node_id, data)}")
                    self._announced_nodes.add(node_key)
                self._last_executing_node = node_key
        elif message_type in {"execution_error", "execution_interrupted"}:
            error = data.get("exception_message") or data.get("message") or message_type
            write_log(f"[ComfyUI] {error}", level="error" if message_type == "execution_error" else "warning")
            return True
        return False

    def _run(self):
        try:
            import websocket
        except ImportError as exc:
            self._log_failure(f"Dependensi websocket-client belum tersedia: {exc}")
            return

        try:
            socket = websocket.create_connection(
                _websocket_url(self.server, self.client_id),
                timeout=5,
            )
            socket.settimeout(1.0)
            self._socket = socket
            while not self._stop_event.is_set():
                try:
                    raw_message = socket.recv()
                except websocket.WebSocketTimeoutException:
                    continue
                if raw_message is None:
                    break
                if isinstance(raw_message, bytes):
                    continue
                try:
                    message = json.loads(raw_message)
                except (TypeError, ValueError):
                    continue
                if isinstance(message, dict) and self._handle_message(message):
                    break
        except Exception as exc:
            if not self._stop_event.is_set():
                self._log_failure(str(exc))
            logger.debug("ComfyUI WebSocket listener stopped for %s: %s", self.prompt_id, exc)
        finally:
            socket = self._socket
            self._socket = None
            if socket is not None:
                try:
                    socket.close()
                except Exception:
                    pass


_progress_listeners = {}
_progress_listeners_lock = threading.Lock()


def start_progress_listener(server: str, client_id: str, prompt_id: str, node_labels=None):
    """Start the optional listener; returns None while the feature is disabled."""
    if not ENABLE_WEBSOCKET_PROGRESS_LOG:
        return None
    listener = ComfyUIProgressListener(server, client_id, prompt_id, node_labels=node_labels)
    with _progress_listeners_lock:
        _progress_listeners[str(prompt_id)] = listener
    listener.start()
    return listener


def stop_progress_listener(prompt_id: str):
    if not prompt_id:
        return
    with _progress_listeners_lock:
        listener = _progress_listeners.pop(str(prompt_id), None)
    if listener is not None:
        listener.stop()
