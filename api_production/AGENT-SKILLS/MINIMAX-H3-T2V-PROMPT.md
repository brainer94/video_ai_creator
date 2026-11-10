---
name: minimax-h3-t2v-prompt
description: Menulis prompt MiniMax H3 T2VA berbasis teks tanpa image alignment reference.
---

# MiniMax H3 T2VA Prompt

Gunakan mode `T2VA`. Prompt disimpan langsung dalam bahasa Inggris pada `positive_prompt`; jangan membuat wrapper bahasa atau field `reference`.

## Struktur JSON

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
  }
}
```

`shots` minimal satu item. Setiap item wajib memiliki `shot_id`, `start`, `end`, `visual`, `action`, `camera`, `dialogue`, dan `diegetic_sound`. `shot_id` berupa string `Shot N`; waktu berupa angka JSON yang berurutan, tidak tumpang tindih, dan berada dalam durasi video.

## Cara menulis prompt

1. `shots[]` adalah timeline audiovisual utama; jelaskan komposisi, subjek, lingkungan, aksi, kamera, dialog, dan suara diegetik pada shot yang sesuai.
2. Shot berikutnya boleh memperkenalkan cut, sudut pandang, ruang, waktu, atau informasi visual baru.
3. `overall_soundscape` merangkum ambience dan suara fisik sepanjang video.
4. `non_diegetic_music` menjelaskan musik yang hanya didengar penonton; gunakan `N/A` bila tidak ada.
5. Gunakan hanya token reference yang benar-benar disediakan oleh scene. Dialog lengkap dan lirik tetap mengikuti `MINIMAX-H3-DIALOG.md`.

Prompt runtime diserialisasi dari object langsung ini menjadi tiga section MiniMax. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris, tetapi runtime tidak menerjemahkan prompt.

Jangan menambahkan `reference`, `negative_prompt`, wrapper bahasa, atau instruksi first-frame ke prompt T2VA.
