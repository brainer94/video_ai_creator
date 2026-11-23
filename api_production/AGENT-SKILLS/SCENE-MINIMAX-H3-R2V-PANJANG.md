# Scene MiniMax H3 R2V-Panjang

## Tujuan

Scene `minimax-h3_r2v-panjang` membuat empat video MiniMax H3 R2V yang saling tersambung lalu menggabungkannya menjadi satu output.

- Setiap proses dapat memakai frame awal dan frame akhir opsional dari aset scene.
- Jika frame awal Proses 2, 3, atau 4 bersumber dari `none`, runtime otomatis menambahkan frame terakhir proses sebelumnya sebagai `Picture` berikutnya.
- Reference image, audio, dan video yang dipilih pada UI berlaku global untuk semua proses.
- Setiap proses memiliki prompt Ref2VA sendiri.
- Frame awal dan frame akhir yang dipilih hanya berlaku pada proses masing-masing dan ditempatkan setelah seluruh reference image global.

## Struktur prompt

Scene menggunakan `minimax_h3_r2v_panjang_prompt.json` dengan empat item tetap pada `prompts[]`. Setiap item memakai authoring Ref2VA yang sama dengan R2V biasa:

- `mode: "R2VA"`
- `style_opening`
- enam section Ref2VA
- `shots[]` dengan bentuk item yang sama seperti T2VA dan I2VA

Field `continuations` menentukan jumlah proses aktif tambahan (`0` berarti hanya Proses 1). `run_start_stage` boleh dipakai untuk menjalankan ulang mulai dari proses tertentu, tetapi segment dan frame proses sebelumnya wajib sudah tersedia.

Jangan menambahkan `id_new`, `id_old`, `en`, wrapper translasi, atau format prompt lama. Jangan mengubah isi adegan ketika hanya menyelaraskan struktur prompt.

## Urutan reference

`references.images` menyimpan maksimal enam gambar global dalam urutan posisi UI. `stage_references` menyimpan empat item `{first, last}` untuk frame setiap proses. Runtime mengirim gambar global terlebih dahulu sebagai `Picture 1..N`, lalu frame awal (terpilih atau otomatis) dan frame akhir terpilih sesuai urutan tersebut. Dengan demikian satu workflow R2V tetap berada dalam batas tujuh slot Picture; jumlah gambar global harus dikurangi bila sebuah proses memakai dua frame terpilih.

`references.audios` maksimal tiga item dan `references.video` maksimal satu item. Token Audio dan Video juga mengikuti urutan array, bukan urutan abjad nama file.

Jika frame awal terpilih atau otomatis tersedia, Picture tambahan setelah reference global diperlakukan sebagai frame awal video. Jika ada `N` gambar global, gunakan token `<Picture N+1>`. Jika frame akhir juga dipilih, gunakan Picture berikutnya sebagai frame akhir dan arahkan shot terakhir untuk berakhir tepat pada Picture tersebut. Definisikan dengan pola Ref2VA seperti S2V:

```text
<Picture N+1> is the initial frame and visual reference for the entire video.
<Picture N+1> (initial frame and composition): fully_preserved - preserve the appearance, pose, lighting, background, and framing.
[Shot 1] The video begins exactly from <Picture N+1>.
```

Kalimat setelah pembuka disesuaikan dengan adegan. Prompt tidak perlu menjelaskan bahwa Picture tersebut berasal dari proses lain, dan tidak memakai object atau anchor first-frame I2VA.

Jika tidak ada frame awal pada Proses 1, jangan membuat kalimat pembuka yang menyatakan bahwa video dimulai tepat dari Picture tertentu. Jika tidak ada frame akhir, jangan menambahkan pernyataan bahwa video harus berakhir pada Picture tertentu.

Setiap Subject harus menyebutkan Picture sumbernya dan semua Picture tempat Subject tersebut muncul dalam satu kalimat lengkap, misalnya:
`<Subject 1> is the man in the tech armor from <Picture 1> and also appears in <Picture N+1>.`
Jika proses memiliki frame awal, ulangi pola tersebut untuk setiap Subject yang terlihat pada frame awal. ID Subject harus konsisten pada seluruh proses dan jangan membuat kalimat Subject duplikat terpisah.

Frame awal dan frame akhir tetap merupakan reference Picture biasa. Keduanya dapat dipakai pada `subject_definitions`, `retention_analysis`, dan visual shot untuk menjelaskan subjek, komposisi, detail visual, dan kesinambungan. Peran tambahannya adalah sebagai anchor pembuka dan target akhir; shot pertama harus dimulai dari frame awal aktif, sedangkan shot terakhir harus mencapai frame akhir aktif.

## Input UI

Tab `MINIMAX-H3_R2V-PANJANG` mengikuti layout `MINIMAX-H3_I2V-PANJANG`:

- tab `Proses 1` sampai `Proses 4`;
- ukuran, LoRA, mode, sound, cache, reference global, serta frame awal dan frame akhir opsional pada setiap proses;
- editor prompt dan instruksi `Buat Prompt` pada setiap proses; tombol pada Proses N dapat membuat prompt Proses 1 sampai N sekaligus dalam satu respons Gemini;
- jumlah lanjutan dan proses awal run pada Proses 1.

Frame awal dan frame akhir setiap proses dipilih secara opsional dari aset scene. Jika frame awal proses lanjutan tidak dipilih, frame carry tidak dipilih manual dan tidak disimpan sebagai reference global; runtime mengambil frame terakhir proses sebelumnya sebagai reference tambahan.

## Validasi

- durasi scene berada pada rentang `0.0`-`15.0` detik;
- minimal satu reference image, audio, video, atau frame proses aktif;
- jumlah gambar global ditambah frame awal/akhir pada setiap proses tidak boleh melebihi tujuh;
- empat item `prompts[]` selalu tersedia;
- prompt pada proses yang dijalankan harus memiliki enam section Ref2VA yang valid;
- token Picture, Audio, dan Video harus sesuai manifest proses;
- proses lanjutan hanya boleh memakai segment dan frame proses sebelumnya yang benar-benar ada.
