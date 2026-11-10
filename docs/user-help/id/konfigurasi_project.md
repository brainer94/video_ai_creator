# KONFIGURASI PROJECT

## Fungsi tampilan

Dialog `Konfigurasi Project` berisi pengaturan yang dipakai bersama oleh semua adegan dalam satu project. Pengaturan ini tidak mengubah project lain.

Alamat ComfyUI tidak diatur di sini. Gunakan `Konfigurasi Umum` untuk koneksi ComfyUI dan pengelolaan model.

## Alur kerja singkat

1. Isi `Deskripsi Project`.
2. Pilih `Ukuran Video Project`.
3. Pilih `Model Prompt Generation` bila ingin menggunakan bantuan Gemini.
4. Atur pembuatan caption bila diperlukan.
5. Atur cover project bila ingin membuat gambar cover.
6. Tekan `Generate Cover` bila ingin langsung membuat cover.
7. Tekan `OK` untuk menyimpan.

## Pengaturan project

### Deskripsi Project

Tulis gambaran umum project, misalnya tema, tokoh, gaya visual, atau tujuan video. Deskripsi project wajib diisi.

### Ukuran Video Project

Menentukan ukuran umum yang digunakan oleh project. Pilih ukuran yang sesuai dengan orientasi video.

Pengaturan ukuran khusus pada adegan tertentu dapat tetap berlaku sesuai tab adegan tersebut.

### Model Prompt Generation

Memilih model Gemini yang digunakan ketika pengguna menekan `Buat Prompt`. Pengaturan ini hanya menentukan model bantuan penyusun prompt; prompt tetap dapat ditulis langsung pada editor.

### Caption Project

Aktifkan `Aktifkan Generate Caption otomatis` bila ingin aplikasi membuat caption otomatis ketika alur pembuatan caption dijalankan.

## Konfigurasi cover

Bagian cover digunakan untuk membuat gambar sampul project.

### Model Cover dan Model Gemini Cover

Pilih model gambar yang digunakan. Bila model Gemini dipilih, pilih juga `Model Gemini Cover`.

### Ukuran Cover

Ukuran cover mengikuti ukuran video project dan tidak diubah secara terpisah.

### Random Seed dan Seed Statik Cover

Dengan `Random Seed`, hasil cover dapat berbeda pada setiap proses. Untuk mencoba kembali hasil yang sama, matikan pilihan tersebut lalu isi `Seed Statik Cover` dengan angka positif.

### Pakai Lora Cover

Aktifkan bila cover ingin menggunakan LoRA. Pilih `Nama Lora Cover` dan atur `Kekuatan Lora` bila tersedia.

### Prompt Positif Cover dan Prompt Negatif Cover

Jelaskan gambar cover yang diinginkan pada `Prompt Positif Cover`. Gunakan `Prompt Negatif Cover` untuk menuliskan hal-hal yang ingin dihindari bila model yang dipilih mendukungnya.

### Generate Cover

Tekan `Generate Cover` untuk membuat cover berdasarkan pengaturan yang sedang terlihat. Simpan pengaturan project setelah selesai mengubahnya.

## Catatan

Deskripsi project dan model prompt wajib tersedia agar pengaturan dapat disimpan. Pengaturan cover hanya diperlukan bila project membutuhkan gambar cover.
