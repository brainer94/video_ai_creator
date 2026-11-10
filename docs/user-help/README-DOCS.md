# Panduan Awal Video AI Creator

Selamat datang di Video AI Creator. Panduan ini muncul ketika aplikasi dibuka sebelum ada project yang aktif. Ikuti urutan di bawah ini untuk menyiapkan aplikasi dan membuat project pertama.

## Urutan singkat

1. Buka `Konfigurasi Umum` dan pastikan alamat ComfyUI dapat diakses.
2. Pastikan model yang diperlukan sudah tersedia.
3. Buat project baru.
4. Lengkapi pengaturan project dan adegan.
5. Simpan, lalu jalankan adegan yang dipilih.

## Konfigurasi Umum

`Konfigurasi Umum` mengatur koneksi ComfyUI serta model dan LoRA yang digunakan oleh semua project. Pengaturan ini bersifat global, sehingga tidak perlu diatur ulang di setiap project.

### Membuka Konfigurasi Umum

Tekan tombol bergambar roda gigi/mesin pada posisi paling kiri toolbar. Tombol ini selalu tersedia, meskipun belum ada project yang dibuka.

### URL ComfyUI

Isi `URL ComfyUI` dengan alamat ComfyUI yang dapat diakses dari komputer ini. Alamat dapat berupa `host:port` atau URL lengkap `http://` / `https://`.

Untuk URL tunnel, salin alamat lengkap yang diberikan oleh penyedia tunnel, termasuk token pada URL bila memang diperlukan.

Tekan `Simpan & Periksa` untuk menyimpan alamat dan menjalankan pemeriksaan. Aplikasi akan memeriksa secara berurutan:

1. apakah ComfyUI dapat dihubungi;
2. apakah ComfyUI-Model-Manager tersedia;
3. apakah kelompok model yang dipilih sudah lengkap;
4. apakah daftar LoRA dapat dibaca.

Hasil pemeriksaan ditampilkan melalui `Log Proses`. Jika ComfyUI-Model-Manager belum tersedia, aplikasi akan mencoba memasangnya, menunggu ComfyUI siap kembali, lalu melanjutkan pemeriksaan.

### Kelompok model

Pada bagian download model tersedia beberapa kelompok:

- `MiniMax H3` untuk mode normal;
- `MiniMax H3 Mode Cepat`;
- `Flux 2`;
- `Z Image Turbo`;
- `Qwen Image Edit`.

Centang satu atau beberapa kelompok, lalu tekan `Download Model`. Kelompok yang seluruh filenya sudah tersedia akan dicentang otomatis dan tidak dapat dipilih ulang. Jika baru sebagian file tersedia, kelompok tersebut tetap dianggap belum lengkap. File yang sudah ada akan dilewati.

Untuk LoRA, tekan `Download LoRA`, masukkan URL dari Hugging Face atau Civitai, pilih kategori tujuan, lalu jalankan download. Setelah selesai, daftar LoRA diperbarui.

Jika ComfyUI tidak dapat dihubungi, periksa alamat, token, dan status ComfyUI. Gunakan `Log Proses` untuk membaca urutan pemeriksaan dan pesan kesalahan.

## Fungsi tombol pada toolbar

Nama beberapa tombol ditampilkan melalui tooltip karena tombolnya menggunakan ikon. Arahkan mouse ke ikon untuk melihat keterangan singkat.

### Konfigurasi Umum

- `Konfigurasi Umum` — mengatur URL ComfyUI, menyiapkan kelompok model, dan mengunduh LoRA.

### Project

- `Project Baru` — membuat project baru dan menyiapkan satu adegan awal.
- `Buka Project` — membuka project yang sudah tersedia.
- `Tutup Project` — menutup project aktif dan kembali ke panduan awal.
- `Konfigurasi Project` — mengatur deskripsi project, ukuran video, model, suara, caption, dan cover.
- `Log Proses` — membuka atau menutup dialog yang menampilkan proses aplikasi dan pesan hasil pekerjaan.
- `Muat Ulang` — memuat ulang daftar adegan dan statusnya.

### Scene

- `Tambah Adegan` — menambahkan adegan baru di akhir daftar.
- `Sisipkan Adegan` — menambahkan adegan baru sebelum adegan yang sedang dipilih.
- `Gandakan Adegan` — menyalin adegan yang dipilih dan menaruh salinannya setelah adegan tersebut.
- `Hapus Adegan` — menghapus adegan yang dipilih.
- `Simpan Adegan` — menyimpan perubahan pada adegan yang sedang dibuka.
- `Upscale Video Adegan` — memperbesar video terakhir pada adegan aktif.

### Proses

- `Buat Gambar Awal` — membuat gambar awal untuk adegan yang mendukung gambar awal.
- `Jalankan Adegan` — menjalankan alur untuk adegan yang sedang dipilih.

### Audio

- `Buat Voice` — membuat audio suara berdasarkan teks suara pada adegan yang dipilih.

### Compose

- `2x` — menjalankan upscale 2x pada video output di setiap scene yang ditandai.
- `Gabungkan` — menggabungkan video dan audio dari semua adegan menjadi satu hasil.
- `Compose per Adegan` — membuat hasil video terpisah untuk setiap adegan dengan musik dan pengaturan ukuran.

### Batch

- `Jalankan Beberapa Adegan` — memilih beberapa adegan, kemudian menjalankannya secara berurutan.
- `Buat Voice Semua Adegan` — membuat voice untuk seluruh adegan dalam project.

### Backup

- `Backup` — menyimpan backup ZIP dari project aktif.

### Runtime

- `Log ComfyUI` — menampilkan 200 baris log ComfyUI terakhir melalui koneksi resmi ComfyUI dan memperbaruinya secara berkala.

### Bantuan

- `Bantuan` — membuka panduan sesuai tab yang sedang dipilih. Setiap tab dan dialog utama memiliki panduan pengguna sendiri.

## Membuat project pertama kali

1. Tekan tombol `Project Baru` pada grup `Project`.
2. Masukkan nama project, lalu konfirmasi.
3. Aplikasi membuat project dan satu adegan awal secara otomatis.
4. Buka `Konfigurasi Project` untuk mengisi deskripsi project dan memilih ukuran video, model, suara, caption, atau cover bila diperlukan.
5. Pada tab `Meta`, isi judul adegan, pilih tipe adegan, dan atur durasi sesuai kebutuhan.
6. Buka tab yang sesuai dengan tipe adegan, lalu isi prompt dan pilih aset referensi bila diperlukan.
7. Tekan `Simpan Adegan`.
8. Jika adegan menggunakan gambar awal, siapkan gambar melalui tab `Gambar Awal` atau tombol `Buat Gambar Awal`.
9. Tekan `Jalankan Adegan` untuk membuat video.
10. Pantau hasil dan pesan proses melalui `Log Proses`. Aset hasil dapat dilihat pada tab `Aset`.

Untuk menjalankan beberapa adegan sekaligus, tekan `Jalankan Beberapa Adegan` pada grup `Batch`, centang adegan yang diinginkan, lalu konfirmasi.

## Jika terjadi masalah

- Nama adegan berwarna merah berarti adegan belum memenuhi syarat untuk dijalankan. Arahkan mouse ke nama adegan untuk membaca masalahnya.
- Buka `Log Proses` untuk melihat langkah yang sedang berjalan dan pesan kesalahan.
- Buka `Log ComfyUI` untuk melihat log terbaru dari ComfyUI.
- Gunakan `Muat Ulang` setelah memperbaiki aset, konfigurasi, atau isi adegan.

## Panduan per tampilan

- [Meta](id/meta.md)
- [Gambar Awal](id/gambar_awal.md)
- [Prompt Tambahan](id/prompt_tambahan.md)
- [MiniMax H3 T2V](id/minimax_h3_t2v.md)
- [MiniMax H3 I2V](id/minimax_h3_i2v.md)
- [MiniMax H3 I2V-Panjang](id/minimax_h3_i2v_panjang.md)
- [MiniMax H3 R2V](id/minimax_h3_r2v.md)
- [MiniMax H3 R2V-Panjang](id/minimax_h3_r2v_panjang.md)
- [MiniMax H3 S2V](id/minimax_h3_s2v.md)
- [I2V](id/i2v.md)
- [Image Pan](id/image_pan.md)
- [Image Zoom](id/image_zoom.md)
- [Qwen Image Edit](id/qwen_image_edit.md)
- [Aset](id/aset.md)
- [Konfigurasi Project](id/konfigurasi_project.md)
- [Download LoRA](id/download_lora.md)
- [Log Proses](id/log_proses.md)
- [Log ComfyUI](id/log_comfyui.md)
- [Upscale Video](id/upscale_video.md)
