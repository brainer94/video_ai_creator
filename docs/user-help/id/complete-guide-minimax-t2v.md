# Panduan Lengkap MiniMax H3 T2V

## Fungsi T2VA

T2VA (`Text-to-Video-Audio`) membuat keseluruhan timeline audiovisual hanya dari deskripsi teks. Karena tidak ada gambar alignment, prompt harus membangun gaya, komposisi, subjek, aksi, kamera, dialog, dan suara dari awal.

Gunakan [Panduan Bersama Penulisan Prompt MiniMax H3](complete-guide-minimax-shared.md) untuk aturan shot, kamera, dialog, suara, dan musik.

## Struktur khusus T2VA

T2VA tidak menggunakan instruksi alignment gambar. Prompt langsung dimulai dengan tiga bagian utama berikut:

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

Urutan tersebut harus dipertahankan. Jangan menambahkan:

- instruksi first frame;
- instruksi last frame;
- field `reference`;
- alignment `<Picture N>` yang tidak memiliki gambar referensi;
- `negative_prompt` sebagai bagian dari prompt T2VA.

## Cara membangun timeline dari teks

1. Tentukan gaya visual dan komposisi pembuka.
2. Perkenalkan subjek, lingkungan, properti, dan posisi awalnya.
3. Susun aksi berdasarkan urutan waktu.
4. Tambahkan gerakan kamera yang membantu penonton memahami aksi.
5. Tempatkan dialog, singing, voiceover, dan suara diegetik pada shot yang sesuai.
6. Gunakan cut hanya ketika shot baru memberikan informasi penting.
7. Akhiri dengan hasil, reaksi, atau keadaan akhir yang jelas.
8. Lengkapi `overall_soundscape` dan `non_diegetic_music` setelah timeline utama selesai.

T2VA boleh menambahkan detail visual dan suara yang tidak ditulis secara eksplisit oleh pengguna selama detail tersebut tetap konsisten dengan maksud utama. Jangan menambahkan elemen yang mengubah subjek, lokasi, atau kejadian utama.

## Contoh T2VA

Contoh berikut menggunakan prompt akhir berbahasa Inggris karena itulah bahasa yang digunakan dalam kontrak MiniMax H3.

```text
integrated_multimodal_description: [Shot 1] From 0.00 to 5.00 seconds, live-action, cinematic, a medium-wide shot frames a baker opening the shutters of a small street bakery before sunrise. The camera pushes in with small amplitude at slow speed as the middle-aged baker with a calm, slightly raspy voice (S1) places a fresh loaf on the wooden counter and says: <d>[English] First batch of the morning.</d> [Shot 2] From 5.00 to 7.00 seconds, the camera cuts to a close-up of steam rising from the sliced bread while the baker's final words carry over from the previous shot.

overall_soundscape: Wooden shutters scrape open over a quiet street as trays clink softly inside the bakery. The doorbell rings once, followed by light footsteps and the crisp sound of bread being sliced.

non_diegetic_music: A soft acoustic-guitar pattern at a moderate tempo, joined by sparse upright-bass notes and a gentle fade at the end.
```

## Hal yang perlu diperhatikan

- Shot pertama harus memberi gambaran yang cukup tentang gaya dan komposisi awal.
- Perubahan keadaan subjek harus dijelaskan sebagai aksi, bukan hanya hasil akhir.
- Gerakan kamera harus berhubungan dengan subjek atau informasi yang ingin ditampilkan.
- Dialog harus berada di timeline yang tepat.
- Suara fisik yang penting dapat ditulis pada `diegetic_sound` shot dan dirangkum kembali secara umum pada `overall_soundscape` tanpa mengulang dialog.
- Jika tidak ada musik latar, gunakan `N/A` pada `non_diegetic_music`.

## Checklist T2VA

- Tidak ada gambar referensi yang digunakan sebagai alignment.
- Timeline dibangun sepenuhnya dari teks.
- `[Shot 1]` dimulai dari `0.00` detik.
- Semua shot berakhir sesuai durasi video.
- Prompt memakai tiga bagian utama dalam urutan yang benar.
- Dialog, suara diegetik, ambience, dan musik ditempatkan pada bagian yang tepat.
- Prompt akhir ditulis dalam bahasa Inggris, sementara isi dialog atau teks layar dipertahankan sesuai sumbernya.
