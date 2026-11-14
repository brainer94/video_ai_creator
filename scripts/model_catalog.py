"""Model download catalog used by the Scene Manager model dialog.

The catalog deliberately contains only weights required by the workflows in
this project.  Custom nodes and optional user LoRAs are outside its scope.
"""

from __future__ import annotations

from copy import deepcopy

from scripts.special_mode import is_special_mode_enabled


MODEL_SPECS = {
    "minimax_h3_fl2va": {
        "label": "MiniMax H3 FL2VA",
        "runtime_name": "MINIMAX-H3/minimax_h3_fl2va_pruned_int8_convrot.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/MINIMAX-H3",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    },
    "minimax_h3_ref2va": {
        "label": "MiniMax H3 Ref2VA",
        "runtime_name": "MINIMAX-H3/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/MINIMAX-H3",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
    },
    "minimax_h3_text_encoder": {
        "label": "MiniMax H3 Text Encoder",
        "runtime_name": "MINIMAX-H3/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
        "manager_type": "clip",
        "save_path": "text_encoders/MINIMAX-H3",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    },
    "minimax_h3_video_vae": {
        "label": "MiniMax H3 Video VAE",
        "runtime_name": "MINIMAX-H3/minimax_h3_video_vae_int8_convrot.safetensors",
        "manager_type": "vae",
        "save_path": "vae/MINIMAX-H3",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_int8_convrot.safetensors",
    },
    "minimax_h3_audio_vae": {
        "label": "MiniMax H3 Audio VAE",
        "runtime_name": "MINIMAX-H3/minimax_h3_audio_vae_fp32.safetensors",
        "manager_type": "vae",
        "save_path": "vae/MINIMAX-H3",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors",
    },
    "minimax_h3_image_diffusion": {
        "label": "MiniMax H3 Image Diffusion",
        "runtime_name": "MINIMAX-H3-IMAGE/minimax_h3_image_pruned_int8_convrot.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/MINIMAX-H3-IMAGE",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3-Image/resolve/main/diffusion_models/minimax_h3_image_pruned_int8_convrot.safetensors?download=true",
    },
    "minimax_h3_image_vae": {
        "label": "MiniMax H3 Image VAE",
        "runtime_name": "MINIMAX-H3-IMAGE/minimax_h3_image_vae_fp16.safetensors",
        "manager_type": "vae",
        "save_path": "vae/MINIMAX-H3-IMAGE",
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3-Image/resolve/main/vae/minimax_h3_image_vae_fp16.safetensors?download=true",
    },
    "minimax_fast_t2v_i2v": {
        "label": "FastH3 T2V/I2V",
        "runtime_name": "MINIMAX-H3/fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/MINIMAX-H3",
        "url": "https://huggingface.co/FastVideo/FastVideo-FastH3-Comfy/resolve/main/diffusion_models/fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors",
    },
    "minimax_fast_r2v": {
        "label": "FastH3 Omni R2V",
        "runtime_name": "MINIMAX-H3/fasth3_omniref_8step_pruned_int8_convrot.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/MINIMAX-H3",
        "url": "https://huggingface.co/FastVideo/FastH3-Omni-Comfy/resolve/main/diffusion_models/fasth3_omniref_8step_pruned_int8_convrot.safetensors",
    },
    "minimax_special": {
        "label": "MiniMax H3 Mode Khusus",
        "runtime_name": "MINIMAX-H3/10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/MINIMAX-H3",
        "url": "https://huggingface.co/TenStrip/10Eros-Max/resolve/main/10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors",
    },
    "flux2_diffusion": {
        "label": "Flux 2 Diffusion",
        "runtime_name": "FLUX2/flux2_dev_fp8mixed.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/FLUX2",
        "url": "https://huggingface.co/Comfy-Org/Flux-2-Dev/resolve/main/split_files/diffusion_models/flux2_dev_fp8mixed.safetensors",
    },
    "flux2_text_encoder": {
        "label": "Flux 2 Text Encoder",
        "runtime_name": "FLUX2/mistral_3_small_flux2_fp8.safetensors",
        "manager_type": "clip",
        "save_path": "text_encoders/FLUX2",
        "url": "https://huggingface.co/Comfy-Org/Flux-2-Dev/resolve/main/split_files/text_encoders/mistral_3_small_flux2_fp8.safetensors",
    },
    "flux2_vae": {
        "label": "Flux 2 VAE",
        "runtime_name": "FLUX2/flux2-vae.safetensors",
        "manager_type": "vae",
        "save_path": "vae/FLUX2",
        "url": "https://huggingface.co/Comfy-Org/Flux-2-Dev/resolve/main/split_files/vae/flux2-vae.safetensors",
    },
    "z_image_diffusion": {
        "label": "Z Image Turbo Diffusion",
        "runtime_name": "Z-IMAGE/z_image_turbo_bf16.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/Z-IMAGE",
        "url": "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors",
    },
    "z_image_text_encoder": {
        "label": "Z Image Turbo Text Encoder",
        # The existing Z-Image workflows load this file from QWEN/.
        "runtime_name": "QWEN/qwen_3_4b.safetensors",
        "manager_type": "clip",
        "save_path": "text_encoders/QWEN",
        "url": "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors",
    },
    "z_image_vae": {
        "label": "Z Image Turbo VAE",
        "runtime_name": "Z-IMAGE/ae.safetensors",
        "manager_type": "vae",
        "save_path": "vae/Z-IMAGE",
        "url": "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors",
    },
    "qwen_image_diffusion": {
        "label": "Qwen Image Edit Diffusion",
        "runtime_name": "QWEN/qwen_image_2.1_bf16.safetensors",
        "manager_type": "unet",
        "save_path": "diffusion_models/QWEN",
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/split_files/diffusion_models/qwen_image_2.1_bf16.safetensors",
    },
    "qwen_image_text_encoder": {
        "label": "Qwen Image Edit Text Encoder",
        "runtime_name": "QWEN/qwen3vl_8b_bf16.safetensors",
        "manager_type": "clip",
        "save_path": "text_encoders/QWEN",
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/split_files/text_encoders/qwen3vl_8b_bf16.safetensors",
    },
    "qwen_image_vae": {
        "label": "Qwen Image Edit VAE",
        "runtime_name": "QWEN/qwen_image_2.1_vae_bf16.safetensors",
        "manager_type": "vae",
        "save_path": "vae/QWEN",
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/split_files/vae/qwen_image_2.1_vae_bf16.safetensors",
    },
}

_H3_BASE = [
    "minimax_h3_fl2va",
    "minimax_h3_ref2va",
    "minimax_h3_text_encoder",
    "minimax_h3_video_vae",
    "minimax_h3_audio_vae",
]

# The special checkpoint uses the shared text/audio/video components, but it
# does not require the normal MiniMax-H3 FL2VA and Ref2VA diffusion weights.
_H3_SPECIAL_SHARED = [
    "minimax_h3_text_encoder",
    "minimax_h3_video_vae",
    "minimax_h3_audio_vae",
]

MODEL_GROUPS = [
    {
        "id": "minimax_h3",
        "label": "MiniMax H3",
        "description": "T2V, I2V, dan R2V mode normal.",
        "model_ids": list(_H3_BASE),
    },
    {
        "id": "minimax_h3_fast",
        "label": "MiniMax H3 Mode Cepat",
        "description": "FastH3 untuk T2V/I2V dan FastH3 Omni untuk R2V.",
        "model_ids": _H3_BASE + ["minimax_fast_t2v_i2v", "minimax_fast_r2v"],
    },
    {
        "id": "minimax_h3_special",
        "label": "MiniMax H3 Mode Khusus",
        "description": "Checkpoint 10Eros-Max beta6 8-step tanpa checkpoint FL2VA dan Ref2VA normal.",
        "model_ids": _H3_SPECIAL_SHARED + ["minimax_special"],
    },
    {
        "id": "minimax_h3_image",
        "label": "MiniMax H3 Image",
        "description": "MiniMax H3 Image untuk image editing berbasis referensi.",
        "model_ids": [
            "minimax_h3_image_diffusion",
            "minimax_h3_text_encoder",
            "minimax_h3_image_vae",
        ],
    },
    {
        "id": "flux2",
        "label": "Flux 2",
        "description": "Flux 2 Dev untuk workflow image.",
        "model_ids": ["flux2_diffusion", "flux2_text_encoder", "flux2_vae"],
    },
    {
        "id": "z_image_turbo",
        "label": "Z Image Turbo",
        "description": "Z Image Turbo untuk image generation dan cover.",
        "model_ids": ["z_image_diffusion", "z_image_text_encoder", "z_image_vae"],
    },
    {
        "id": "qwen_image_edit",
        "label": "Qwen Image Edit",
        "description": "Qwen Image 2.1 untuk image editing berbasis referensi.",
        "model_ids": ["qwen_image_diffusion", "qwen_image_text_encoder", "qwen_image_vae"],
    },
]

def get_model_groups() -> list[dict]:
    """Return a copy so callers cannot mutate the catalog."""
    groups = deepcopy(MODEL_GROUPS)
    if not is_special_mode_enabled():
        groups = [group for group in groups if group.get("id") != "minimax_h3_special"]
    return groups


def expand_model_groups(group_ids) -> list[dict]:
    """Expand selected groups into an ordered, de-duplicated model list."""
    selected = {str(value).strip() for value in (group_ids or []) if str(value).strip()}
    expanded_ids = []
    seen = set()
    for group in get_model_groups():
        if group["id"] not in selected:
            continue
        for model_id in group["model_ids"]:
            if model_id in seen:
                continue
            if model_id not in MODEL_SPECS:
                raise KeyError(f"Model catalog tidak memiliki item: {model_id}")
            seen.add(model_id)
            expanded_ids.append(model_id)
    return [deepcopy(MODEL_SPECS[model_id] | {"id": model_id}) for model_id in expanded_ids]

