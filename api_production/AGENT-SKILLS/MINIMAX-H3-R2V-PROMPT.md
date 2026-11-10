---
name: minimax-h3-r2v-prompt
description: Menulis prompt MiniMax H3 Ref2VA/R2V dengan reference image, video, dan audio yang aktif.
---

# MiniMax H3 R2V Ref2VA Prompt

Gunakan mode `R2VA`. Prompt disimpan langsung dalam bahasa Inggris pada `positive_prompt` dan memiliki enam section Ref2VA dalam urutan yang sama saat diserialisasi:

```text
subject_definitions: ...

summary: ...

retention_analysis: ...

detailed_description: ...

overall_soundscape: ...

non_diegetic_music: ...
```

## Struktur JSON authoring

```json
{
  "positive_prompt": {
    "mode": "R2VA",
    "style_opening": "...",
    "subject_definitions": "...",
    "summary": "...",
    "retention_analysis": "...",
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
  "references": {"images": [], "audios": [], "video": ""}
}
```

`shots[]` memakai struktur yang sama dengan T2VA dan I2VA. Aplikasi mengompilasi `style_opening` dan kartu shot menjadi section runtime `detailed_description`; jangan menyimpan wrapper bahasa dan jangan menulis ulang isi adegan saat mengubah struktur.

Saat dikirim ke ComfyUI, setiap shot R2V diserialisasi dengan rentang waktu eksplisit:

```text
[Shot 1] From 0.00 to 1.00 seconds, ...
[Shot 2] From 1.00 to 3.00 seconds, ...
```

Parser tetap menerima format lama `[Shot N] At MM:SS.mmm, ...` agar project lama tetap dapat dimuat, tetapi prompt baru harus menggunakan rentang `From ... to ... seconds`.

Untuk scene `minimax-h3_r2v-panjang`, gunakan empat prompt authoring di
`minimax_h3_r2v_panjang_prompt.json`. Reference image global ditulis dalam
`references.images` dengan maksimal empat item; runtime menambahkan frame
terakhir proses sebelumnya sebagai Picture berikutnya pada proses 2–4. Jangan
menulis frame carry ke array reference global.

## Reference aktif

Token harus dibuat dari manifest aktif dengan penomoran rapat: image `<Picture N>`, video `<Video 1>`, dan audio `<Audio N>`. Gunakan hanya token yang benar-benar tersedia. `<Subject N>`, `<Shot N>`, `<d>`, `</d>`, dan speaker ID adalah token semantik yang tetap boleh digunakan.

Pertahankan setiap token reference persis sama pada keenam section. Jangan mengarang, mengganti nama, atau melompati nomor token.

## Cara menulis enam section

- `subject_definitions`: identitas subjek dan hubungan dengan reference aktif.
- `summary`: ringkasan adegan, tujuan aksi, dan hubungan antar-reference.
- `retention_analysis`: detail reference yang harus dipertahankan.
- `style_opening`: gaya visual global sebelum shot pertama, bila diperlukan.
- `shots[]`: timeline visual, aksi, kamera, dialog, suara, dan penggunaan reference.
- `overall_soundscape`: ambience, suara fisik, suara manusia non-verbal, dan audio reference.
- `non_diegetic_music`: musik latar atau `N/A`.

Teks dialog dan lirik lengkap hanya ditulis pada field dialog shot sesuai aturan `MINIMAX-H3-DIALOG.md` dan referensi Ref2VA. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris; runtime tidak menerjemahkan prompt.
