---
name: scene-minimax-h3-i2v
description: Create standalone MiniMax H3 I2V scenes with an optional generated initial image and a MiniMax H3 I2VA video stage.
---

# Scene minimax-h3_i2v

Scene ini adalah workflow I2V mandiri. `Gambar Awal` dapat membuat gambar dari `z_image_prompt.json`, lalu gambar terbaru di root scene menjadi `Picture 1`.

## File output

Scene menyediakan:

- `z_image_prompt.json`
- `minimax_h3_i2v_prompt.json`

`minimax_h3_i2v_prompt.json` menyimpan prompt langsung dalam bahasa Inggris:

```json
{
  "positive_prompt": {
    "mode": "I2VA",
    "reference": {
      "picture": "Picture 1",
      "source": "[Shot 1]",
      "time": 0.0,
      "instruction": "fully referenced"
    },
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

Jangan membuat key `id_new`, `id_old`, atau `en` dan jangan menambahkan `negative_prompt`.

## Aturan I2VA

- `mode` harus `I2VA`.
- `reference` harus persis memetakan `Picture 1` ke `[Shot 1]) pada `0.0`.
- `shots[]` memakai struktur yang sama dengan T2VA.
- Hasil serialisasi harus dimulai dengan:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

- Mulai shot pertama dari komposisi, subjek, pakaian, objek, pencahayaan, dan layout pada gambar awal.
- Kembangkan aksi kontinu sampai akhir video dan pertahankan identitas serta hubungan ruang.
- Runtime tidak menerjemahkan prompt. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris.

## Durasi dan sumber gambar

- Durasi `0.0) sampai `15.0) detik dengan maksimal empat angka desimal.
- Gambar terbaru dari root scene menjadi first frame `Picture 1`.
- Scene tidak menjalankan T2V.
- Ukuran dan LoRA diterapkan sesuai konfigurasi scene dan folder `MINIMAX-H3`.

## Checklist

- Dua file JSON tersedia dan valid.
- Prompt I2VA langsung berupa object dan memiliki `reference), `shots[]), serta dua audio global.
- Anchor `Picture 1` ada di awal prompt runtime.
- Tidak ada wrapper bahasa atau `negative_prompt`.
