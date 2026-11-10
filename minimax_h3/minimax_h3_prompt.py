"""Structured prompt schema and serializer for MiniMax H3 T2VA/I2VA."""

from __future__ import annotations

import json
import copy
import ast
import re
from numbers import Real


I2VA_FIRST_FRAME_PREFIX = (
    "For the target video, at 0.00 seconds into the target video, "
    "<Picture 1> (from [Shot 1]) is fully referenced."
)
I2VA_FIRST_FRAME_DETAIL_INSTRUCTION = (
    "The selected <Picture 1> reference image is the exact visual state at "
    "0.00 seconds and must be preserved as the first frame. Begin the motion "
    "from this image without changing the subject identity, composition, "
    "clothing, important objects, or spatial layout."
)
I2VA_FIRST_SHOT_VISUAL_EN = "At 0.00 seconds, <Picture 1> is the first frame of the video"
REQUIRED_SHOT_KEYS = (
    "shot_id",
    "start",
    "end",
    "visual",
    "action",
    "camera",
    "dialogue",
    "diegetic_sound",
)
REQUIRED_AUDIO_KEYS = ("overall_soundscape", "non_diegetic_music")
REF2VA_SECTION_KEYS = (
    "subject_definitions",
    "summary",
    "retention_analysis",
    "detailed_description",
    "overall_soundscape",
    "non_diegetic_music",
)

LEGACY_PROMPT_WRAPPER_KEYS = ("id_new", "id_old", "en")


def unwrap_prompt_value(value):
    """Return the canonical prompt value from old or new storage formats.

    Older scene files wrapped every prompt in ``id_old``/``id_new``/``en``.
    The canonical format stores the English value directly.  Keeping this
    adapter at the schema boundary lets old projects load safely while every
    new save and runtime path uses the direct value.
    """
    current = copy.deepcopy(value)
    for _ in range(4):
        if not isinstance(current, dict) or not any(
            key in current for key in LEGACY_PROMPT_WRAPPER_KEYS
        ):
            return current
        selected = None
        for key in ("en", "id_new", "id_old"):
            candidate = current.get(key)
            if isinstance(candidate, (dict, list)):
                selected = candidate
                break
            if isinstance(candidate, str) and candidate.strip():
                selected = candidate
                break
        if selected is None:
            return ""
        current = copy.deepcopy(selected)
    return current

_REF2VA_SHOT_MARKER_PATTERN = re.compile(r"(?im)(?<!\w)\[Shot\s+(\d+)\]")
_REF2VA_SHOT_AT_PATTERN = re.compile(
    r"^\s*At\s+(\d{1,3}):(\d{2})(?:\.(\d{1,3}))?\s*,?\s*",
    re.IGNORECASE,
)
_REF2VA_SHOT_RANGE_PATTERN = re.compile(
    r"^\s*From\s+(\d+(?:\.\d+)?)\s+to\s+"
    r"(\d+(?:\.\d+)?)\s+seconds?\s*,?\s*",
    re.IGNORECASE,
)
_REF2VA_SHOT_ID_RANGE_PATTERN = re.compile(
    r"^\s*Dari\s+(\d+(?:[.,]\d+)?)\s+hingga\s+"
    r"(\d+(?:[.,]\d+)?)\s+detik\s*,?\s*",
    re.IGNORECASE,
)

_REF2VA_REFERENCE_PATTERN = re.compile(r"<(Picture|Video|Audio)\s+(\d+)>")
_I2VA_LAST_FRAME_SENTENCE_PATTERN = re.compile(
    r"(?:At\s+\d+(?:\.\d+)?\s+seconds,\s*<Picture\s+2>\s+is\s+the\s+last\s+frame\s+of\s+the\s+video|"
    r"Pada\s+\d+(?:[.,]\d+)?\s+detik,\s*<Picture\s+2>\s+adalah\s+frame\s+terakhir\s+video)\.?",
    re.IGNORECASE,
)


def synchronize_i2va_frame_instructions(entry: dict) -> dict:
    """Normalize an I2VA value after generated frame metadata changes."""
    return unwrap_prompt_value(entry) if isinstance(entry, dict) else {}


def empty_ref2va_prompt() -> dict:
    return {key: "" for key in REF2VA_SECTION_KEYS}


def validate_ref2va_prompt(value) -> list[str]:
    value = unwrap_prompt_value(value)
    if not isinstance(value, dict):
        return ["Ref2VA prompt harus berupa object JSON."]
    errors = []
    required_keys = tuple(key for key in REF2VA_SECTION_KEYS if key != "detailed_description")
    for key in required_keys:
        if not isinstance(value.get(key), str) or not value.get(key, "").strip():
            errors.append(f"Ref2VA.{key} harus berupa string tidak kosong.")
    shots = value.get("shots")
    if shots is not None:
        if not isinstance(shots, list) or not shots:
            errors.append("Ref2VA.shots harus berupa array berisi minimal satu shot.")
        else:
            previous_end = 0.0
            for index, shot in enumerate(shots):
                prefix = f"Ref2VA.shots[{index}]"
                if not isinstance(shot, dict):
                    errors.append(f"{prefix} harus berupa object.")
                    continue
                for key in REQUIRED_SHOT_KEYS:
                    if key not in shot:
                        errors.append(f"{prefix}.{key} wajib ada.")
                start, end = shot.get("start"), shot.get("end")
                if not isinstance(start, Real) or isinstance(start, bool) or not isinstance(end, Real) or isinstance(end, bool):
                    errors.append(f"{prefix}.start dan end harus berupa angka.")
                elif float(start) < previous_end or float(end) <= float(start):
                    errors.append(f"{prefix} memiliki timeline tidak valid atau tidak berurutan.")
                else:
                    previous_end = float(end)
                for key in REQUIRED_SHOT_KEYS:
                    if key not in {"start", "end"} and not isinstance(shot.get(key), str):
                        errors.append(f"{prefix}.{key} harus berupa string.")
                    elif key not in {"start", "end"} and not str(shot.get(key, "")).strip():
                        errors.append(f"{prefix}.{key} tidak boleh kosong.")
    elif not isinstance(value.get("detailed_description"), str) or not value.get("detailed_description", "").strip():
        errors.append("Ref2VA.detailed_description atau Ref2VA.shots wajib diisi.")
    return errors


def _ref2va_clock_to_seconds(minutes: str, seconds: str, milliseconds: str | None) -> float:
    fraction = (milliseconds or "").ljust(3, "0")[:3]
    return float(int(minutes) * 60 + int(seconds)) + (int(fraction) / 1000 if fraction else 0.0)


def _ref2va_format_cut_time(value) -> str:
    try:
        total = max(0.0, float(value))
    except (TypeError, ValueError):
        total = 0.0
    minutes = int(total // 60)
    seconds = total - (minutes * 60)
    return f"{minutes:02d}:{seconds:06.3f}"


def _ref2va_format_range_time(value) -> str:
    try:
        total = max(0.0, float(value))
    except (TypeError, ValueError):
        total = 0.0
    return f"{total:.2f}"


def _empty_ref2va_shot(start: float, end: float, text: str = "") -> dict:
    return {
        "shot_id": "Shot 1",
        "start": float(start),
        "end": float(end),
        "visual": str(text or "").strip(),
        "action": "",
        "camera": "",
        "dialogue": "",
        "diegetic_sound": "",
    }


def _match_ref2va_shot_range(text: str):
    match = _REF2VA_SHOT_RANGE_PATTERN.match(text)
    if match:
        return float(match.group(1)), float(match.group(2)), match
    match = _REF2VA_SHOT_ID_RANGE_PATTERN.match(text)
    if match:
        return (
            float(match.group(1).replace(",", ".")),
            float(match.group(2).replace(",", ".")),
            match,
        )
    return None


def parse_ref2va_detailed_description(text: str, duration: float = 5.0) -> dict:
    """Parse Ref2VA timeline markers into the editor's shared shot model.

    Ref2VA persists ``detailed_description`` as one string. This parser is an
    authoring adapter only: it accepts the canonical ``From X to Y seconds``
    markers and the older ``At MM:SS.mmm`` examples, while keeping all
    prose inside the visual field so an existing scene is not rewritten.
    """
    source = str(text or "").replace("\r\n", "\n").strip()
    try:
        fallback_duration = max(0.0, float(duration or 0.0)) or 5.0
    except (TypeError, ValueError):
        fallback_duration = 5.0
    markers = list(_REF2VA_SHOT_MARKER_PATTERN.finditer(source))
    if not markers:
        leading_range = re.search(
            r"(?i)(?:From\s+\d+(?:\.\d+)?\s+to\s+\d+(?:\.\d+)?\s+seconds?|"
            r"Dari\s+\d+(?:[.,]\d+)?\s+hingga\s+\d+(?:[.,]\d+)?\s+detik)",
            source,
        )
        if leading_range:
            prefix = source[:leading_range.start()].strip()
            range_value = _match_ref2va_shot_range(source[leading_range.start():])
            if range_value:
                start, end, range_match = range_value
                body = source[leading_range.start() + range_match.end():].strip()
                return {
                    "style_opening": prefix,
                    "shots": [_empty_ref2va_shot(start, end, body)],
                    "has_markers": False,
                }
        return {
            "style_opening": "",
            "shots": [_empty_ref2va_shot(0.0, fallback_duration, source)],
            "has_markers": False,
        }

    style_opening = source[:markers[0].start()].strip()
    parsed = []
    for index, marker in enumerate(markers):
        next_start = markers[index + 1].start() if index + 1 < len(markers) else len(source)
        body = source[marker.end():next_start].strip()
        start = 0.0 if index == 0 else None
        end = None

        range_value = _match_ref2va_shot_range(body)
        if range_value:
            start, end, range_match = range_value
            body = body[range_match.end():].strip()
        else:
            at_match = _REF2VA_SHOT_AT_PATTERN.match(body)
            if at_match:
                start = _ref2va_clock_to_seconds(
                    at_match.group(1), at_match.group(2), at_match.group(3)
                )
                body = body[at_match.end():].strip()

        parsed.append({
            "start": start,
            "end": end,
            "text": body,
        })

    previous_end = 0.0
    shots = []
    for index, item in enumerate(parsed):
        start = item["start"]
        if start is None:
            start = previous_end if index else 0.0
        end = item["end"]
        if end is None:
            next_start = parsed[index + 1]["start"] if index + 1 < len(parsed) else None
            end = next_start if next_start is not None else fallback_duration
        if end < start:
            end = start
        shot = _empty_ref2va_shot(start, end, item["text"])
        shot["shot_id"] = f"Shot {index + 1}"
        shots.append(shot)
        previous_end = end

    return {
        "style_opening": style_opening,
        "shots": shots or [_empty_ref2va_shot(0.0, fallback_duration)],
        "has_markers": True,
    }


def normalize_ref2va_authoring_prompt(value, duration: float = 5.0):
    """Return the canonical Ref2VA authoring shape with shared ``shots[]``.

    Ref2VA runtime still consumes ``detailed_description``, but R2V scene
    files and the interactive editor use ``style_opening`` plus the shared
    shot cards. This adapter also accepts a legacy/generated six-section
    object so an older LLM response cannot be persisted in the old shape.
    """
    result = unwrap_prompt_value(value)
    if not isinstance(result, dict):
        return result
    result = copy.deepcopy(result)
    if not isinstance(result.get("shots"), list):
        parsed = parse_ref2va_detailed_description(
            result.get("detailed_description", ""),
            duration=duration,
        )
        result["style_opening"] = parsed.get("style_opening", "")
        result["shots"] = parsed.get("shots", [])
    else:
        result["style_opening"] = str(result.get("style_opening", "") or "").strip()
    result.pop("detailed_description", None)
    for shot in result.get("shots", []):
        if not isinstance(shot, dict):
            continue
        try:
            start = float(shot.get("start", 0.0))
            end = float(shot.get("end", start))
        except (TypeError, ValueError):
            start, end = 0.0, 0.001
        if end <= start:
            shot["end"] = start + 0.001
    return result


def serialize_ref2va_detailed_description(
    style_opening: str,
    shots: list[dict] | None,
) -> str:
    """Compile shared shot cards into the Ref2VA string contract."""
    parts = []
    opening = str(style_opening or "").strip()
    if opening:
        parts.append(opening)
    for index, shot in enumerate(shots or [], start=1):
        if not isinstance(shot, dict):
            continue
        fields = (
            shot.get("visual"),
            shot.get("action"),
            shot.get("camera"),
            shot.get("dialogue"),
            shot.get("diegetic_sound"),
        )
        body = " ".join(str(value or "").strip() for value in fields if str(value or "").strip())
        if not body:
            continue
        marker = (
            f"[Shot {index}] From {_ref2va_format_range_time(shot.get('start', 0.0))} "
            f"to {_ref2va_format_range_time(shot.get('end', 0.0))} seconds,"
        )
        parts.append(f"{marker} {body}".strip())
    return "\n\n".join(parts).strip()


def validate_ref2va_shot_timeline(text: str, duration: float | None = None) -> list[str]:
    """Validate the canonical shot markers emitted by the Ref2VA editor."""
    source = str(text or "").replace("\r\n", "\n").strip()
    markers = list(_REF2VA_SHOT_MARKER_PATTERN.finditer(source))
    if not markers:
        return ["Ref2VA.detailed_description harus memiliki marker [Shot 1]."]

    errors = []
    previous_start = -1.0
    previous_end = None
    for index, marker in enumerate(markers):
        number = int(marker.group(1))
        if number != index + 1:
            errors.append(
                f"Marker Ref2VA harus berurutan; ditemukan [Shot {number}] pada posisi {index + 1}."
            )
        next_start = markers[index + 1].start() if index + 1 < len(markers) else len(source)
        body = source[marker.end():next_start].strip()
        start = 0.0 if index == 0 else None
        end = None
        range_match = _REF2VA_SHOT_RANGE_PATTERN.match(body)
        at_match = _REF2VA_SHOT_AT_PATTERN.match(body)
        if range_match:
            start = float(range_match.group(1))
            end = float(range_match.group(2))
            body = body[range_match.end():].strip()
        elif index > 0:
            if not at_match:
                errors.append(
                    f"[Shot {index + 1}] harus memiliki rentang waktu From X to Y seconds "
                    "atau format waktu lama At MM:SS.mmm."
                )
            else:
                start = _ref2va_clock_to_seconds(
                    at_match.group(1), at_match.group(2), at_match.group(3)
                )
                body = body[at_match.end():].strip()
        elif at_match:
            errors.append("[Shot 1] harus menggunakan rentang waktu From X to Y seconds atau tanpa prefix waktu lama.")
            body = body[at_match.end():].strip()
        if start is not None:
            if index > 0 and start <= previous_start:
                errors.append(f"Waktu [Shot {index + 1}] harus lebih besar dari shot sebelumnya.")
            if previous_end is not None and start < previous_end:
                errors.append(f"Rentang waktu [Shot {index + 1}] bertumpang tindih dengan shot sebelumnya.")
            if duration is not None and start > max(0.0, float(duration)):
                errors.append(f"Waktu [Shot {index + 1}] berada di luar durasi video.")
            previous_start = start
        if end is not None:
            if start is None or end <= start:
                errors.append(f"Rentang waktu [Shot {index + 1}] tidak valid.")
            if duration is not None and end > max(0.0, float(duration)):
                errors.append(f"Akhir waktu [Shot {index + 1}] berada di luar durasi video.")
            previous_end = end
        if not body:
            errors.append(f"[Shot {index + 1}] harus memiliki deskripsi.")
    return errors


def validate_ref2va_reference_tokens(
    value: dict,
    *,
    image_count: int = 0,
    audio_count: int = 0,
    has_video: bool = False,
) -> list[str]:
    """Ensure Ref2VA references mentioned in text exist in the active scene."""
    errors = []
    value = unwrap_prompt_value(value)
    if not isinstance(value, dict):
        return ["Ref2VA prompt harus berupa object JSON."]
    allowed = {f"Picture {index}" for index in range(1, max(0, int(image_count)) + 1)}
    allowed.update(f"Audio {index}" for index in range(1, max(0, int(audio_count)) + 1))
    if has_video:
        allowed.add("Video 1")
        # Audio 4 is the semantic label commonly used for synchronized audio
        # carried by Video 1; it is not a fourth uploaded audio slot.
        allowed.add("Audio 4")
    found = set()
    section_values = {section: value.get(section, "") for section in REF2VA_SECTION_KEYS}
    if isinstance(value.get("shots"), list):
        section_values["detailed_description"] = serialize_ref2va_detailed_description(
            value.get("style_opening", ""), value.get("shots", [])
        )
    for text in section_values.values():
        if not isinstance(text, str):
            continue
        for kind, number in _REF2VA_REFERENCE_PATTERN.findall(text):
            token = f"{kind} {number}"
            found.add(token)
            if token not in allowed:
                errors.append(f"Token <{token}> tidak tersedia pada reference aktif.")
    return list(dict.fromkeys(errors))


def serialize_ref2va_prompt(value) -> str:
    value = unwrap_prompt_value(value)
    if not isinstance(value, dict):
        return str(value or "").strip()
    sections = dict(value)
    if isinstance(value.get("shots"), list):
        sections["detailed_description"] = serialize_ref2va_detailed_description(
            value.get("style_opening", ""), value.get("shots", [])
        )
    return "\n\n".join(f"{key}:\n{sections.get(key, '')}" for key in REF2VA_SECTION_KEYS).strip()


def empty_structured_prompt(mode: str) -> dict:
    mode = "I2VA" if str(mode).upper() == "I2VA" else "T2VA"
    value = {
        "mode": mode,
        "shots": [],
        "overall_soundscape": "",
        "non_diegetic_music": "",
    }
    if mode == "I2VA":
        value["reference"] = {
            "picture": "Picture 1",
            "source": "[Shot 1]",
            "time": 0.0,
            "instruction": "fully referenced",
        }
    return value


def default_structured_prompt(mode: str, language: str = "en") -> dict:
    """Return a non-empty, saveable English MiniMax H3 prompt."""
    value = empty_structured_prompt(mode)
    visual = "A clear cinematic scene with a primary subject and coherent composition."
    action = "The primary subject moves naturally within the scene."
    camera = "The camera uses a stable medium shot with smooth movement."
    dialogue = "No dialogue."
    diegetic_sound = "Natural environmental sound follows the visible action."
    overall_soundscape = "A coherent cinematic soundscape follows the environment and visible action."
    value["shots"] = [{
        "shot_id": "Shot 1",
        "start": 0.0,
        "end": 5.0,
        "visual": (
            f"{I2VA_FIRST_FRAME_DETAIL_INSTRUCTION} {visual}"
            if str(mode).upper() == "I2VA"
            else visual
        ),
        "action": action,
        "camera": camera,
        "dialogue": dialogue,
        "diegetic_sound": diegetic_sound,
    }]
    value["overall_soundscape"] = overall_soundscape
    value["non_diegetic_music"] = "N/A"
    return value


def structured_prompt_entry(mode: str, value: dict | None = None) -> dict:
    """Build the canonical direct English value."""
    mode = "I2VA" if str(mode).upper() == "I2VA" else "T2VA"
    if isinstance(value, dict):
        return copy.deepcopy(value)
    return empty_structured_prompt(mode)


def enforce_i2va_first_shot_visual(entry: dict) -> dict:
    """Ensure the English first-frame wording without discarding Shot 1."""
    result = unwrap_prompt_value(entry)
    if not isinstance(result, dict):
        return result
    shots = result.get("shots") if isinstance(result, dict) else None
    if isinstance(shots, list):
        for shot in shots:
            if isinstance(shot, dict) and shot.get("shot_id") == "Shot 1":
                visual = str(shot.get("visual", "")).strip()
                if I2VA_FIRST_SHOT_VISUAL_EN.lower() not in visual.lower():
                    shot["visual"] = f"{I2VA_FIRST_SHOT_VISUAL_EN}. {visual}".strip()
                break
    return result


def ensure_i2va_frame_instructions(entry: dict, end_time: float, include_last_frame: bool = False) -> dict:
    """Repair the mandatory English first/last-frame sentences."""
    result = unwrap_prompt_value(entry)
    if not isinstance(result, dict):
        return {}
    shots = result.get("shots")
    if not isinstance(shots, list):
        return result
    for shot in shots:
        if isinstance(shot, dict):
            visual = _I2VA_LAST_FRAME_SENTENCE_PATTERN.sub("", str(shot.get("visual", "")))
            shot["visual"] = re.sub(r"\s{2,}", " ", visual).strip()
    first_shot = next((shot for shot in shots if isinstance(shot, dict) and shot.get("shot_id") == "Shot 1"), None)
    if first_shot is not None and I2VA_FIRST_SHOT_VISUAL_EN.lower() not in str(first_shot.get("visual", "")).lower():
        first_shot["visual"] = f"{I2VA_FIRST_SHOT_VISUAL_EN}. {str(first_shot.get('visual', '')).strip()}".strip()
    if include_last_frame:
        last_shot = next((shot for shot in reversed(shots) if isinstance(shot, dict)), None)
        last_sentence = f"At {float(end_time):.2f} seconds, <Picture 2> is the last frame of the video"
        if last_shot is not None and last_sentence.lower() not in str(last_shot.get("visual", "")).lower():
            visual = str(last_shot.get("visual", "")).strip()
            if visual and visual[-1] not in ".!?":
                visual += "."
            last_shot["visual"] = f"{visual} {last_sentence}".strip()
    return result


def validate_i2va_shot_timeline(value: dict, end_time: float) -> list[str]:
    """Ensure the first and final shot boundaries match the video duration."""
    if not isinstance(value, dict):
        return ["Prompt I2VA harus berupa object JSON."]
    shots = value.get("shots")
    if not isinstance(shots, list) or not shots:
        return []
    try:
        expected_end = float(end_time)
    except (TypeError, ValueError):
        return ["Durasi video I2VA tidak valid."]

    errors = []
    first_shot = next(
        (shot for shot in shots if isinstance(shot, dict) and shot.get("shot_id") == "Shot 1"),
        None,
    )
    if first_shot is not None:
        first_start = first_shot.get("start")
        if isinstance(first_start, Real) and not isinstance(first_start, bool) and abs(float(first_start)) > 1e-6:
            errors.append("Shot 1 I2VA harus dimulai pada 0.00 detik.")

    last_shot = next((shot for shot in reversed(shots) if isinstance(shot, dict)), None)
    if last_shot is not None:
        last_end = last_shot.get("end")
        if (
            isinstance(last_end, Real)
            and not isinstance(last_end, bool)
            and abs(float(last_end) - expected_end) > 1e-6
        ):
            errors.append(
                f"Shot terakhir I2VA harus berakhir pada {expected_end:.2f} detik "
                "sesuai durasi Meta."
            )
    return errors


def validate_i2va_frame_instructions(entry: dict, end_time: float, include_last_frame: bool = False) -> list[str]:
    """Validate mandatory frame sentences in the English prompt payload."""
    errors = []
    localized = unwrap_prompt_value(entry)
    if not isinstance(localized, dict):
        return ["positive_prompt harus berupa object JSON."]
    if str(localized.get("mode", "")).upper() != "I2VA":
        errors.append("positive_prompt.mode harus I2VA.")
    shots = localized.get("shots")
    if not isinstance(shots, list) or not shots:
        return ["positive_prompt.shots wajib berisi minimal satu shot."]
    errors.extend(validate_i2va_shot_timeline(localized, end_time))
    first_shot = next((shot for shot in shots if isinstance(shot, dict) and shot.get("shot_id") == "Shot 1"), None)
    if first_shot is None or I2VA_FIRST_SHOT_VISUAL_EN.lower() not in str(first_shot.get("visual", "")).lower():
        errors.append("Kalimat first frame I2VA wajib ada pada Shot 1.")
    if include_last_frame:
        last_shot = next((shot for shot in reversed(shots) if isinstance(shot, dict)), None)
        expected = f"At {float(end_time):.2f} seconds, <Picture 2> is the last frame of the video"
        if last_shot is None or expected.lower() not in str(last_shot.get("visual", "")).lower():
            errors.append("Kalimat last frame I2VA wajib ada pada shot terakhir.")
    elif any(
        _I2VA_LAST_FRAME_SENTENCE_PATTERN.search(str(shot.get("visual", "")))
        for shot in shots
        if isinstance(shot, dict)
    ):
        errors.append("Kalimat last frame tidak boleh ada jika image akhir tidak dipilih.")
    return errors


def _recover_nested_legacy_prompt(value):
    """Unwrap the accidental one-shot string representation from old saves."""
    current = value
    for _ in range(4):
        if not isinstance(current, dict):
            break
        shots = current.get("shots")
        if not isinstance(shots, list) or len(shots) != 1 or not isinstance(shots[0], dict):
            break
        visual = shots[0].get("visual")
        if not isinstance(visual, str):
            break
        candidate = visual.strip()
        if not (candidate.startswith("{") and candidate.endswith("}")):
            break
        try:
            parsed = json.loads(candidate)
        except Exception:
            try:
                parsed = ast.literal_eval(candidate)
            except Exception:
                break
        if not isinstance(parsed, dict) or not isinstance(parsed.get("shots"), list):
            break
        current = parsed
    return current


def validate_structured_prompt(value, expected_mode: str | None = None) -> list[str]:
    value = unwrap_prompt_value(value)
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["positive_prompt harus berupa object."]
    mode = str(value.get("mode", "")).upper()
    if mode not in {"T2VA", "I2VA"}:
        errors.append("positive_prompt.mode harus T2VA atau I2VA.")
    if expected_mode and mode != str(expected_mode).upper():
        errors.append(f"mode harus {expected_mode}.")
    shots = value.get("shots")
    if not isinstance(shots, list) or not shots:
        errors.append("positive_prompt.shots wajib berupa array berisi minimal satu shot.")
    else:
        previous_end = 0.0
        for index, shot in enumerate(shots):
            prefix = f"positive_prompt.shots[{index}]"
            if not isinstance(shot, dict):
                errors.append(f"{prefix} harus berupa object.")
                continue
            for key in REQUIRED_SHOT_KEYS:
                if key not in shot:
                    errors.append(f"{prefix}.{key} wajib ada.")
            start, end = shot.get("start"), shot.get("end")
            if not isinstance(start, Real) or isinstance(start, bool) or not isinstance(end, Real) or isinstance(end, bool):
                errors.append(f"{prefix}.start dan end harus berupa angka.")
            elif float(start) < 0 or float(end) <= float(start) or float(start) < previous_end:
                errors.append(f"{prefix} memiliki timeline tidak valid atau tidak berurutan.")
            else:
                previous_end = float(end)
            for key in REQUIRED_SHOT_KEYS:
                if key not in {"start", "end"} and not isinstance(shot.get(key), str):
                    errors.append(f"{prefix}.{key} harus berupa string.")
                elif key not in {"start", "end"} and not str(shot.get(key, "")).strip():
                    errors.append(f"{prefix}.{key} tidak boleh kosong.")

    for key in REQUIRED_AUDIO_KEYS:
        if not isinstance(value.get(key), str) or not str(value.get(key)).strip():
            errors.append(f"positive_prompt.{key} wajib berupa string tidak kosong.")
    if mode == "I2VA":
        reference = value.get("reference")
        if not isinstance(reference, dict):
            errors.append("I2VA wajib memiliki positive_prompt.reference.")
        else:
            if reference.get("picture") != "Picture 1":
                errors.append("I2VA reference.picture harus Picture 1.")
            if reference.get("source") != "[Shot 1]":
                errors.append("I2VA reference.source harus [Shot 1].")
            if reference.get("time") != 0.0:
                errors.append("I2VA reference.time harus 0.0.")
            if reference.get("instruction") != "fully referenced":
                errors.append("I2VA reference.instruction tidak valid.")
    elif "reference" in value:
        errors.append("T2VA tidak boleh memiliki field reference.")
    return errors


def serialize_structured_prompt(value) -> str:
    """Convert the nested JSON prompt to the exact MiniMax workflow text."""
    value = unwrap_prompt_value(value)
    if not isinstance(value, dict):
        return str(value or "").strip()
    mode = str(value.get("mode", "T2VA")).upper()
    lines: list[str] = []
    if mode == "I2VA":
        lines.extend([I2VA_FIRST_FRAME_PREFIX, ""])
    lines.append("integrated_multimodal_description:")
    for shot in value.get("shots", []) if isinstance(value.get("shots"), list) else []:
        if not isinstance(shot, dict):
            continue
        visual = str(shot.get("visual", ""))
        if mode == "I2VA" and shot.get("shot_id", "") == "Shot 1":
            detail_marker = "The selected <Picture 1> reference image is the exact visual state"
            if detail_marker.lower() not in visual.lower():
                visual = f"{I2VA_FIRST_FRAME_DETAIL_INSTRUCTION} {visual}".strip()
        lines.append(
            f"[{shot.get('shot_id', 'Shot 1')}] "
            f"From {float(shot.get('start', 0)):.2f} to {float(shot.get('end', 0)):.2f} seconds, "
            f"visual: {visual}; action: {shot.get('action', '')}; "
            f"camera: {shot.get('camera', '')}; dialogue: {shot.get('dialogue', '')}; "
            f"diegetic sound: {shot.get('diegetic_sound', '')}."
        )
    lines.extend([
        "",
        f"overall_soundscape: {value.get('overall_soundscape', '')}",
        "",
        f"non_diegetic_music: {value.get('non_diegetic_music', '')}",
    ])
    return "\n".join(lines).strip()


def prompt_entry_to_display(value) -> str:
    value = unwrap_prompt_value(value)
    if isinstance(value, dict):
        if "mode" in value or "shots" in value or any(key in value for key in REF2VA_SECTION_KEYS):
            return serialize_structured_prompt(value) if str(value.get("mode", "")).upper() in {"T2VA", "I2VA"} else serialize_ref2va_prompt(value)
        return str(value.get("prompt", "") or "").strip()
    return str(value or "").strip()


def parse_structured_response(payload, expected_mode: str) -> tuple[dict | None, list[str]]:
    """Accept a direct MiniMax workflow object or its old wrapper."""
    if not isinstance(payload, dict):
        return None, ["Response MiniMax harus berupa object JSON."]
    entry = copy.deepcopy(payload.get("positive_prompt", payload.get("en", payload)))
    entry = unwrap_prompt_value(entry)
    # Some models emit shot_id as 1, 2, ... although the workflow schema uses
    # the textual identifiers Shot 1, Shot 2, ... . Normalize that harmless
    # representation before strict validation.
    if isinstance(entry, dict):
        if isinstance(entry.get("shots"), list):
            for index, shot in enumerate(entry["shots"], start=1):
                if isinstance(shot, dict):
                    shot_id = shot.get("shot_id")
                    if isinstance(shot_id, (int, float)) and not isinstance(shot_id, bool):
                        shot["shot_id"] = f"Shot {int(shot_id)}"
                    elif not isinstance(shot_id, str) or not shot_id.strip():
                        shot["shot_id"] = f"Shot {index}"
    errors = validate_structured_prompt(entry, expected_mode=expected_mode)
    if errors:
        return None, errors
    return unwrap_prompt_value(entry), []


def normalize_minimax_prompt_payload(data: dict, mode: str) -> dict:
    """Return a MiniMax payload with the canonical direct prompt schema."""
    result = dict(data or {})
    entry = unwrap_prompt_value(result.get("positive_prompt"))
    entry = _recover_nested_legacy_prompt(entry)
    nested = empty_structured_prompt(mode)
    if isinstance(entry, dict) and entry.get("mode"):
        nested = copy.deepcopy(entry)
    elif isinstance(entry, dict) and isinstance(entry.get("shots"), list):
        nested = copy.deepcopy(entry)
    elif isinstance(entry, str) and entry.strip():
        nested["shots"] = [{
            "shot_id": "Shot 1", "start": 0.0, "end": 1.0,
            "visual": entry.strip(), "action": "", "camera": "",
            "dialogue": "", "diegetic_sound": "",
        }]
        nested["overall_soundscape"] = "N/A"
        nested["non_diegetic_music"] = "N/A"
    result["positive_prompt"] = nested
    return result
