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

`shots[]` memakai struktur yang sama dengan T2VA dan I2VA. Semua field shot harus berisi string yang tidak kosong. Jika tidak ada dialog, gunakan `No dialogue.`; jika tidak ada suara diegetik, gunakan `No diegetic sound.`. Aplikasi mengompilasi `style_opening` dan kartu shot menjadi section runtime `detailed_description`; jangan menyimpan wrapper bahasa dan jangan menulis ulang isi adegan saat mengubah struktur.

Saat dikirim ke ComfyUI, setiap shot R2V diserialisasi dengan rentang waktu eksplisit:

```text
[Shot 1] From 0.00 to 1.00 seconds, ...
[Shot 2] From 1.00 to 3.00 seconds, ...
```

Parser tetap menerima format lama `[Shot N] At MM:SS.mmm, ...` agar project lama tetap dapat dimuat, tetapi prompt baru harus menggunakan rentang `From ... to ... seconds`.

Untuk scene `minimax-h3_r2v-panjang`, gunakan empat prompt authoring di
`minimax_h3_r2v_panjang_prompt.json`. Reference image global ditulis dalam
`references.images` dengan maksimal empat item. `references.initial_image`
bersifat opsional dan hanya digunakan sebagai Picture tambahan pada Proses 1;
field ini tidak menjadi reference global. Pada proses 2–4, runtime menambahkan
frame terakhir proses sebelumnya sebagai Picture tambahan setelah seluruh
reference global. Jangan menulis frame carry ke array reference global.

Struktur reference khusus R2V-Panjang adalah:

```json
{
  "images": [],
  "initial_image": "",
  "audios": [],
  "video": ""
}
```

Pada Proses 1 dengan `initial_image`, gunakan Picture terakhir sebagai frame
awal dan tulis tiga kalimat pembuka Ref2VA berikut, dengan `N` sebagai jumlah
reference image global:

```text
<Picture N+1> is the initial frame and visual reference for the entire video.
<Picture N+1> (initial frame and composition): fully_preserved - preserve the appearance, pose, lighting, background, and framing.
[Shot 1] The video begins exactly from <Picture N+1>.
```

Jika Proses 1 tidak memiliki `initial_image`, jangan menyatakan bahwa video
dimulai tepat dari Picture tertentu. Picture global tetap dapat dipakai sebagai
reference subject, gaya, komposisi, atau properti. Pada proses 2–4, gunakan
Picture tambahan yang berasal dari frame proses sebelumnya dengan pola pembuka
yang sama. Jangan menjelaskan asal frame tersebut kepada LLM dan jangan memakai
object atau anchor first-frame I2VA.

Pada Proses 1 dengan `initial_image`, dan pada proses 2-4, Picture tambahan
setelah reference global adalah frame awal video proses tersebut. Jika terdapat
`N` gambar global, Picture ini bernomor `N+1`. Ikuti pola Ref2VA S2V untuk
mendefinisikan perannya, bukan anchor atau object `reference` I2VA. Awali field
berikut dengan kalimat yang sesuai nomor Picture aktif:

```text
subject_definitions:
<Picture N+1> is the initial frame and visual reference for the entire video.

retention_analysis:
<Picture N+1> (initial frame and composition): fully_preserved - preserve the appearance, pose, lighting, background, and framing.

detailed_description:
[Shot 1] The video begins exactly from <Picture N+1>.
```

Lanjutkan kalimat tersebut dengan detail adegan yang sesuai. Jangan menjelaskan
asal Picture dari proses lain kepada LLM dan jangan menambahkan format I2VA.

## Reference aktif

Token harus dibuat dari manifest aktif dengan penomoran rapat: image `<Picture N>`, video `<Video 1>`, dan audio `<Audio N>`. Gunakan hanya token yang benar-benar tersedia. `<Subject N>`, `<Shot N>`, `<d>`, `</d>`, dan speaker ID adalah token semantik yang tetap boleh digunakan.

Pertahankan setiap token reference persis sama pada keenam section. Jangan mengarang, mengganti nama, atau melompati nomor token.

Setiap `Subject` harus dijelaskan sumber `Picture`-nya dan pada `Picture` mana
Subject tersebut muncul. Pada Proses 1 dengan `initial_image`, dan pada proses
2-4, gunakan satu kalimat lengkap dengan pola:
`<Subject N> is [description] from <Picture M> and also appears in <Picture K>.`
ID Subject harus tetap sama antarproses. Pada Proses 1 dengan `initial_image`,
`K` adalah Picture frame awal yang dipilih; pada proses 2-4, `K` adalah Picture
frame awal otomatis. Jangan menaruh `also appears` di dalam kurung sebelum `is`
dan jangan menambahkan kalimat Subject duplikat terpisah.

## Cara menulis enam section

- `subject_definitions`: identitas subjek dan hubungan dengan reference aktif.
- `summary`: ringkasan adegan, tujuan aksi, dan hubungan antar-reference.
- `retention_analysis`: detail reference yang harus dipertahankan.
- `style_opening`: gaya visual global sebelum shot pertama, bila diperlukan.
- `shots[]`: timeline visual, aksi, kamera, dialog, suara, dan penggunaan reference.
- `overall_soundscape`: ambience, suara fisik, suara manusia non-verbal, dan audio reference.
- `non_diegetic_music`: musik latar atau `N/A`.

Teks dialog dan lirik lengkap hanya ditulis pada field dialog shot sesuai aturan `MINIMAX-H3-DIALOG.md` dan referensi Ref2VA. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris; runtime tidak menerjemahkan prompt. Pada R2V-Panjang, tombol pada Proses N menghasilkan array prompt untuk Proses 1 sampai N dalam satu respons, lalu aplikasi memvalidasi dan menyimpan seluruh hasil secara atomik.
