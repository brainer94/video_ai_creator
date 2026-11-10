# Scene MiniMax H3 R2V

## Tujuan

Scene `minimax-h3_r2v` membuat video MiniMax H3 Reference-to-Video dengan reference media yang dipilih secara dinamis:

- maksimal 5 Picture;
- maksimal 3 Audio;
- maksimal 1 Video;
- minimal 1 reference dari salah satu kategori.

Reference yang tidak aktif harus dihapus dari JSON dan workflow. Nomor token dimulai dari 1 dan rapat. Urutan token mengikuti array `references.images` dan `references.audios`, bukan urutan abjad nama file.

## Prompt

Gunakan mode full-reference `Ref2VA` sesuai `MINIMAX-H3-R2V-PROMPT.md`. Prompt disimpan langsung dalam bahasa Inggris dan memiliki section runtime:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

Untuk authoring, `positive_prompt` memiliki `style_opening` dan `shots[]` dengan struktur yang sama seperti T2VA/I2VA. Aplikasi mengompilasi kartu shot menjadi `detailed_description` saat runtime; isi adegan tidak boleh ditulis ulang ketika hanya mengubah struktur. Jangan membuat key `id_new`, `id_old`, atau `en`.

Gunakan hanya token Picture, Audio, dan Video yang tercantum pada reference aktif. Token semantic seperti `<Subject 1>`, `<Shot 1>`, `<d>`, `</d>`, dan speaker ID tetap boleh digunakan. Audio harus dijelaskan sebagai `reference`, `fully_copy`, atau `partially_copy` sesuai kebutuhan.

## Struktur file

Scene menggunakan `minimax_h3_r2v_prompt.json`. MiniMax H3 R2V hanya memakai prompt positif; jangan menambahkan `negative_prompt` atau field scene yang tidak diperlukan.

## Input UI

- Tab `MINIMAX-H3_R2V` berisi ukuran, prompt positif, dan dropdown reference berurutan.
- Tab `Aset` mempertahankan urutan gambar dan audio yang sudah dipilih ketika daftar aset diperbarui.
- Tidak ada checkbox `Buat Image Awal` atau `Hapus Sound`.
- Prompt editor R2V dapat menambah/menghapus kartu shot; hasil simpan tetap mengikuti schema authoring di atas.

## Durasi dan validasi

- Durasi `0.0` sampai `15.0` detik dengan maksimal empat angka desimal.
- Minimal satu reference aktif wajib tersedia.
- Nomor token setiap kategori dimulai dari 1 dan berurutan.
- Keenam section Ref2VA tersedia setelah serialisasi.
- `shots[]` tidak kosong dan timeline berurutan.
- Tidak ada token media yang tidak tersedia.
- Tidak ada wrapper bahasa, `negative_prompt`, atau field tambahan yang tidak diperlukan.
