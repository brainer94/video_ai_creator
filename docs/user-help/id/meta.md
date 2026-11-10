# META

## Fungsi tampilan

Tab `Meta` berisi pengaturan dasar untuk adegan yang sedang dipilih. Di sinilah pengguna menentukan nama adegan, jenis video, durasi, dan pengaturan suara.

## Alur kerja singkat

1. Isi `Judul Adegan`.
2. Pilih `Tipe Adegan`.
3. Atur durasi jika tipe adegan menggunakan durasi manual.
4. Atur suara atau isi `Teks Suara` jika adegan membutuhkan voice-over.
5. Aktifkan `Upscale` bila hasil akhir ingin diperbesar.
6. Simpan adegan sebelum menjalankannya.

## Pengaturan dasar

### Judul Adegan

Nama yang ditampilkan pada daftar adegan di sisi kiri. Judul wajib diisi agar adegan mudah dikenali dan dapat dijalankan.

### Deskripsi Adegan

Catatan tentang isi adegan, misalnya siapa tokohnya, apa yang terjadi, atau suasana yang diinginkan.

Bagian ini boleh dikosongkan. Isinya membantu pengguna mengingat konteks adegan dan dapat membantu Gemini ketika pengguna meminta bantuan menyusun prompt, tetapi bukan syarat untuk menjalankan adegan.

### Tipe Adegan

Menentukan cara video dibuat. Pilihan yang tersedia meliputi:

- `minimax-h3_t2v` untuk video dari prompt teks;
- `minimax-h3_i2v` untuk video dari satu gambar awal;
- `minimax-h3_i2v-panjang` untuk video yang dapat terdiri dari beberapa proses berurutan;
- `minimax-h3_r2v` untuk video dari referensi gambar, audio, atau video;
- `minimax-h3_r2v-panjang` untuk beberapa proses R2V yang saling berurutan;
- `minimax-h3_s2v` untuk video dari gambar dan audio speech;
- `i2v` untuk menyusun video dari beberapa gambar secara berurutan;
- `image_pan` untuk gerakan mendatar pada satu gambar;
- `image_zoom` untuk gerakan memperbesar atau memperkecil satu gambar.

Setelah tipe diubah, buka tab yang sesuai dan periksa kembali pengaturannya.

### Durasi (detik)

Durasi mengikuti jenis adegan:

- semua adegan MiniMax H3 dapat diatur dari `0` sampai `15` detik dan dapat memakai angka desimal;
- `i2v`, `image_pan`, dan `image_zoom` memakai bilangan bulat dari `1` sampai `15` detik;
- `minimax-h3_s2v` mengikuti durasi audio speech, sehingga durasi tidak diatur secara manual pada tab ini.

Untuk adegan MiniMax H3, durasi pada `Meta` menjadi batas akhir alur bidikan yang ditulis pada editor prompt.

## Pengaturan suara

### Model Gemini TTS

Memilih model Gemini untuk membuat suara dari `Teks Suara`.

### Pilihan Suara Scene

Untuk model suara biasa, pilih salah satu profil yang tersedia:

- `Lily`;
- `Lily - Ngaji`;
- `Lily - Arab`.

Jika memilih `gemini-3.8-flash-tts`, pilihan berubah menjadi katalog suara Gemini. Pilih suara langsung dari daftar tersebut.

### Teks Suara

Teks yang akan dibacakan menjadi suara. Kosongkan bila adegan tidak membutuhkan voice-over.

Untuk `minimax-h3_s2v`, audio speech yang digunakan untuk video harus tersedia sebagai audio speech di adegan. Pastikan teks atau audio yang dipakai sesuai dengan tujuan adegan.

## Upscale

Aktifkan `Upscale` bila hasil adegan ingin diproses dengan pembesaran setelah video selesai dibuat. Pengaturan ini bersifat pilihan dan tidak diperlukan untuk menjalankan adegan biasa.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah mengubah judul, tipe, durasi, suara, atau pilihan upscale.

Sebelum menjalankan, pastikan:

- `Judul Adegan` sudah diisi;
- tipe adegan sudah benar;
- durasi sesuai aturan tipe adegan;
- pengaturan pada tab tipe adegan sudah diperiksa;
- ComfyUI dapat diakses melalui `Konfigurasi Umum`.

`Deskripsi Adegan` tidak perlu diisi bila memang tidak ada catatan tambahan.
