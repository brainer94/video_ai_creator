---
name: minimax-h3-i2v-prompt
description: Menulis prompt MiniMax H3 I2VA dengan satu gambar sebagai first frame.
---

# MiniMax H3 I2VA Prompt

Gunakan mode `I2VA`. Prompt disimpan langsung dalam bahasa Inggris pada `positive_prompt`. Prompt wajib memiliki anchor berikut pada awal hasil serialisasi:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

`<Picture 1>` adalah gambar referensi aktual dan merupakan kondisi visual persis pada frame pertama.

## Struktur JSON

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
  }
}
```

`shots` minimal satu item. Setiap item wajib memiliki delapan field yang sama dengan T2VA. `reference` harus persis memetakan `Picture 1` ke `[Shot 1]` pada `0.0`.

## Cara menulis prompt

1. Mulai `Shot 1` dari komposisi, subjek, pakaian, warna, objek penting, pencahayaan, dan layout yang terlihat pada `<Picture 1>`.
2. Tegaskan bahwa `<Picture 1>` adalah exact first frame pada `0.00` detik.
3. Kembangkan gerakan secara kontinu menuju akhir video dan pertahankan identitas, komposisi, pakaian, objek, pencahayaan, serta hubungan ruang.
4. Jelaskan aksi, kamera, dialog, suara diegetik, ambience, dan musik sesuai timeline.

Prompt runtime diserialisasi dari object langsung ini. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris, tetapi runtime tidak menerjemahkan prompt.

Jangan memakai format T2VA, FL2VA, atau L2VA dan jangan menambahkan `negative_prompt`.
