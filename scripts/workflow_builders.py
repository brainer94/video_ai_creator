import copy
import json
import os

from z_image.z_image import build_z_image_workflow


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_TEMPLATE = os.path.join(ROOT, "api_template")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_template(name):
    return load_json(os.path.join(API_TEMPLATE, name))


def traverse_and_replace(node, replace_map):
    if isinstance(node, dict):
        inputs = node.get("inputs")
        if isinstance(inputs, dict) and "text" in inputs:
            val = inputs["text"]
            if isinstance(val, str) and val in replace_map:
                inputs["text"] = replace_map[val]
        for value in node.values():
            traverse_and_replace(value, replace_map)
    elif isinstance(node, list):
        for item in node:
            traverse_and_replace(item, replace_map)


def replace_any_string_values(node, replace_map):
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, str):
                if value in replace_map:
                    node[key] = replace_map[value]
            else:
                replace_any_string_values(value, replace_map)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            if isinstance(item, str):
                if item in replace_map:
                    node[idx] = replace_map[item]
            else:
                replace_any_string_values(item, replace_map)


def bypass_model_lora_nodes(
    workflow: dict,
    lora_node_ids: tuple[str, ...] | list[str],
    base_model_node_id: str,
) -> None:
    """Remove model-only LoRA nodes and reconnect their model consumers.

    MiniMax templates place two ``LoraLoaderModelOnly`` nodes in a model
    chain.  When LoRA is disabled, leaving those nodes in the API payload can
    still make ComfyUI try to load the selected file.  Reconnect every model
    input that points to one of the LoRA nodes, then remove the nodes so the
    workflow follows the original model path directly.
    """
    if not isinstance(workflow, dict):
        return
    lora_ids = {str(node_id) for node_id in (lora_node_ids or ())}
    if not lora_ids:
        return
    base_link = [str(base_model_node_id), 0]
    for node in workflow.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        for key, value in list(inputs.items()):
            if key != "model" or not isinstance(value, list) or not value:
                continue
            if str(value[0]) in lora_ids:
                inputs[key] = list(base_link)
    for node_id in lora_ids:
        workflow.pop(node_id, None)
