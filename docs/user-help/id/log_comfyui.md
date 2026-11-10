# LOG COMFYUI

## Fungsi tampilan

`Log ComfyUI` menampilkan baris log terbaru yang diberikan oleh ComfyUI. Gunakan dialog ini untuk memantau progres pembuatan media dan melihat pesan yang berasal langsung dari ComfyUI.

## Isi log

Dialog menampilkan paling banyak `200` baris terakhir agar tetap ringan. Isinya dapat mencakup:

- nama proses yang sedang dikerjakan;
- progres langkah pembuatan video atau gambar;
- pesan pemuatan dan pelepasan model;
- peringatan dari ComfyUI;
- pesan kesalahan dari proses pembuatan media.

Jika ComfyUI menampilkan progres langkah, progres tersebut terlihat sebagai baris kemajuan yang terus diperbarui. Nama proses ditampilkan dengan istilah yang lebih mudah dibaca bila informasinya tersedia.

## Pembaruan otomatis

Log diperbarui secara berkala selama dialog terbuka. Saat proses scene sedang berjalan, buka dialog ini untuk melihat perkembangan terbaru.

Jika koneksi log belum tersedia, proses scene tetap dapat berjalan dan dialog akan mencoba mengambil log terbaru dari ComfyUI pada pembaruan berikutnya.

## Cara menggunakan

1. Pastikan ComfyUI dapat diakses melalui `Konfigurasi Umum`.
2. Jalankan adegan atau proses yang ingin dipantau.
3. Buka `Log ComfyUI` dari toolbar.
4. Amati baris progres dan pesan terakhir.
5. Jika muncul pesan kesalahan, simpan keterangannya sebelum mencoba kembali.

## Perbedaan dengan Log Proses

Gunakan `Log Proses` untuk melihat apa yang dilakukan aplikasi, seperti pemeriksaan koneksi, pembuatan prompt, atau antrean download.

Gunakan `Log ComfyUI` untuk melihat kegiatan yang berlangsung di ComfyUI, terutama progres pembuatan media dan pesan dari proses tersebut.
