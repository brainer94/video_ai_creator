import copy
import base64
import json
import mimetypes
import os
import ast
import logging
import re
import time
from pathlib import Path
from typing import Callable

import requests
from scripts.timeout_config import LLM_CALL_TIMEOUT_SECONDS

from gemini.gemini_image import find_gemini_key
from scripts.server_config import load_server_config
from minimax_h3.minimax_h3_prompt import (
    REF2VA_SECTION_KEYS,
    normalize_ref2va_authoring_prompt,
    serialize_ref2va_prompt,
    validate_ref2va_prompt,
    normalize_minimax_prompt_payload,
    parse_structured_response,
    prompt_entry_to_display,
    serialize_structured_prompt,
    unwrap_prompt_value,
    validate_structured_prompt,
)
from minimax_h3.minimax_h3_r2v_panjang import PROMPT_FILENAME as MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME


LOGGER = logging.getLogger(__name__)

QWEN_IMAGE_EDIT_SYSTEM_PROMPT_URL = (
    "https://github.com/QwenLM/Qwen-Image-2.1/blob/main/prompt_rewrite/prompts/system_prompt_edit.txt"
)
QWEN_IMAGE_EDIT_SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parent / "qwen_image_edit" / "system_prompt_edit.txt"
)


def _load_qwen_image_edit_system_prompt() -> str:
    try:
        prompt = QWEN_IMAGE_EDIT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(
            "System prompt Qwen Image Edit tidak ditemukan: "
            f"{QWEN_IMAGE_EDIT_SYSTEM_PROMPT_PATH}"
        ) from exc
    if not prompt:
        raise RuntimeError("System prompt Qwen Image Edit kosong.")
    return prompt


DEFAULT_PROMPT_GENERATION_MODEL = "gemini-3.1-flash-lite"


def format_llm_runtime_log(
    provider: str,
    phase: str,
    model: str,
    elapsed_seconds: float | None,
    tok_per_sec: float | None,
    status: str = "sukses",
    extra_parts: list[str] | None = None,
) -> str:
    provider = str(provider or "").strip().lower() or "unknown"
    phase = str(phase or "").strip() or "call"
    model = str(model or "").strip() or "n/a"
    status = str(status or "").strip() or "sukses"
    parts = [
        f"[{provider}] {phase} {status}",
        f"model={model}",
        f"elapsed={elapsed_seconds:.3f}s" if isinstance(elapsed_seconds, (int, float)) else "elapsed=n/a",
        f"tok/s={tok_per_sec:.2f}" if isinstance(tok_per_sec, (int, float)) else "tok/s=n/a",
    ]
    if extra_parts:
        parts.extend(str(part) for part in extra_parts if str(part).strip())
    return " | ".join(parts)


PROMPT_TOP_LEVEL_FIELDS = {
    "z_image_prompt.json": ["positive_prompt", "negative_prompt"],
    "qwen_image_edit_prompt.json": ["positive_prompt", "negative_prompt"],
    "minimax_h3_t2v_prompt.json": ["positive_prompt"],
    "minimax_h3_i2v_prompt.json": ["positive_prompt"],
    "minimax_h3_s2v_prompt.json": ["positive_prompt"],
    "minimax_h3_r2v_prompt.json": ["positive_prompt"],
    "project_settings_cover.json": ["positive_prompt", "negative_prompt"],
    "project_settings.json": [],
    "scene_meta.json": ["sound_prompt"],
}

GROUP_PROMPT_FIELDS = {
    "z_image_extra_prompts.json": ["positive_prompt", "negative_prompt"],
    "image_edit_prompt.json": ["prompt"],
    "wan22_t2v_batch_extra_prompts.json": ["positive_prompt", "negative_prompt"],
}

ADDITIONAL_TOP_LEVEL_PROMPT_FIELDS = {
    "wan22_i2v_prompt.json": [
        "positive_prompt_one", "negative_prompt_one",
        "positive_prompt_two", "negative_prompt_two",
    ],
    "wan22_s2v_prompt.json": ["positive_prompt", "negative_prompt"],
    "wan22_t2v_prompt.json": ["positive_prompt", "negative_prompt"],
}

MINIMAX_H3_I2V_PANJANG_PROMPT_FILENAME = "minimax_h3_i2v_panjang_prompt.json"

LORA_TRIGGER_WORDS_FIELD = "lora_trigger_words"

TRIGGER_WORD_PROMPT_FIELDS = {
    "z_image_prompt.json": ["positive_prompt"],
    "z_image_extra_prompts.json": ["positive_prompt"],
}

class GeminiPromptTranslator:
    def __init__(
        self,
        prompt_generation_model_name: str = DEFAULT_PROMPT_GENERATION_MODEL,
    ):
        self.prompt_generation_model_name = str(prompt_generation_model_name or "").strip() or DEFAULT_PROMPT_GENERATION_MODEL
        self.api_key = find_gemini_key()
        self.last_call_metrics: dict | None = None

    def _call_text_model(
        self,
        model_name: str,
        instruction: str,
        text: str,
        timeout: int = LLM_CALL_TIMEOUT_SECONDS,
        phase: str = "call",
        image_parts: list[dict] | None = None,
    ) -> str:
        if not self.api_key:
            raise RuntimeError(
                "Gemini API key tidak ditemukan. Tambahkan GEMINIKEY / GEMINI_API_KEY / GOOGLE_API_KEY di keys.cfg."
            )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            f"?key={self.api_key}"
        )
        parts = [
            {"text": instruction},
            {"text": text},
        ]
        parts.extend(image_parts or [])
        payload = {
            "contents": [
                {
                    "parts": parts,
                }
            ],
            "generationConfig": {},
        }

        start_time = time.perf_counter()
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            elapsed_seconds = time.perf_counter() - start_time
            if response.status_code >= 400:
                self.last_call_metrics = {
                    "provider": "gemini",
                    "model": model_name,
                    "elapsed_seconds": elapsed_seconds,
                    "tok_per_sec": None,
                    "prompt_token_count": None,
                    "candidates_token_count": None,
                    "total_token_count": None,
                    "status_code": response.status_code,
                    "ok": False,
                }
                LOGGER.error(
                    format_llm_runtime_log(
                        "gemini",
                        phase,
                        model_name,
                        elapsed_seconds,
                        None,
                        status="gagal",
                        extra_parts=[f"status_code={response.status_code}", f"error={response.text[:600]}"],
                    )
                )
                raise RuntimeError(f"Gemini error {response.status_code}: {response.text[:600]}")

            response_payload = response.json()
            generated_text = _clean_text(_extract_text_from_gemini_response(response_payload))
            usage = response_payload.get("usageMetadata") or response_payload.get("usage_metadata") or {}
            if not isinstance(usage, dict):
                usage = {}

            prompt_token_count = usage.get("promptTokenCount", usage.get("prompt_token_count"))
            candidates_token_count = usage.get("candidatesTokenCount", usage.get("candidates_token_count"))
            total_token_count = usage.get("totalTokenCount", usage.get("total_token_count"))

            tok_per_sec = None
            if isinstance(candidates_token_count, (int, float)) and elapsed_seconds > 0:
                tok_per_sec = float(candidates_token_count) / elapsed_seconds

            self.last_call_metrics = {
                "provider": "gemini",
                "model": model_name,
                "elapsed_seconds": elapsed_seconds,
                "tok_per_sec": tok_per_sec,
                "prompt_token_count": prompt_token_count,
                "candidates_token_count": candidates_token_count,
                "total_token_count": total_token_count,
                "status_code": response.status_code,
                "ok": True,
            }
            LOGGER.info(
                format_llm_runtime_log(
                    "gemini",
                    phase,
                    model_name,
                    elapsed_seconds,
                    tok_per_sec,
                    extra_parts=[
                        f"prompt_tokens={prompt_token_count}" if prompt_token_count is not None else None,
                        f"output_tokens={candidates_token_count}" if candidates_token_count is not None else None,
                        f"total_tokens={total_token_count}" if total_token_count is not None else None,
                    ],
                )
            )
            return generated_text
        except requests.RequestException as exc:
            elapsed_seconds = time.perf_counter() - start_time
            self.last_call_metrics = {
                "provider": "gemini",
                "model": model_name,
                "elapsed_seconds": elapsed_seconds,
                "tok_per_sec": None,
                "prompt_token_count": None,
                "candidates_token_count": None,
                "total_token_count": None,
                "status_code": None,
                "ok": False,
                "error": str(exc),
            }
            LOGGER.error(
                format_llm_runtime_log(
                    "gemini",
                    phase,
                    model_name,
                    elapsed_seconds,
                    None,
                    status="gagal",
                    extra_parts=[f"error={exc}"],
                )
            )
            raise


    def generate_prompt_to_english(self, text: str, context: str = "") -> str:
        text = _clean_text(text)
        if not text:
            return ""
        instruction = (
            "You are a senior AI prompt engineer.\n"
            "Rewrite the prompt into a polished English prompt for image generation.\n"
            "Preserve the subject, composition, style, lighting, atmosphere, and important details.\n"
            "Use the provided context to improve the prompt.\n"
            "Return only the English prompt without bullet points, quotes, or explanation."
        )
        payload_text = _compose_prompt_request_text(text, context)
        generated = self._call_text_model(
            self.prompt_generation_model_name,
            instruction,
            payload_text,
            timeout=LLM_CALL_TIMEOUT_SECONDS,
            phase="generate_prompt_to_english",
        )
        return generated or text


def _load_qwen_multimodal_image_payloads(image_paths: list[str | Path]) -> list[dict]:
    payloads = []
    for index, raw_path in enumerate(image_paths, start=1):
        path = Path(raw_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Gambar referensi Qwen tidak ditemukan: {path}")
        mime_type = mimetypes.guess_type(path.name)[0] or ""
        if not mime_type.startswith("image/"):
            raise ValueError(f"File referensi Qwen bukan gambar: {path.name}")
        payloads.append(
            {
                "label": f"<image{index}>",
                "name": path.name,
                "path": str(path),
                "mime_type": mime_type,
                "base64": base64.b64encode(path.read_bytes()).decode("ascii"),
            }
        )
    return payloads


def _load_minimax_multimodal_image_payloads(image_paths: list[str | Path]) -> list[dict]:
    """Load ordered MiniMax image attachments without exposing their bytes in logs."""
    payloads = []
    for index, raw_path in enumerate(image_paths, start=1):
        path = Path(raw_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Gambar referensi MiniMax tidak ditemukan: {path}")
        mime_type = mimetypes.guess_type(path.name)[0] or ""
        if not mime_type.startswith("image/"):
            raise ValueError(f"File referensi MiniMax bukan gambar: {path.name}")
        payloads.append(
            {
                "label": f"<Picture {index}>",
                "name": path.name,
                "path": str(path),
                "mime_type": mime_type,
                "base64": base64.b64encode(path.read_bytes()).decode("ascii"),
            }
        )
    return payloads


def _log_llm_audit(
    phase: str,
    provider: str,
    model: str,
    instruction: str,
    payload_text: str,
    image_payloads: list[dict] | None = None,
):
    """Write the exact textual request and ordered image manifest for auditing."""
    images = image_payloads or []
    image_lines = [
        f"{item.get('label', '(unlabeled)')} -> {item.get('path', item.get('name', '(unknown)'))}"
        for item in images
    ]
    LOGGER.info(
        "[LLM AUDIT] phase=%s provider=%s model=%s\n"
        "--- INSTRUCTION SENT ---\n%s\n"
        "--- TEXT PAYLOAD SENT ---\n%s\n"
        "--- EFFECTIVE TEXT REQUEST ---\n%s\n"
        "--- IMAGES SENT (ORDERED) ---\n%s",
        str(phase or "call"),
        str(provider or "unknown"),
        str(model or "unknown"),
        str(instruction or ""),
        str(payload_text or ""),
        f"{str(instruction or '').rstrip()}\n\n{str(payload_text or '').lstrip()}",
        "\n".join(image_lines) if image_lines else "(none)",
    )


class PromptTranslator:
    def __init__(
        self,
        prompt_generation_model_name: str = "",
    ):
        self._gemini = GeminiPromptTranslator(
            prompt_generation_model_name=prompt_generation_model_name,
        )
        configured_prompt_model = str(prompt_generation_model_name or "").strip()
        self.prompt_generation_model_name = configured_prompt_model or DEFAULT_PROMPT_GENERATION_MODEL
        self.last_call_metrics: dict | None = None

    def generate_qwen_image_edit_prompt_multimodal(
        self,
        prompt_text: str,
        image_paths: list[str | Path],
    ) -> dict:
        """Generate the Qwen Image Edit positive prompt from ordered images.

        This is intentionally a dedicated multimodal path. Existing prompt
        generation methods remain text-only and keep their current payloads.
        """
        prompt_text = _clean_text(prompt_text)
        if not prompt_text:
            raise ValueError("Instruksi prompt Qwen Image Edit tidak boleh kosong.")
        references = _load_qwen_multimodal_image_payloads(image_paths)
        if not references:
            raise ValueError("Minimal satu gambar referensi Qwen harus dipilih.")

        qwen_system_prompt = _load_qwen_image_edit_system_prompt()
        manifest = "\n".join(
            f"{item['label']} = {item['name']} (attached image {index + 1})"
            for index, item in enumerate(references)
        )
        output_contract = (
            "APPLICATION OUTPUT CONTRACT — this contract is authoritative for this integration.\n"
            "Apply all image-analysis, preservation, multi-image labeling, and editing rules from the Qwen system prompt above.\n"
            "Override only its original output field names and output-size metadata for this call.\n"
            "Do not return `rewritten_prompt`, `wh_ratio`, or `ratio_follow`.\n"
            "Return a valid JSON object with exactly one string key and no other keys:\n"
            "{\"prompt\":\"...\"}\n"
            "`prompt` must contain the complete rewritten editing instruction in natural English.\n"
            "Keep every valid `<imageN>` label exactly as assigned in the ordered image manifest.\n"
            "Output JSON only: no markdown fences, explanations, or text outside the JSON object."
        )
        user_payload = (
            "ORDERED IMAGE MANIFEST:\n"
            f"{manifest}\n\n"
            "USER INSTRUCTION FROM UI:\n"
            f"{prompt_text}"
        )
        model_instruction = f"{qwen_system_prompt}\n\n{output_contract}"
        image_parts = [
            {
                "inline_data": {
                    "mime_type": item["mime_type"],
                    "data": item["base64"],
                }
            }
            for item in references
        ]
        _log_llm_audit(
            "generate_qwen_image_edit_prompt_multimodal",
            "gemini",
            self.prompt_generation_model_name,
            model_instruction,
            user_payload,
            references,
        )
        response_text = self._gemini._call_text_model(
            self.prompt_generation_model_name,
            model_instruction,
            user_payload,
            timeout=LLM_CALL_TIMEOUT_SECONDS,
            phase="generate_qwen_image_edit_prompt_multimodal",
            image_parts=image_parts,
        )
        self.last_call_metrics = self._gemini.last_call_metrics

        english = _clean_text(_parse_qwen_image_edit_prompt_response(response_text))
        if not english:
            raise RuntimeError("LLM tidak mengembalikan prompt Qwen berbahasa Inggris yang valid.")
        allowed_labels = {item["label"] for item in references}
        used_labels = set(re.findall(r"<image\d+>", english, flags=re.IGNORECASE))
        invalid_labels = used_labels - allowed_labels
        if invalid_labels:
            raise RuntimeError(
                "LLM menggunakan label gambar yang tidak tersedia: "
                + ", ".join(sorted(invalid_labels))
            )
        return english


    def generate_prompt_to_english(self, text: str, context: str = "") -> str:
        text = _clean_text(text)
        if not text:
            return ""
        result = self._gemini.generate_prompt_to_english(text, context=context)
        self.last_call_metrics = self._gemini.last_call_metrics
        return result

    def generate_prompt_english(
        self,
        text: str,
        context: str = "",
        additional_instruction: str = "",
        image_paths: list[str | Path] | None = None,
    ) -> dict | str:
        text = _clean_text(text)
        additional_instruction = _clean_text(additional_instruction)
        if not text and not additional_instruction and not image_paths:
            return ""
        is_minimax = "MiniMax H3" in str(context or "")
        references = _load_minimax_multimodal_image_payloads(image_paths or []) if is_minimax and image_paths else []
        manifest = "\n".join(
            f"{item['label']} = {item['name']} (attached image {index + 1})"
            for index, item in enumerate(references)
        )
        is_r2v_ref2va = (
            "Active MiniMax H3 mode: Ref2VA" in str(context or "")
            and "Target: MiniMax H3 R2V" in str(context or "")
        )
        if is_r2v_ref2va:
            instruction = (
                "You are a senior MiniMax H3 R2V Ref2VA video prompt engineer.\n"
                "Generate only the canonical English authoring object as JSON.\n"
                "Use exactly these fields: mode, style_opening, subject_definitions, summary, "
                "retention_analysis, shots, overall_soundscape, and non_diegetic_music.\n"
                "Set mode to R2VA. Do not return detailed_description; the application compiles "
                "style_opening and shots into that runtime section.\n"
                "Each shot must use the shared shape with shot_id, numeric start/end, visual, action, "
                "camera, dialogue, and diegetic_sound.\n"
                "Use only the active reference tokens listed in the context; do not invent, rename, "
                "or renumber Picture, Video, or Audio labels. Preserve technical tokens exactly.\n"
                'Return JSON only in this shape: {"mode":"R2VA","style_opening":"...",'
                '"subject_definitions":"...","summary":"...","retention_analysis":"...",'
                '"shots":[{"shot_id":"Shot 1","start":0.0,"end":5.0,"visual":"...",'
                '"action":"...","camera":"...","dialogue":"...","diegetic_sound":"..."}],'
                '"overall_soundscape":"...","non_diegetic_music":"..."}'
            )
        elif "Active MiniMax H3 mode: Ref2VA" in str(context or ""):
            instruction = (
                "You are a senior MiniMax H3 Ref2VA video prompt engineer.\n"
                "Generate only the English workflow prompt as JSON. Do not return translation fields.\n"
                "The JSON must contain exactly the canonical English fields: "
                + ", ".join(REF2VA_SECTION_KEYS) + ".\n"
                "Use only the active reference tokens listed in the context; do not invent, rename, or renumber any Picture, Video, or Audio label. If a reference category is marked none, do not mention it. Non-reference semantic tokens such as <Subject N>, <Shot N>, <d>, </d>, and speaker IDs remain allowed. Preserve every technical token in angle brackets character-for-character.\n"
                'Return JSON only in this shape: {"subject_definitions":"...","summary":"...","retention_analysis":"...","detailed_description":"...","overall_soundscape":"...","non_diegetic_music":"..."}'
            )
        elif "MiniMax H3" in str(context or ""):
            active_mode = str(context or "")
            expected_mode = "I2VA" if "Active MiniMax H3 mode: I2VA" in active_mode else "T2VA"
            mode_instruction = (
                "The target is a MiniMax H3 audiovisual video prompt. Follow the MiniMax H3 base prompt guide.\n"
                "This is the creative generation phase. Return only the canonical English workflow object.\n"
                "The JSON schema is authoritative: use only the keys explicitly required below. The phrase integrated_multimodal_description describes the content of the shots timeline; it is not a JSON key. Never create an integrated_multimodal_description key.\n"
                "Every shot.shot_id must be a string exactly like Shot 1, Shot 2, and never a number.\n"
                "Every shot.start and shot.end must be JSON numbers. All other shot fields and both audio fields must be JSON strings.\n"
                "The response must be a JSON object with mode, shots, overall_soundscape, and non_diegetic_music.\n"
                "Each shot must contain shot_id, start, end, visual, action, camera, dialogue, and diegetic_sound.\n"
                "Use at least two shots when the scene has multiple actions. Do not return a text prompt instead of the object.\n"
            )
            if "Active MiniMax H3 mode: I2VA" in active_mode:
                output_shape = (
                    '{"mode":"I2VA","reference":{"picture":"Picture 1",'
                    '"source":"[Shot 1]","time":0.0,"instruction":"fully referenced"},'
                    '"shots":[{"shot_id":"Shot 1","start":0.0,"end":1.0,'
                    '"visual":"...","action":"...","camera":"...",'
                    '"dialogue":"...","diegetic_sound":"..."}],'
                    '"overall_soundscape":"...","non_diegetic_music":"..."}'
                )
                mode_instruction += (
                    "This is I2VA. The object must additionally contain reference with picture Picture 1, source [Shot 1], time 0.0, and instruction fully referenced.\n"
                    "The reference object is structural metadata; do not replace it with a text alignment field or an integrated_multimodal_description key.\n"
                )
            elif "Active MiniMax H3 mode: T2VA" in active_mode:
                output_shape = (
                    '{"mode":"T2VA","shots":[{"shot_id":"Shot 1",'
                    '"start":0.0,"end":1.0,"visual":"...","action":"...",'
                    '"camera":"...","dialogue":"...","diegetic_sound":"..."}],'
                    '"overall_soundscape":"...","non_diegetic_music":"..."}'
                )
                mode_instruction += "This is T2VA. Do not add reference, image-alignment instructions, or an integrated_multimodal_description key.\n"
            else:
                raise ValueError("MiniMax H3 prompt context must declare the active T2VA or I2VA mode.")
            instruction = (
                "You are a senior AI video prompt engineer.\n"
                + mode_instruction
                + "Return JSON only with exactly this shape: "
                + output_shape
            )
        else:
            instruction = (
                "You are a senior AI prompt engineer.\n"
                "Rewrite the prompt into a polished English prompt for image generation.\n"
                "Preserve subject, composition, style, lighting, atmosphere, and important details.\n"
                "Use the provided context to improve the prompt.\n"
                "Return only the English prompt as a plain string, without JSON keys, quotes, or explanation."
            )
        payload_text = _compose_prompt_request_text(
            text,
            context,
            additional_instruction=additional_instruction,
            image_manifest=manifest,
        )
        image_parts = [
            {
                "inline_data": {
                    "mime_type": item["mime_type"],
                    "data": item["base64"],
                }
            }
            for item in references
        ]
        _log_llm_audit(
            "generate_prompt_english",
            "gemini",
            self.prompt_generation_model_name,
            instruction,
            payload_text,
            references,
        )
        response_text = self._gemini._call_text_model(
            self.prompt_generation_model_name,
            instruction,
            payload_text,
            timeout=LLM_CALL_TIMEOUT_SECONDS,
            phase="generate_prompt_english",
            image_parts=image_parts,
        )
        self.last_call_metrics = self._gemini.last_call_metrics
        if is_r2v_ref2va:
            raw_payload = _parse_json_object_response(response_text)
            raw_value = raw_payload.get("positive_prompt", raw_payload) if isinstance(raw_payload, dict) else {}
            raw_value = normalize_ref2va_authoring_prompt(raw_value)
            if isinstance(raw_value, dict):
                raw_value["mode"] = "R2VA"
            errors = validate_ref2va_prompt(raw_value)
            if errors:
                raise RuntimeError("Response MiniMax H3 R2V Ref2VA tidak valid: " + "; ".join(errors[:3]))
            return raw_value
        if "Active MiniMax H3 mode: Ref2VA" in str(context or ""):
            raw_payload = _parse_json_object_response(response_text)
            raw_value = raw_payload.get("positive_prompt", raw_payload) if isinstance(raw_payload, dict) else {}
            errors = validate_ref2va_prompt(raw_value)
            if errors:
                raise RuntimeError("Response MiniMax H3 Ref2VA tidak valid: " + "; ".join(errors[:3]))
            return unwrap_prompt_value(raw_value)
        if "MiniMax H3" in str(context or ""):
            raw_payload = _parse_json_object_response(response_text)
            raw_en = raw_payload.get("positive_prompt", raw_payload) if isinstance(raw_payload, dict) else None
            raw_en = unwrap_prompt_value(raw_en)
            if not isinstance(raw_en, dict):
                raise RuntimeError("Response MiniMax H3 harus berupa object JSON.")
            expected_mode = "I2VA" if "Active MiniMax H3 mode: I2VA" in str(context or "") else "T2VA"
            if expected_mode == "I2VA":
                # The reference object is a structural control field, not
                # creative text. Some LLM responses omit it despite the
                # schema instruction, so restore the exact skill contract
                # deterministically before validation.
                raw_en = copy.deepcopy(raw_en)
                raw_en["mode"] = "I2VA"
                raw_en["reference"] = {
                    "picture": "Picture 1",
                    "source": "[Shot 1]",
                    "time": 0.0,
                    "instruction": "fully referenced",
                }
            _, errors = parse_structured_response(raw_en, expected_mode=expected_mode)
            if errors:
                raise RuntimeError("Response MiniMax tidak valid: " + "; ".join(errors[:3]))
            return raw_en
        raw_text = _strip_markdown_code_fences(response_text)
        if raw_text.startswith("{"):
            parsed = _parse_json_object_response(raw_text)
            raw_text = parsed.get("prompt") or parsed.get("english") or ""
        raw_text = _clean_text(raw_text)
        if not raw_text:
            raise RuntimeError("LLM tidak mengembalikan prompt Inggris yang valid.")
        return raw_text

    # Compatibility alias for callers from the previous UI. This method now
    # performs prompt generation only; it never translates.
    generate_prompt_multilang = generate_prompt_english



def _clean_text(value) -> str:
    return str(value or "").strip()


def _strip_markdown_code_fences(text: str) -> str:
    text = str(text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text




def _parse_json_object_response(text: str) -> dict:
    raw = _strip_markdown_code_fences(text)
    try:
        payload = json.loads(raw)
    except Exception:
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            return {}
        try:
            payload = json.loads(raw[start:end + 1])
        except Exception:
            return {}
    return payload if isinstance(payload, dict) else {}


def _parse_qwen_image_edit_prompt_response(text: str) -> str:
    payload = _parse_json_object_response(text)
    if not payload:
        return ""
    return _clean_text(
        payload.get("prompt")
        or payload.get("en")
        or payload.get("rewritten_prompt")
        or payload.get("english")
    )


def _extract_json_text_candidate(text: str) -> str:
    raw = _strip_markdown_code_fences(text)
    if not raw:
        return ""
    try:
        json.loads(raw)
        return raw
    except Exception:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        candidate = raw[start:end + 1].strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass
    return ""


def _compose_prompt_request_text(
    prompt_text: str,
    context: str = "",
    additional_instruction: str = "",
    image_manifest: str = "",
) -> str:
    prompt_text = _clean_text(prompt_text)
    context = _clean_text(context)
    additional_instruction = _clean_text(additional_instruction)
    image_manifest = _clean_text(image_manifest)
    if not additional_instruction and not image_manifest:
        if context:
            return f"Context:\n{context}\n\nPrompt:\n{prompt_text}" if prompt_text else f"Context:\n{context}"
        return prompt_text
    sections = []
    if context:
        sections.append(f"Context:\n{context}")
    if image_manifest:
        sections.append(f"ORDERED PICTURE MANIFEST:\n{image_manifest}")
    if prompt_text:
        sections.append(f"Prompt:\n{prompt_text}")
    if additional_instruction:
        sections.append(f"ADDITIONAL INSTRUCTION FROM UI:\n{additional_instruction}")
    return "\n\n".join(sections)


def _maybe_parse_prompt_object_string(value):
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return value
    if not (text.startswith("{") and text.endswith("}")):
        return value
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return value


def _extract_text_from_gemini_response(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    for cand in candidates:
        content = cand.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            text = part.get("text")
            if text:
                return str(text)
    return ""


def get_prompt_translator(project_dir: str | Path | None = None):
    config = load_server_config()
    prompt_generation_config = config.get("prompt_generation") if isinstance(config, dict) else {}
    prompt_generation_config = prompt_generation_config if isinstance(prompt_generation_config, dict) else {}
    prompt_generation_model = str(
        prompt_generation_config.get("model", DEFAULT_PROMPT_GENERATION_MODEL)
    ).strip() or DEFAULT_PROMPT_GENERATION_MODEL
    if project_dir:
        try:
            from scripts.project_settings import load_project_settings
            project_config = load_project_settings(Path(project_dir))
            project_prompt = project_config.get("prompt_generation", {}) if isinstance(project_config, dict) else {}
            if isinstance(project_prompt, dict):
                project_model = str(project_prompt.get("model", "")).strip()
                if project_model and not project_model.startswith(("qwen", "llama", "ollama")):
                    prompt_generation_model = project_model
        except Exception:
            pass
    return PromptTranslator(
        prompt_generation_model_name=prompt_generation_model,
    )


def update_generated_prompt_entry(
    filename: str,
    data: dict,
    key: str,
    fallback_value: str,
    generated_value: str,
    group_index: int | None = None,
) -> dict:
    """Store one generated English prompt directly at its prompt slot."""
    result = copy.deepcopy(data or {})
    key = str(key or "").strip()
    value = generated_value if generated_value not in (None, "") else fallback_value
    value = unwrap_prompt_value(value)

    if group_index is None:
        result[key] = copy.deepcopy(value)
        return result

    groups = result.get("groups")
    if not isinstance(groups, list):
        groups = []
    while len(groups) <= group_index:
        groups.append({})
    item = dict(groups[group_index]) if isinstance(groups[group_index], dict) else {}
    item[key] = copy.deepcopy(value)
    groups[group_index] = item
    result["groups"] = groups
    return result


def _canonical_prompt_entry(value):
    """Convert a legacy prompt wrapper to the direct English value."""
    value = _maybe_parse_prompt_object_string(value)
    return unwrap_prompt_value(value)


def _top_level_fields_for(filename: str) -> list[str]:
    filename = str(filename or "")
    return list(dict.fromkeys(
        PROMPT_TOP_LEVEL_FIELDS.get(filename, [])
        + ADDITIONAL_TOP_LEVEL_PROMPT_FIELDS.get(filename, [])
    ))


def _group_fields_for(filename: str) -> list[str]:
    return GROUP_PROMPT_FIELDS.get(str(filename or ""), [])


def normalize_lora_trigger_words(value) -> str:
    return str(value or "").strip()


def prepend_lora_trigger_words(prompt_text: str, trigger_words: str) -> str:
    prompt_text = str(prompt_text or "").strip()
    trigger_words = normalize_lora_trigger_words(trigger_words)
    if not trigger_words:
        return prompt_text
    if not prompt_text:
        return trigger_words
    if prompt_text.casefold().startswith(trigger_words.casefold()):
        return prompt_text
    return f"{trigger_words} {prompt_text}"


def apply_lora_trigger_words_to_prompt_payload(
    filename: str,
    data: dict,
    trigger_words: str | None = None,
) -> dict:
    result = copy.deepcopy(data or {})
    fields = TRIGGER_WORD_PROMPT_FIELDS.get(str(filename or ""), [])
    if not fields:
        return result

    effective_trigger_words = normalize_lora_trigger_words(
        result.get(LORA_TRIGGER_WORDS_FIELD, "") if trigger_words is None else trigger_words
    )
    if not effective_trigger_words:
        return result

    groups = result.get("groups")
    if isinstance(groups, list):
        updated_groups = []
        for item in groups:
            group_item = dict(item) if isinstance(item, dict) else {}
            for key in fields:
                if key in group_item:
                    group_item[key] = prepend_lora_trigger_words(group_item.get(key, ""), effective_trigger_words)
            updated_groups.append(group_item)
        result["groups"] = updated_groups
        return result

    for key in fields:
        if key in result:
            result[key] = prepend_lora_trigger_words(result.get(key, ""), effective_trigger_words)
    return result


def _get_group_item(groups_value, index: int):
    if isinstance(groups_value, list) and 0 <= index < len(groups_value) and isinstance(groups_value[index], dict):
        return groups_value[index]
    return {}


def convert_prompt_payload_for_ui(filename: str, data: dict) -> dict:
    return _canonicalize_prompt_slots(filename, data)


def prepare_prompt_payload_for_save(filename: str, data: dict, existing_data: dict | None = None) -> dict:
    return _canonicalize_prompt_slots(filename, data)


def _canonicalize_prompt_slots(filename: str, data: dict) -> dict:
    """Canonicalize all prompt-bearing slots without changing metadata."""
    result = copy.deepcopy(data or {})
    filename = str(filename or "")
    if filename in {
        MINIMAX_H3_I2V_PANJANG_PROMPT_FILENAME,
        MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME,
    }:
        prompts = result.get("prompts")
        if isinstance(prompts, list):
            normalized = []
            for item in prompts:
                value = _canonical_prompt_entry(item)
                if filename == MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME:
                    value = normalize_ref2va_authoring_prompt(value)
                    if isinstance(value, dict):
                        value["mode"] = "R2VA"
                normalized.append(value)
            result["prompts"] = normalized
        return result
    if filename in {"minimax_h3_t2v_prompt.json", "minimax_h3_i2v_prompt.json"}:
        mode = "I2VA" if filename.endswith("i2v_prompt.json") else "T2VA"
        return normalize_minimax_prompt_payload(result, mode)
    if filename in {"minimax_h3_s2v_prompt.json", "minimax_h3_r2v_prompt.json"}:
        if "positive_prompt" in result:
            value = _canonical_prompt_entry(result.get("positive_prompt"))
            if filename == "minimax_h3_r2v_prompt.json":
                value = normalize_ref2va_authoring_prompt(value)
                if isinstance(value, dict):
                    value["mode"] = "R2VA"
            result["positive_prompt"] = value
        return result
    for key in _top_level_fields_for(filename):
        if key in result:
            result[key] = _canonical_prompt_entry(result.get(key))
    groups = result.get("groups")
    group_fields = _group_fields_for(filename)
    if isinstance(groups, list) and group_fields:
        for item in groups:
            if not isinstance(item, dict):
                continue
            for key in group_fields:
                if key in item:
                    item[key] = _canonical_prompt_entry(item.get(key))
    if filename == "project_settings.json" and isinstance(result.get("cover"), dict):
        result["cover"] = _canonicalize_prompt_slots("project_settings_cover.json", result["cover"])
    return result



def resolve_prompt_payload_for_runtime(
    filename: str,
    data: dict,
    log_fn: Callable[[str], None] | None = None,
    preserve_structured: bool = False,
) -> tuple[dict, dict, bool]:
    """Resolve prompt payloads without translation or bilingual wrappers."""
    source = copy.deepcopy(data or {})
    stored = _canonicalize_prompt_slots(filename, source)
    resolved = copy.deepcopy(stored)
    changed = stored != source

    if filename == MINIMAX_H3_I2V_PANJANG_PROMPT_FILENAME:
        prompts = stored.get("prompts")
        if not isinstance(prompts, list) or len(prompts) != 4:
            raise ValueError("Prompt MiniMax H3 I2V panjang harus memiliki tepat 4 prompt.")
        try:
            active_count = max(1, min(4, int(stored.get("continuations", 0)) + 1))
            run_start_stage = int(stored.get("run_start_stage", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError("Konfigurasi tahap MiniMax H3 I2V panjang tidak valid.") from exc
        if not 1 <= run_start_stage <= active_count:
            raise ValueError("run_start_stage MiniMax H3 I2V panjang berada di luar tahap aktif.")
        for index, entry in enumerate(prompts, start=1):
            if run_start_stage <= index <= active_count:
                errors = validate_structured_prompt(entry, expected_mode="I2VA")
                if errors:
                    raise ValueError(
                        f"Prompt MiniMax H3 I2V panjang ke-{index} tidak valid: "
                        + "; ".join(errors[:3])
                    )
        return resolved, stored, changed

    if filename == MINIMAX_H3_R2V_PANJANG_PROMPT_FILENAME:
        prompts = stored.get("prompts")
        if not isinstance(prompts, list) or len(prompts) != 4:
            raise ValueError("Prompt MiniMax H3 R2V panjang harus memiliki tepat 4 prompt.")
        try:
            active_count = max(1, min(4, int(stored.get("continuations", 0)) + 1))
            run_start_stage = int(stored.get("run_start_stage", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError("Konfigurasi tahap MiniMax H3 R2V panjang tidak valid.") from exc
        if not 1 <= run_start_stage <= active_count:
            raise ValueError("run_start_stage MiniMax H3 R2V panjang berada di luar tahap aktif.")
        for index, entry in enumerate(prompts, start=1):
            if run_start_stage <= index <= active_count:
                errors = validate_ref2va_prompt(entry)
                if errors:
                    raise ValueError(
                        f"Prompt MiniMax H3 R2V panjang ke-{index} tidak valid: "
                        + "; ".join(errors[:3])
                    )
        return resolved, stored, changed

    if filename in {"minimax_h3_t2v_prompt.json", "minimax_h3_i2v_prompt.json"}:
        mode = "I2VA" if filename.endswith("i2v_prompt.json") else "T2VA"
        errors = validate_structured_prompt(stored.get("positive_prompt"), expected_mode=mode)
        if errors:
            raise ValueError("Prompt MiniMax H3 structured tidak valid: " + "; ".join(errors[:3]))
        resolved["positive_prompt"] = serialize_structured_prompt(stored["positive_prompt"])
        return resolved, stored, changed

    if filename in {"minimax_h3_s2v_prompt.json", "minimax_h3_r2v_prompt.json"}:
        errors = validate_ref2va_prompt(stored.get("positive_prompt"))
        if errors:
            raise ValueError("Prompt MiniMax H3 Ref2VA tidak valid: " + "; ".join(errors[:3]))
        resolved["positive_prompt"] = serialize_ref2va_prompt(stored["positive_prompt"])
        return resolved, stored, changed

    for key in _top_level_fields_for(filename):
        if key in stored:
            resolved[key] = prompt_entry_to_display(stored.get(key))

    groups = stored.get("groups")
    group_fields = _group_fields_for(filename)
    if isinstance(groups, list) and group_fields:
        resolved_groups = []
        for item in groups:
            out_item = dict(item) if isinstance(item, dict) else {}
            for key in group_fields:
                if key in out_item:
                    out_item[key] = prompt_entry_to_display(out_item.get(key))
            resolved_groups.append(out_item)
        resolved["groups"] = resolved_groups

    if filename == "project_settings.json" and isinstance(stored.get("cover"), dict):
        cover_resolved, cover_stored, cover_changed = resolve_prompt_payload_for_runtime(
            "project_settings_cover.json",
            stored["cover"],
            log_fn=log_fn,
        )
        stored["cover"] = cover_stored
        resolved["cover"] = cover_resolved
        changed = changed or cover_changed

    resolved = apply_lora_trigger_words_to_prompt_payload(filename, resolved)
    return resolved, stored, changed


def _read_json_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_file(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json_for_runtime(
    path: str,
    required: bool = False,
    persist_updates: bool = True,
    log_fn: Callable[[str], None] | None = None,
    preserve_structured: bool = False,
) -> dict:
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(path)
        return {}

    source = _read_json_file(path)
    filename = os.path.basename(path)
    resolved, stored, changed = resolve_prompt_payload_for_runtime(
        filename,
        source,
        log_fn=log_fn,
        preserve_structured=preserve_structured,
    )
    if changed and persist_updates:
        _write_json_file(path, stored)
        if log_fn:
            log_fn(f"Prompt schema diperbarui: {path}")
    return resolved
