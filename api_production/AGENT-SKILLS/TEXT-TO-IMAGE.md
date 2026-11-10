# Petunjuk pembuatan text menjadi image

## Konfigurasi JSON

File konfigurasi: `z_image_prompt.json`.

Prompt disimpan langsung dalam bahasa Inggris pada `positive_prompt` dan `negative_prompt`:

```json
{
  "positive_prompt": "cinematic portrait of ...",
  "negative_prompt": "blurry, distorted anatomy"
}
```

Jangan membuat wrapper bahasa dan jangan mengubah setting lain yang tidak terkait prompt.

## Flow pembuatan image

Gambar dibuat menggunakan `positive_prompt` dan `negative_prompt`. Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan prompt Inggris; runtime tidak menerjemahkan prompt.
