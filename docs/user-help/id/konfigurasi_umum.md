# KONFIGURASI UMUM

## Fungsi tampilan

`Konfigurasi Umum` adalah tempat untuk mengatur koneksi ComfyUI dan menyiapkan model serta LoRA yang digunakan project. Pengaturan ini bersifat global dan berlaku untuk semua project.

Tombolnya selalu tersedia pada toolbar utama. Tidak ada lagi alamat ComfyUI terpisah untuk setiap project.

## Alur kerja singkat

1. Buka `Konfigurasi Umum` dari tombol konfigurasi pada toolbar.
2. Isi `URL ComfyUI`.
3. Tekan `Simpan & Periksa`.
4. Ikuti langkah pemeriksaan pada area status.
5. Unduh kelompok model yang belum lengkap bila diperlukan.
6. Buka `Download LoRA` bila ingin menambahkan LoRA.

## URL ComfyUI

Isi alamat ComfyUI yang sedang berjalan dan dapat diakses dari komputer ini. Alamat dapat berupa `host:port` atau URL `http://` / `https://`.

Untuk URL tunnel, salin alamat lengkap yang diberikan oleh penyedia tunnel, termasuk token pada URL bila memang diperlukan.

## Pemeriksaan otomatis

Setelah dialog dibuka, aplikasi memeriksa beberapa hal secara berurutan:

1. apakah ComfyUI dapat dihubungi;
2. apakah ComfyUI-Model-Manager tersedia;
3. apakah kelompok model yang dipilih sudah lengkap;
4. apakah daftar LoRA dapat dibaca.

Hasilnya ditampilkan pada area status. Bila ComfyUI-Model-Manager belum tersedia, aplikasi akan mencoba memasangnya, menunggu ComfyUI kembali siap, lalu melanjutkan pemeriksaan.

Jika URL diubah dan `Simpan & Periksa` ditekan, pemeriksaan yang sama dijalankan kembali untuk alamat baru.

## Kelompok Model

Centang satu atau beberapa kelompok yang ingin disiapkan, lalu tekan `Download Model`.

Kelompok yang tersedia:

- `MiniMax H3` untuk mode normal;
- `MiniMax H3 Mode Cepat`;
- `Flux 2`;
- `Z Image Turbo`;
- `Qwen Image Edit`.

Kelompok yang seluruh filenya sudah tersedia akan dicentang otomatis dan tidak dapat dipilih ulang. Jika baru sebagian file yang tersedia, kelompok tetap dianggap belum lengkap.

File yang sudah ada akan dilewati sehingga tidak perlu diunduh ulang.

## Download Model

Tekan `Download Model` setelah memilih kelompok yang belum lengkap. Pengunduhan dijalankan melalui ComfyUI-Model-Manager pada ComfyUI yang sudah dipilih.

Pantau area status sampai setiap model dinyatakan selesai atau gagal. Jika ComfyUI baru saja direstart, tunggu sampai pemeriksaan menyatakan ComfyUI siap sebelum mencoba lagi.

## Download LoRA

Tekan `Download LoRA` untuk membuka dialog pengunduhan LoRA. Dialog tersebut meminta URL LoRA, kategori tujuan, dan nama file. Panduan lengkapnya tersedia pada [Download LoRA](download_lora.md).

Setelah pengunduhan selesai, daftar LoRA diperbarui agar file dapat dipilih pada tab yang sesuai.

## Jika terjadi masalah

- Jika ComfyUI tidak dapat dihubungi, pastikan alamat dan token benar serta ComfyUI sedang berjalan.
- Jika model belum ditemukan, tunggu pemeriksaan selesai lalu ulangi pengunduhan untuk kelompok yang belum lengkap.
- Jika LoRA belum muncul, pastikan pengunduhan selesai kemudian buka kembali pilihan LoRA atau periksa ulang koneksi ComfyUI.
- Gunakan `Log Proses` untuk melihat urutan pemeriksaan dan hasil tindakannya.
