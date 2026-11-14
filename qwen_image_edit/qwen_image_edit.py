import copy
import json
import os
import random

from scripts import comfyui_api
from logging_config import get_logger, write_log
from minimax_h3.minimax_h3_prompt import unwrap_prompt_value


logger = get_logger(__name__)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_TEMPLATE = os.path.join(ROOT, "api_template")

ENGINE_QWEN_2_1 = "qwen_2_1"
ENGINE_MINIMAX_H3_IMAGE = "minimax_h3_image"
DEFAULT_ENGINE = ENGINE_QWEN_2_1
ENGINE_OPTIONS = (
    (ENGINE_MINIMAX_H3_IMAGE, "Minimax H3 Image"),
    (ENGINE_QWEN_2_1, "Qwen 2.1 Image"),
)
ENGINE_TEMPLATES = {
    ENGINE_QWEN_2_1: "qwen_2_1_edit_api.json",
    ENGINE_MINIMAX_H3_IMAGE: "minimax_h3_image_edit_api.json",
}

# Backward-compatible alias for code that imported the original template name.
TEMPLATE = ENGINE_TEMPLATES[ENGINE_QWEN_2_1]
MAX_REFERENCE_IMAGES = 10
TEXT_ENCODE_NODE = "510"
LATENT_NODE = "505"
SAMPLER_NODE = "507"
REFERENCE_NODE_START = 470

MINIMAX_CONDITIONING_NODE = "32"
MINIMAX_FIRST_IMAGE_NODE = "45"
MINIMAX_FIRST_RESIZE_NODE = "56"
MINIMAX_GRID_RESIZE_NODE = "48"
MINIMAX_SIZE_NODE = "50"
MINIMAX_SAMPLER_NODE = "38"

SIZE_OPTIONS = [
    ("368x640", 368, 640),
    ("480x848", 480, 848),
    ("720x1280", 720, 1280),
    ("640x368", 640, 368),
    ("848x480", 848, 480),
    ("1280x720", 1280, 720),
]

DEFAULT_PROMPT = {
    "engine": DEFAULT_ENGINE,
    "images": ["" for _ in range(MAX_REFERENCE_IMAGES)],
    "width": 368,
    "height": 640,
    "use_random_seed": True,
    "seed": 1,
    "number_of_edits": 1,
    "prompt_images": ["" for _ in range(MAX_REFERENCE_IMAGES)],
    "prompt_instruction": "",
    "positive_prompt": "",
    "negative_prompt": "",
    "target_aspect_ratio": "",
}


def normalize_engine(value) -> str:
    value = str(value or "").strip().lower()
    aliases = {
        "": DEFAULT_ENGINE,
        "qwen": ENGINE_QWEN_2_1,
        "qwen 2.1": ENGINE_QWEN_2_1,
        "qwen 2.1 image": ENGINE_QWEN_2_1,
        "qwen_image": ENGINE_QWEN_2_1,
        "qwen_image_2.1": ENGINE_QWEN_2_1,
        "minimax": ENGINE_MINIMAX_H3_IMAGE,
        "minimax h3 image": ENGINE_MINIMAX_H3_IMAGE,
        "minimax_h3": ENGINE_MINIMAX_H3_IMAGE,
        "minimax_h3_image": ENGINE_MINIMAX_H3_IMAGE,
    }
    return aliases.get(value, DEFAULT_ENGINE)


def engine_label(value) -> str:
    normalized = normalize_engine(value)
    return dict(ENGINE_OPTIONS).get(normalized, dict(ENGINE_OPTIONS)[DEFAULT_ENGINE])


def _load_template(engine=DEFAULT_ENGINE) -> dict:
    normalized_engine = normalize_engine(engine)
    template_name = ENGINE_TEMPLATES[normalized_engine]
    with open(os.path.join(API_TEMPLATE, template_name), "r", encoding="utf-8") as file:
        return json.load(file)


def _prompt_text(value) -> str:
    value = unwrap_prompt_value(value)
    if isinstance(value, dict):
        return str(value.get("prompt", "") or "").strip()
    return str(value or "").strip()


def _set_node_input(workflow: dict, node_id: str, key: str, value):
    node = workflow.get(node_id)
    if not isinstance(node, dict):
        node = {"inputs": {}, "class_type": ""}
        workflow[node_id] = node
    inputs = node.setdefault("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}
        node["inputs"] = inputs
    inputs[key] = value


def _set_reference_images(workflow: dict, image_names) -> None:
    """Inject only selected reference images into TextEncodeQwenImage21.

    Empty dropdowns intentionally remove both the LoadImage node and the
    corresponding autogrow input. This allows sparse selections such as
    image_1 and image_4 without inventing placeholder files.
    """
    values = [
        str(value or "").strip()
        for value in list(image_names or [])[:MAX_REFERENCE_IMAGES]
        if str(value or "").strip()
    ]
    for slot in range(1, MAX_REFERENCE_IMAGES + 1):
        node_id = str(REFERENCE_NODE_START + slot - 1)
        input_key = f"images.image_{slot}"
        workflow.pop(node_id, None)
        encoder = workflow.get(TEXT_ENCODE_NODE)
        if isinstance(encoder, dict) and isinstance(encoder.get("inputs"), dict):
            encoder["inputs"].pop(input_key, None)

        image_name = str(values[slot - 1] if slot - 1 < len(values) else "").strip()
        if not image_name:
            continue
        workflow[node_id] = {
            "inputs": {"image": image_name},
            "class_type": "LoadImage",
            "_meta": {"title": f"Load Reference Image {slot}"},
        }
        _set_node_input(workflow, TEXT_ENCODE_NODE, input_key, [node_id, 0])


def _selected_reference_images(image_names) -> list[str]:
    return [
        str(value or "").strip()
        for value in list(image_names or [])[:MAX_REFERENCE_IMAGES]
        if str(value or "").strip()
    ]


def _next_workflow_node_id(workflow: dict) -> str:
    numeric_ids = []
    for key in workflow:
        try:
            numeric_ids.append(int(str(key)))
        except (TypeError, ValueError):
            continue
    return str(max(numeric_ids, default=0) + 1)


def _set_minimax_reference_images(workflow: dict, image_names) -> int:
    """Inject the first image through the 4 MP sizing path and later images directly.

    MiniMax H3 Image uses the first reference as the image being edited. Its
    resized dimensions also determine the output latent size. Additional
    references are deliberately connected directly to the conditioning node;
    the node performs its own reference scaling for those images.
    """
    values = _selected_reference_images(image_names)
    if not values:
        raise ValueError("MiniMax H3 Image membutuhkan minimal satu gambar referensi.")

    conditioning = workflow.get(MINIMAX_CONDITIONING_NODE)
    if not isinstance(conditioning, dict):
        raise RuntimeError("Template MiniMax H3 Image tidak memiliki node conditioning.")
    inputs = conditioning.setdefault("inputs", {})
    for key in list(inputs):
        if str(key).startswith("images.image_"):
            inputs.pop(key, None)

    _set_node_input(workflow, MINIMAX_FIRST_IMAGE_NODE, "image", values[0])
    _set_node_input(
        workflow,
        MINIMAX_CONDITIONING_NODE,
        "images.image_1",
        [MINIMAX_GRID_RESIZE_NODE, 0],
    )

    next_node_id = _next_workflow_node_id(workflow)
    for picture_number, image_name in enumerate(values[1:], start=2):
        node_id = next_node_id
        next_node_id = str(int(next_node_id) + 1)
        workflow[node_id] = {
            "inputs": {"image": image_name},
            "class_type": "LoadImage",
            "_meta": {"title": f"Load Reference Image {picture_number}"},
        }
        _set_node_input(
            workflow,
            MINIMAX_CONDITIONING_NODE,
            f"images.image_{picture_number}",
            [node_id, 0],
        )
    return len(values)


def _set_seed(workflow: dict, prompt: dict | None) -> int:
    prompt = prompt if isinstance(prompt, dict) else {}
    use_random = bool(prompt.get("use_random_seed", True))
    if use_random:
        seed = random.randint(10**15, 10**16 - 1)
    else:
        try:
            seed = int(prompt.get("seed", 1))
        except (TypeError, ValueError):
            seed = 1
        if seed <= 0:
            seed = 1
    _set_node_input(workflow, SAMPLER_NODE, "seed", seed)
    return seed


def _set_minimax_seed(workflow: dict) -> int:
    seed = random.randint(10**15, 10**16 - 1)
    _set_node_input(workflow, MINIMAX_SAMPLER_NODE, "seed", seed)
    return seed


def _build_qwen_workflow(prompt: dict, uploaded_images=None) -> dict:
    prompt = prompt if isinstance(prompt, dict) else {}
    workflow = copy.deepcopy(_load_template(ENGINE_QWEN_2_1))
    _set_node_input(workflow, TEXT_ENCODE_NODE, "prompt", _prompt_text(prompt.get("positive_prompt", "")))
    _set_node_input(workflow, TEXT_ENCODE_NODE, "negative_prompt", _prompt_text(prompt.get("negative_prompt", "")))

    try:
        width = int(prompt.get("width", DEFAULT_PROMPT["width"]))
    except (TypeError, ValueError):
        width = DEFAULT_PROMPT["width"]
    try:
        height = int(prompt.get("height", DEFAULT_PROMPT["height"]))
    except (TypeError, ValueError):
        height = DEFAULT_PROMPT["height"]
    _set_node_input(workflow, LATENT_NODE, "width", max(1, width))
    _set_node_input(workflow, LATENT_NODE, "height", max(1, height))

    image_names = uploaded_images if uploaded_images is not None else prompt.get("images", [])
    _set_reference_images(workflow, image_names)
    _set_seed(workflow, prompt)
    return workflow


def _build_minimax_workflow(prompt: dict, uploaded_images=None) -> dict:
    prompt = prompt if isinstance(prompt, dict) else {}
    workflow = copy.deepcopy(_load_template(ENGINE_MINIMAX_H3_IMAGE))
    _set_node_input(
        workflow,
        "43",
        "value",
        _prompt_text(prompt.get("positive_prompt", "")),
    )
    reference_count = _set_minimax_reference_images(workflow, uploaded_images)
    _set_minimax_seed(workflow)
    write_log(f"MiniMax H3 Image references={reference_count}")
    return workflow


def build_workflow(prompt: dict, uploaded_images=None) -> dict:
    prompt = prompt if isinstance(prompt, dict) else {}
    engine = normalize_engine(prompt.get("engine"))
    if engine == ENGINE_MINIMAX_H3_IMAGE:
        return _build_minimax_workflow(prompt, uploaded_images=uploaded_images)
    return _build_qwen_workflow(prompt, uploaded_images=uploaded_images)


def build_qwen_image_edit_workflow(prompt: dict, uploaded_images=None) -> dict:
    return build_workflow(prompt, uploaded_images=uploaded_images)


def send_workflow(prompt: dict, server: str, uploaded_images=None):
    workflow = build_workflow(prompt, uploaded_images=uploaded_images)
    engine = normalize_engine(prompt.get("engine") if isinstance(prompt, dict) else "")
    if engine == ENGINE_MINIMAX_H3_IMAGE:
        size_node = workflow.get(MINIMAX_SIZE_NODE, {})
        size_inputs = size_node.get("inputs", {}) if isinstance(size_node, dict) else {}
        size_text = "output-size-from-first-reference"
        reference_count = sum(
            1
            for key in workflow.get(MINIMAX_CONDITIONING_NODE, {}).get("inputs", {})
            if str(key).startswith("images.image_")
        )
    else:
        size_inputs = workflow[LATENT_NODE]["inputs"]
        size_text = f"{size_inputs.get('width')}x{size_inputs.get('height')}"
        reference_count = sum(
            1 for key in workflow.get(TEXT_ENCODE_NODE, {}).get("inputs", {}) if key.startswith("images.image_")
        )
    write_log(
        f"{engine_label(engine)} workflow: size={size_text}, references={reference_count}"
    )
    return comfyui_api.post_workflow_api(workflow, server)
