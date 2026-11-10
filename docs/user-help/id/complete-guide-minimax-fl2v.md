# Panduan Lengkap MiniMax H3 FL2V

## Fungsi FL2VA

FL2VA (`First-and-Last-Frame-to-Video-Audio`) menggunakan dua gambar sebagai batas visual video:

- `<Picture 1>` adalah keadaan pada frame pertama;
- `<Picture 2>` adalah keadaan pada frame terakhir.

Prompt harus menjelaskan jalur perubahan yang masuk akal dari gambar pertama menuju gambar terakhir. Fokusnya bukan mengulang dua gambar secara terpisah, melainkan menjelaskan gerakan, perubahan pose, perpindahan objek, perubahan komposisi, dan transisi pencahayaan yang menghubungkan keduanya.

Gunakan [Panduan Bersama Penulisan Prompt MiniMax H3](complete-guide-minimax-shared.md) untuk aturan shot, kamera, dialog, suara, dan musik.

## Instruksi alignment first frame dan last frame

Prompt FL2VA harus diawali dengan instruksi berikut:

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

Keterangan:

- `Picture 1` harus menjadi frame pertama dan berasal dari `[Shot 1]`;
- `Picture 2` harus menjadi frame terakhir dan berasal dari shot terakhir yang sebenarnya;
- `N` adalah nomor shot terakhir yang digunakan;
- `S.SS` adalah durasi efektif video dan harus ditulis dengan tepat dua angka desimal.

Instruksi alignment menjadi baris pertama prompt, kemudian diikuti satu baris kosong sebelum tiga bagian utama prompt.

## Cara menulis jalur dari awal ke akhir

Gunakan urutan berikut:

1. Mulai dari posisi, komposisi, dan keadaan visual pada `<Picture 1>`.
2. Jelaskan aksi yang memulai perubahan.
3. Jelaskan perubahan yang terlihat secara bertahap di antara kedua gambar.
4. Tunjukkan bagaimana pose, objek, kamera, ruang, dan pencahayaan bergerak menuju keadaan akhir.
5. Pastikan keadaan pada `<Picture 2>` tercapai di akhir shot terakhir.

Struktur yang disarankan adalah:

```text
first-frame state → observable intermediate changes → progressively narrowing differences → last-frame state
```

FL2VA umumnya lebih baik menggunakan satu shot agar model dapat melakukan interpolasi kontinu dari gambar awal ke gambar akhir. Gunakan beberapa shot hanya jika memang dibutuhkan atau diminta secara eksplisit. Jika menggunakan beberapa shot, gambar akhir harus dicapai pada `[Shot N]` terakhir.

Jangan hanya menuliskan:

```text
The video changes from Picture 1 to Picture 2.
```

Tuliskan proses perubahannya secara konkret, misalnya subjek bergerak, benda dipindahkan, kamera berputar, pintu terbuka, atau pencahayaan berubah secara bertahap.

## Contoh FL2VA

Contoh berikut menggunakan satu shot berdurasi delapan detik. Prompt akhir tetap berbahasa Inggris karena mengikuti kontrak MiniMax H3.

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a rain-soaked cyclist begins in the position and framing established by Picture 1, holding a closed black umbrella beside a silver bicycle. The camera pulls out with small amplitude at slow speed as she releases the bicycle handle, raises the umbrella above her shoulder, and presses the runner upward until the canopy opens. Water rolls from the expanding fabric while she steps beneath it, rotates the handle into the final angle, and settles into the pose, spacing, and composition established by Picture 2 at the end of the shot.

overall_soundscape: Rain falls steadily on the pavement, followed by the metallic click of the umbrella runner and the soft snap of the canopy opening. Water drips from the bicycle frame as distant traffic passes.

non_diegetic_music: N/A
```

## Hal yang perlu dihindari

- Jangan menempatkan `Picture 1` dan `Picture 2` sebagai dua deskripsi statis tanpa jalur perubahan.
- Jangan membuat perubahan yang tidak mungkin menjembatani keadaan awal dan akhir.
- Jangan mencapai keadaan akhir sebelum shot terakhir selesai.
- Jangan menambahkan last-frame instruction jika hanya tersedia gambar awal; gunakan panduan I2VA.
- Jangan menggunakan instruksi L2VA, karena L2VA hanya memiliki gambar tujuan pada akhir video.
- Jangan mengubah isi teks atau dialog yang diberikan pengguna.

## Checklist FL2VA

- `Picture 1` dipetakan ke `0.00` detik dan `[Shot 1]`.
- `Picture 2` dipetakan ke durasi akhir video dan shot terakhir.
- Durasi alignment ditulis dengan dua angka desimal.
- Jalur perubahan dari awal ke akhir dijelaskan secara konkret.
- Gerakan kamera membantu menjembatani kedua keadaan visual.
- Satu shot digunakan bila interpolasi kontinu lebih tepat.
- Jika ada beberapa shot, shot terakhir benar-benar mendarat pada keadaan `Picture 2`.
- Tiga bagian utama dan semua aturan umum mengikuti [panduan bersama](complete-guide-minimax-shared.md).
