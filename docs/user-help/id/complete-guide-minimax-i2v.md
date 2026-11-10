# Panduan Lengkap MiniMax H3 I2V

## Fungsi I2VA

I2VA (`Image-to-Video-Audio`) menggunakan satu gambar sebagai frame pertama video, lalu mengembangkan gerakan dan kejadian dari kondisi visual tersebut. Gambar referensi bukan sekadar inspirasi gaya; gambar tersebut menjadi keadaan nyata pada awal video.

Gunakan [Panduan Bersama Penulisan Prompt MiniMax H3](complete-guide-minimax-shared.md) untuk aturan shot, kamera, dialog, suara, dan musik.

## Instruksi first frame

Prompt I2VA harus diawali dengan kalimat alignment berikut:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

Kalimat tersebut harus menjadi baris pertama prompt, kemudian diikuti satu baris kosong sebelum tiga bagian utama prompt.

Maknanya:

- `<Picture 1>` adalah gambar yang benar-benar digunakan sebagai input first frame;
- gambar tersebut dipetakan ke `[Shot 1]`;
- gambar tersebut menjadi kondisi visual pada `0.00` detik;
- keadaan subjek, komposisi, dan lingkungan pada gambar harus menjadi dasar perkembangan video.

Jangan mengganti kalimat alignment dengan deskripsi umum seperti “sebuah gambar digunakan sebagai referensi”. Model perlu menerima hubungan yang jelas antara gambar, shot, dan waktu.

## Cara mengembangkan video dari gambar awal

Gunakan urutan berikut:

1. Mulai dengan komposisi, gaya, subjek, pakaian, warna, objek penting, pencahayaan, dan hubungan ruang yang terlihat pada `<Picture 1>`.
2. Tegaskan bahwa subjek tetap memiliki identitas dan penampilan yang sama.
3. Jelaskan aksi pertama yang dimulai setelah frame awal.
4. Kembangkan gerakan secara kontinu menuju akhir video.
5. Pertahankan elemen penting dari gambar awal kecuali pengguna memang meminta perubahan.
6. Jelaskan perubahan pose, ekspresi, objek, atau kamera secara bertahap.
7. Gunakan `overall_soundscape` dan `non_diegetic_music` untuk melengkapi timeline audiovisual.

Struktur yang disarankan adalah:

```text
first-frame anchor → action onset → continuous development → result or reaction
```

Hindari menulis ulang gambar awal sebagai dua kondisi yang tidak berhubungan. Jelaskan bagaimana keadaan yang terlihat pada gambar berkembang menjadi aksi berikutnya.

## Contoh I2VA

Contoh berikut menggunakan prompt akhir berbahasa Inggris karena itulah bahasa yang digunakan dalam kontrak MiniMax H3.

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, the young woman shown in <Picture 1> remains beside the rain-covered train window, preserving her appearance, clothing, seat position, and the carriage layout. The camera trucks right with small amplitude at slow speed as she lifts her gaze from the folded letter toward the passing city lights. Her reflection moves across the glass while the quiet, breathy young woman (S1) says: <d>[English] I get off at the next station.</d> She folds the letter along its existing crease.

overall_soundscape: The train wheels produce a steady metallic rhythm beneath a low ventilation hum. Rain ticks against the window while paper rustles softly in her hands.

non_diegetic_music: Sustained cello notes at a slow tempo with widely spaced piano tones, gradually decreasing in volume.
```

## Menjaga kontinuitas gambar awal

Periksa kesinambungan berikut saat menulis prompt:

- wajah, bentuk tubuh, pakaian, dan aksesori;
- posisi subjek terhadap kamera dan lingkungan;
- warna, pencahayaan, dan arah bayangan;
- posisi objek penting dan hubungan antarobjek;
- gaya visual dan tingkat realisme;
- arah gerak yang dimulai dari pose pada gambar awal.

Jika kamera bergerak, jelaskan bagaimana komposisi berubah tanpa membuat subjek tiba-tiba berpindah atau berubah bentuk. Jika subjek berjalan, mengangkat benda, atau berinteraksi dengan objek, tuliskan titik awal dan perkembangan aksinya.

## Hal yang perlu dihindari

- Jangan memakai instruksi T2VA tanpa kalimat first frame.
- Jangan menempatkan `<Picture 1>` pada shot selain `[Shot 1]` sebagai first-frame anchor.
- Jangan membuat model memulai dari keadaan yang berbeda dengan gambar referensi.
- Jangan mengubah pakaian, identitas, warna, atau properti penting tanpa alasan dari prompt.
- Jangan memakai format FL2VA atau L2VA jika hanya tersedia gambar awal.
- Jangan menambahkan `negative_prompt` ke prompt I2VA.

## Checklist I2VA

- Kalimat alignment first frame berada di baris pertama.
- `<Picture 1>` dipetakan ke `[Shot 1]` pada `0.00` detik.
- Shot pertama menjelaskan keadaan yang benar-benar terlihat pada gambar.
- Aksi berkembang secara kontinu dari gambar awal.
- Identitas subjek, pakaian, warna, objek, dan komposisi tetap konsisten.
- Timeline shot, soundscape, dan musik mengikuti aturan panduan bersama.
- Prompt akhir ditulis dalam bahasa Inggris, sementara dialog atau teks layar dipertahankan sesuai sumbernya.
