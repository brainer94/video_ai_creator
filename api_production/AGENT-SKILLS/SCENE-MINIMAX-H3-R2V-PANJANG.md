# Scene MiniMax H3 R2V-Panjang

## Tujuan

Scene `minimax-h3_r2v-panjang` membuat empat video MiniMax H3 R2V yang saling tersambung lalu menggabungkannya menjadi satu output.

- Proses 1 memakai reference global yang dipilih pengguna dan dapat memakai satu frame awal opsional.
- Proses 2, 3, dan 4 otomatis menambahkan frame terakhir proses sebelumnya sebagai `Picture` berikutnya.
- Reference image, audio, dan video yang dipilih pada UI berlaku global untuk semua proses.
- Setiap proses memiliki prompt Ref2VA sendiri.
- Jika dipilih, frame awal Proses 1 hanya berlaku untuk Proses 1 dan ditempatkan setelah seluruh reference image global.

## Struktur prompt

Scene menggunakan `minimax_h3_r2v_panjang_prompt.json` dengan empat item tetap pada `prompts[]`. Setiap item memakai authoring Ref2VA yang sama dengan R2V biasa:

- `mode: "R2VA"`
- `style_opening`
- enam section Ref2VA
- `shots[]` dengan bentuk item yang sama seperti T2VA dan I2VA

Field `continuations` menentukan jumlah proses aktif tambahan (`0` berarti hanya Proses 1). `run_start_stage` boleh dipakai untuk menjalankan ulang mulai dari proses tertentu, tetapi segment dan frame proses sebelumnya wajib sudah tersedia.

Jangan menambahkan `id_new`, `id_old`, `en`, wrapper translasi, atau format prompt lama. Jangan mengubah isi adegan ketika hanya menyelaraskan struktur prompt.

## Urutan reference

`references.images` menyimpan maksimal empat gambar global dalam urutan posisi UI. `references.initial_image` menyimpan satu frame awal opsional untuk Proses 1 dan tidak menjadi reference global. Runtime mengirim gambar global terlebih dahulu sebagai `Picture 1..N`, lalu mengirim `initial_image` pada Proses 1 atau frame carry pada proses 2-4 sebagai `Picture N+1`. Dengan demikian satu workflow R2V tetap berada dalam batas lima slot Picture.

`references.audios` maksimal tiga item dan `references.video` maksimal satu item. Token Audio dan Video juga mengikuti urutan array, bukan urutan abjad nama file.

Pada Proses 1 dengan `initial_image`, dan pada proses 2-4 dengan frame carry, Picture tambahan setelah reference global diperlakukan sebagai frame awal video. Jika ada `N` gambar global, gunakan token `<Picture N+1>`. Definisikan dengan pola Ref2VA seperti S2V:

```text
<Picture N+1> is the initial frame and visual reference for the entire video.
<Picture N+1> (initial frame and composition): fully_preserved - preserve the appearance, pose, lighting, background, and framing.
[Shot 1] The video begins exactly from <Picture N+1>.
```

Kalimat setelah pembuka disesuaikan dengan adegan. Prompt tidak perlu menjelaskan bahwa Picture tersebut berasal dari proses lain, dan tidak memakai object atau anchor first-frame I2VA.

Pada Proses 1 tanpa `initial_image`, jangan membuat kalimat pembuka yang menyatakan bahwa video dimulai tepat dari Picture tertentu.

Setiap Subject harus menyebutkan Picture sumbernya dan semua Picture tempat Subject tersebut muncul dalam satu kalimat lengkap, misalnya:
`<Subject 1> is the man in the tech armor from <Picture 1> and also appears in <Picture N+1>.`
Pada Proses 1 dengan `initial_image`, dan pada proses 2-4, ulangi pola tersebut untuk setiap Subject yang terlihat pada frame awal. ID Subject harus konsisten pada seluruh proses dan jangan membuat kalimat Subject duplikat terpisah.

## Input UI

Tab `MINIMAX-H3_R2V-PANJANG` mengikuti layout `MINIMAX-H3_I2V-PANJANG`:

- tab `Proses 1` sampai `Proses 4`;
- ukuran, LoRA, mode, sound, cache, reference global, dan frame awal opsional pada Proses 1;
- editor prompt dan instruksi `Buat Prompt` pada setiap proses; tombol pada Proses N dapat membuat prompt Proses 1 sampai N sekaligus dalam satu respons Gemini;
- jumlah lanjutan dan proses awal run pada Proses 1.

Frame awal Proses 1 dipilih secara opsional pada Proses 1. Frame carry tidak dipilih manual dan tidak disimpan sebagai reference global. UI menampilkan frame awal atau frame carry sebagai reference tambahan pada editor proses yang relevan.

## Validasi

- durasi scene berada pada rentang `0.0`-`15.0` detik;
- minimal satu reference image, audio, video, atau frame awal Proses 1 aktif;
- empat item `prompts[]` selalu tersedia;
- prompt pada proses yang dijalankan harus memiliki enam section Ref2VA yang valid;
- token Picture, Audio, dan Video harus sesuai manifest proses;
- proses lanjutan hanya boleh memakai segment dan frame proses sebelumnya yang benar-benar ada.
