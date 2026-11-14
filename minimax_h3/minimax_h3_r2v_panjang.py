"""Shared defaults for the chained MiniMax H3 R2V scene."""

from __future__ import annotations

import copy

from minimax_h3_r2v.minimax_h3_r2v import DEFAULT_R2V_PROMPT


SCENE_TYPE = "minimax-h3_r2v-panjang"
PROMPT_FILENAME = "minimax_h3_r2v_panjang_prompt.json"
MAX_PROMPTS = 4
MAX_GLOBAL_IMAGE_REFERENCES = 4


def build_default_prompt() -> dict:
    base = copy.deepcopy(DEFAULT_R2V_PROMPT)
    base.pop("prompt_instruction", None)
    base.pop("positive_prompt", None)
    base["continuations"] = 0
    base["run_start_stage"] = 1
    base["prompts"] = [
        copy.deepcopy(DEFAULT_R2V_PROMPT["positive_prompt"])
        for _ in range(MAX_PROMPTS)
    ]
    base["prompt_instructions"] = ["" for _ in range(MAX_PROMPTS)]
    base["references"] = {
        "images": [],
        "initial_image": "",
        "audios": [],
        "video": "",
    }
    base["remove_sound"] = False
    return base


DEFAULT_PROMPT = build_default_prompt()
