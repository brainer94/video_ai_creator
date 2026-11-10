# LOG PROSES

## Fungsi tampilan

`Log Proses` menampilkan urutan tindakan yang dilakukan aplikasi. Gunakan log ini untuk memahami apa yang sedang diperiksa, proses mana yang sedang berjalan, dan langkah mana yang gagal.

Log ini juga dipakai untuk menampilkan pemeriksaan otomatis saat aplikasi mulai digunakan dan saat URL ComfyUI diganti pada `Konfigurasi Umum`.

## Kapan dialog terbuka

Dialog dapat terbuka saat aplikasi menjalankan pemeriksaan awal atau setelah pengguna menyimpan URL ComfyUI baru. Dialog juga dapat dibuka kembali dari tombol log proses pada toolbar.

## Isi log

Pesan dapat berisi:

- pemeriksaan apakah ComfyUI dapat dihubungi;
- pemeriksaan ComfyUI-Model-Manager;
- pemeriksaan kelengkapan kelompok model;
- pemeriksaan daftar LoRA;
- pembuatan prompt dengan bantuan Gemini;
- pembuatan gambar, video, atau suara;
- penggabungan media;
- alasan suatu proses berhenti atau gagal.

Pemeriksaan koneksi ditampilkan bertahap agar mudah diketahui bagian mana yang sudah selesai dan bagian mana yang masih bermasalah.

## Cara menggunakan

1. Baca pesan dari atas ke bawah untuk memahami urutan kejadian.
2. Perhatikan pesan terakhir bila proses masih berjalan.
3. Jika ada pesan gagal, ikuti petunjuknya dan perbaiki hal yang disebutkan.
4. Jalankan kembali tindakan setelah masalah diperbaiki.

Gunakan `Log ComfyUI` bila membutuhkan detail yang berasal langsung dari ComfyUI, misalnya progres pembuatan video atau pesan dari proses di dalamnya.
