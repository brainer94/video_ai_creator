---
name: minimax-h3-i2v-prompt
description: Menulis prompt MiniMax H3 I2VA dengan satu gambar sebagai first frame.
---

# MiniMax H3 I2VA Prompt

Gunakan mode `I2VA`. Prompt disimpan langsung dalam bahasa Inggris pada `positive_prompt`. Prompt wajib memiliki anchor berikut pada awal hasil serialisasi:

`<Picture 1>` adalah gambar referensi aktual dan merupakan kondisi visual persis pada frame pertama. Kalimat alignment di bawah ini hanya muncul pada prompt runtime, bukan pada JSON authoring:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

## Struktur JSON

```json
{
  "positive_prompt": {
    "mode": "I2VA",
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

`shots` minimal satu item. Setiap item wajib memiliki delapan field yang sama dengan T2VA. Field `reference` tidak ditulis pada JSON authoring; runtime membuatnya untuk memetakan `Picture 1` ke `[Shot 1]` pada `0.0`.

## Cara menulis prompt

1. Mulai `Shot 1` dari komposisi, subjek, pakaian, warna, objek penting, pencahayaan, dan layout yang terlihat pada `<Picture 1>`.
2. Gunakan `<Picture 1>` sebagai dasar visual Shot 1. Peran first frame dan kalimat alignment ditambahkan oleh runtime, bukan ditulis dalam prompt authoring.
3. Kembangkan gerakan secara kontinu menuju akhir video dan pertahankan identitas, komposisi, pakaian, objek, pencahayaan, serta hubungan ruang.
4. Jelaskan aksi, kamera, dialog, suara diegetik, ambience, dan musik sesuai timeline.

Prompt runtime diserialisasi dari object langsung ini. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris, tetapi runtime tidak menerjemahkan prompt.

Jangan memakai format T2VA, FL2VA, atau L2VA dan jangan menambahkan `negative_prompt`.
