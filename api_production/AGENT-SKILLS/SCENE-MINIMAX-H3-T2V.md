# Scene minimax-h3_t2v

Scene ini memakai satu workflow MiniMax H3 T2VA tanpa gambar referensi atau stage I2V.

## File output

Scene menyediakan `minimax_h3_t2v_prompt.json`:

```json
{
  "positive_prompt": {
    "mode": "T2VA",
    "shots": [
      {
        "shot_id": "Shot 1",
        "start": 0.0,
        "end": 5.0,
        "visual": "...",
        "action": "...",
        "camera": "...",
        "dialogue": "...",
        "diegetic_sound": "..."
      }
    ],
    "overall_soundscape": "...",
    "non_diegetic_music": "N/A"
  },
  "lora_name": "MINIMAX-H3/AI-Girl-Fictional.safetensors",
  "lora_strength": 0,
  "width": 368,
  "height": 640
}
```

Prompt disimpan langsung dalam bahasa Inggris. Jangan membuat key `id_new`, `id_old`, atau `en`; jangan menambahkan `negative_prompt` atau `reference`.

## Prompt T2VA

- `positive_prompt.mode` harus `T2VA`.
- `shots[]` minimal satu item dengan `shot_id`, `start`, `end`, `visual`, `action`, `camera`, `dialogue`, dan `diegetic_sound`.
- `shot_id` berupa string `Shot N`; waktu berupa angka JSON berurutan, tidak tumpang tindih, dan berada dalam durasi scene.
- `overall_soundscape` merangkum ambience dan suara fisik.
- `non_diegetic_music` menjelaskan musik penonton atau `N/A`.
- Dialog dan teks layar mempertahankan bahasa serta tanda baca asli.
- Runtime menserialisasi object langsung ini; runtime tidak menerjemahkan prompt. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris.

## Durasi dan resolusi

- Durasi `0.0` sampai `15.0` detik, maksimal empat angka desimal.
- FPS MiniMax H3 adalah `24`.
- Ukuran scene disimpan pada prompt dan diterapkan ke node `ResolutionSelector`.
- `lora_name` dan `lora_strength` berasal dari folder `MINIMAX-H3` di ComfyUI.

## Checklist

- JSON valid dan prompt langsung berupa object T2VA.
- Tidak ada wrapper bahasa, `negative_prompt`, atau `reference`.
- Timeline berada dalam durasi scene.
- LoRA dan ukuran valid.
