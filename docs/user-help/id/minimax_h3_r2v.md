# MINIMAX-H3_R2V

## Fungsi tampilan

Tab `MINIMAX-H3_R2V` digunakan untuk membuat video berdasarkan satu atau beberapa referensi:

- Gambar
- Audio
- Video

Referensi tersebut membantu MiniMax H3 mempertahankan identitas subjek, gaya visual, suara, atau unsur lain dari bahan yang dipilih.

Susun prompt melalui editor interaktif. Jika membutuhkan bantuan Gemini, isi `Perintah kepada LLM`, lalu tekan `Buat Prompt`.

## Alur kerja singkat

Urutan penggunaan yang disarankan:

1. Pilih tipe adegan `minimax-h3_r2v` pada tab `Meta`.
2. Atur durasi dan judul adegan pada tab `Meta`.
3. Buka tab `MINIMAX-H3_R2V`.
4. Pilih referensi gambar, audio, dan video jika diperlukan.
5. Periksa urutan referensi.
6. Susun prompt melalui editor interaktif.
7. Isi pengaturan ukuran, LoRA, mode, dan jumlah step.
8. Simpan adegan.
9. Jalankan adegan melalui tombol proses.

Gemini membantu menyusun prompt berdasarkan informasi adegan, referensi, dan perintah yang diberikan.

## Bagian 1 — Pengaturan video

### Ukuran

Menentukan ukuran video keluaran. Pilih ukuran yang sesuai dengan orientasi dan kebutuhan project.

### Pakai Lora

Centang `Pakai Lora` bila ingin menggunakan LoRA pada video. Jika tidak dicentang, LoRA 1 dan LoRA 2 dilewati sehingga video dibuat tanpa LoRA.

### LoRA

Pilih LoRA pertama jika ingin menambahkan gaya atau karakter tertentu.

### Kekuatan

Menentukan seberapa kuat LoRA pertama memengaruhi hasil video.

### LoRA 2 dan Kekuatan 2

LoRA kedua bersifat opsional. Gunakan bila membutuhkan kombinasi dua LoRA.

Gunakan checkbox `Pakai Lora` untuk menentukan apakah kedua LoRA digunakan. Jika checkbox tidak dicentang, pilihan LoRA dan kekuatannya tidak diterapkan.

### Mode Cepat

Menggunakan pengaturan pemrosesan MiniMax H3 yang lebih cepat.

## Bagian 2 — Referensi

### Referensi gambar

Tersedia hingga lima slot `Picture`.

Setiap slot dapat diisi dengan satu file gambar dari aset adegan. Tidak semua slot harus diisi.

### Referensi audio

Tersedia hingga tiga slot `Audio`.

Audio dapat digunakan untuk memberikan karakter suara, ucapan, atau unsur audio lain yang perlu dipertahankan oleh model.

### Referensi video

Dapat dipilih paling banyak satu video.

Video dapat menjadi referensi gerakan, komposisi, atau alur visual.

### Cara menentukan urutan referensi

Urutan slot menentukan nomor referensi yang digunakan di prompt:

```text
Picture 1 → <Picture 1>
Picture 2 → <Picture 2>
Picture 3 → <Picture 3>

Audio 1 → <Audio 1>
Audio 2 → <Audio 2>
Audio 3 → <Audio 3>

Video 1 → <Video 1>
```

Daftar pilihan file dapat terlihat berurutan abjad, tetapi nomor referensi mengikuti urutan slot yang dipilih pengguna.

Gunakan tombol panah atas dan bawah di samping slot untuk mengubah urutan. Contoh:

```text
Sebelum:
Picture 1 → wanita.png
Picture 2 → rumah.png

Sesudah dipindahkan ke atas:
Picture 1 → rumah.png
Picture 2 → wanita.png
```

Urutan tersebut digunakan secara konsisten ketika prompt dan video dibuat:

- `<Picture N>`, `<Audio N>`, dan `<Video 1>` digunakan dalam prompt;
- referensi digunakan oleh proses pembuatan video.

### Jumlah referensi minimum

Setidaknya satu referensi harus dipilih. Referensi tersebut dapat berupa salah satu dari:

- minimal satu gambar;
- minimal satu audio;
- satu video.

Tidak wajib mengisi ketiga jenis referensi sekaligus.

## Bagian 3 — Editor prompt interaktif

Editor prompt digunakan untuk menyusun prompt R2V secara teratur tanpa perlu menulis format teknis.

Editor memiliki enam bagian utama:

1. `Definisi Subjek`
2. `Ringkasan`
3. `Analisis Pemertahanan Referensi`
4. `Deskripsi Rinci`
5. `Suasana Suara Keseluruhan`
6. `Musik Latar`

Semua isi prompt yang dikirim ke model harus menggunakan bahasa Inggris, kecuali dialog, lirik, atau teks yang memang harus tetap menggunakan bahasa aslinya.

### Definisi Subjek

Jelaskan subjek penting dan hubungan subjek tersebut dengan referensi.

Contoh:

```text
<Picture 1> shows a woman standing in a kitchen. <Subject 1> is the woman.
<Picture 2> shows the kitchen background and its main objects.
```

Gunakan nomor referensi yang benar-benar tersedia. Jangan menulis `<Picture 3>` jika hanya dua gambar yang dipilih.

### Ringkasan

Jelaskan secara singkat isi dan tujuan video.

Contoh:

```text
The woman prepares tea in the kitchen while the camera slowly moves closer.
```

### Analisis Pemertahanan Referensi

Jelaskan bagian mana dari referensi yang harus dipertahankan, misalnya identitas wajah, pakaian, bentuk objek, suasana, atau komposisi.

Contoh:

```text
<Subject 1>: fully_preserved — preserve her identity, face, clothing, and hair.
<Picture 2>: fully_preserved — preserve the kitchen layout and lighting direction.
```

### Deskripsi Rinci

Bagian ini menjelaskan perjalanan video dari awal sampai akhir.

Pada editor interaktif, bagian ini berisi:

- pembuka gaya visual, bila diperlukan;
- daftar kartu `Bidikan`;
- waktu mulai dan selesai setiap bidikan;
- gambaran visual;
- aksi;
- kamera;
- dialog atau lirik;
- suara dalam adegan.

### Suasana Suara Keseluruhan

Jelaskan suara lingkungan dan suasana audio yang berlangsung sepanjang video.

Contoh:

```text
Soft room ambience and the natural sound of the kettle continue throughout the video.
```

### Musik Latar

Jelaskan musik yang hanya didengar oleh penonton. Isi `N/A` jika tidak ada musik latar.

Contoh:

```text
N/A
```

## Bagian 4 — Kartu Bidikan

### Menambah bidikan

Tekan `Tambah Bidikan` untuk menambahkan bagian baru pada linimasa.

Setiap bidikan akan diberi nomor otomatis, misalnya `Bidikan 1`, `Bidikan 2`, dan seterusnya.

### Menghapus bidikan

Tekan `Hapus` pada kartu bidikan yang ingin dihapus.

Minimal harus ada satu bidikan. Bidikan terakhir tidak dapat dihapus jika hanya tersisa satu kartu.

### Waktu mulai dan selesai

Isi waktu dalam satuan detik.

Contoh:

```text
Bidikan 1: Mulai 0.00 — Selesai 2.00
Bidikan 2: Mulai 2.00 — Selesai 5.00
```

Aturan waktu:

- `Bidikan 1` harus dimulai dari `0.00` detik.
- Waktu selesai harus lebih besar daripada waktu mulai.
- Bidikan berikutnya harus berada setelah bidikan sebelumnya.
- Rentang bidikan tidak boleh tumpang tindih.
- Waktu tidak boleh melewati durasi adegan.

Tombol `Akhir = durasi` mengatur waktu selesai bidikan terakhir agar sama dengan durasi adegan.

### Gambaran Visual

Jelaskan apa yang terlihat pada bidikan.

Sebaiknya mencakup hal-hal seperti:

- subjek dan identitasnya;
- komposisi dan posisi;
- pakaian;
- lingkungan;
- pencahayaan;
- properti;
- teks yang terlihat;
- referensi yang sedang digunakan.

### Aksi

Jelaskan gerakan atau perubahan yang terjadi.

Contoh:

```text
The woman lifts the cup, looks toward the window, and takes a slow sip.
```

### Kamera

Jelaskan pembingkaian dan gerakan kamera.

Contoh:

```text
The camera slowly pushes in from a medium shot to a close-up.
```

### Dialog / Lirik

Masukkan dialog atau lirik jika ada. Jika tidak ada, tulis `No dialogue.`

Dialog dan lirik boleh menggunakan bahasa Indonesia atau bahasa asli yang harus terdengar di video.

### Suara dalam Adegan

Jelaskan suara yang berasal dari kejadian di dalam adegan, misalnya suara langkah kaki, pintu, air, atau suara objek.

Contoh:

```text
The cup makes a soft ceramic sound when placed on the table.
```

Suara dalam adegan dari setiap bidikan akan digunakan sesuai urutan bidikan. Suasana suara keseluruhan dan musik latar berlaku untuk seluruh video.

## Bagian 5 — Perintah kepada LLM

Kolom `Perintah kepada LLM` berisi arahan tambahan jika pengguna ingin meminta Gemini membuat prompt.

Contoh:

```text
Buat video yang tenang dan realistis. Pertahankan wajah, pakaian, dan tata letak ruangan dari referensi. Gunakan gerakan kamera yang halus.
```

Kolom ini hanya diperlukan jika tombol `Buat Prompt` digunakan.

## Bagian 6 — Meminta bantuan membuat prompt

### Kapan digunakan

Gunakan `Buat Prompt` jika Anda:

- belum yakin cara menyusun prompt MiniMax H3;
- ingin Gemini membantu mengisi enam bagian prompt;
- ingin mengubah deskripsi adegan menjadi prompt yang lebih terstruktur.

### Data yang digunakan Gemini

Saat tombol ditekan, aplikasi mengirimkan konteks berikut:

- judul adegan;
- tipe adegan;
- `Deskripsi Adegan` dari tab `Meta`;
- ukuran video;
- daftar referensi aktif dan urutannya;
- gambar referensi yang dipilih, dalam urutan slotnya;
- isi `Perintah kepada LLM`.

`Teks Suara` pada tab `Meta` bukan bagian dari konteks prompt R2V.

### Hal yang perlu diperhatikan

1. Pastikan referensi sudah dipilih dan urutannya benar.
2. Isi `Perintah kepada LLM` sebelum menekan `Buat Prompt`.
3. Periksa hasil prompt pada editor setelah Gemini selesai.
4. Periksa kembali label `<Picture N>`, `<Audio N>`, dan `<Video 1>`.
5. Sesuaikan isi bidikan bila hasil Gemini belum sesuai adegan.

Hasil `Buat Prompt` langsung ditampilkan pada editor dan menggantikan isi prompt sebelumnya. Periksa hasilnya sebelum menyimpan atau menjalankan adegan.

## Bagian 7 — Menyimpan adegan

Tekan tombol simpan pada toolbar setelah mengubah referensi atau prompt.

Saat disimpan, perubahan pada referensi, pengaturan, dan prompt akan disimpan pada adegan aktif.

Jika ada masalah, aplikasi akan menampilkan peringatan validasi. Perbaiki masalah tersebut sebelum menjalankan adegan.

## Bagian 8 — Menjalankan adegan

Tekan tombol jalankan adegan pada toolbar.

Sebelum proses dimulai, aplikasi akan menyimpan perubahan dan memeriksa durasi, referensi, prompt, pengaturan, serta koneksi ComfyUI.

Jika suatu jenis referensi tidak dipilih, video tetap dapat dibuat menggunakan jenis referensi lain yang tersedia. Gambar, audio, dan video tidak harus dipilih sekaligus.

## Syarat agar scene dapat dijalankan

Periksa hal-hal berikut jika scene berwarna merah atau tidak dapat dijalankan:

- durasi berada antara 0 sampai 15 detik;
- minimal satu referensi gambar, audio, atau video dipilih;
- maksimal lima gambar dipilih;
- maksimal tiga audio dipilih;
- maksimal satu video dipilih;
- tidak ada referensi yang sama berulang;
- semua file referensi masih ada di folder scene;
- enam bagian prompt terisi dengan benar;
- minimal satu bidikan tersedia;
- waktu bidikan berurutan dan tidak tumpang tindih;
- jumlah step berada pada nilai yang diterima aplikasi;
- ComfyUI dapat diakses.

`Deskripsi Adegan` pada tab `Meta` membantu Gemini memahami konteks, tetapi boleh dikosongkan.

## Contoh alur sederhana

Misalnya pengguna ingin membuat video seorang wanita membaca buku:

1. Pada `Meta`, pilih tipe `minimax-h3_r2v` dan durasi `5` detik.
2. Pada referensi gambar, pilih `wanita.png` sebagai `Picture 1`.
3. Pilih `Audio 1` jika ada suara lingkungan atau ucapan yang perlu dijadikan referensi.
4. Pada `Definisi Subjek`, jelaskan bahwa `<Subject 1>` adalah wanita pada `<Picture 1>`.
5. Pada `Ringkasan`, jelaskan bahwa wanita membaca buku di ruang yang tenang.
6. Pada `Deskripsi Rinci`, buat satu bidikan dari `0.00` sampai `5.00` detik.
7. Isi gambaran visual, aksi membaca, gerakan kamera, dialog, dan suara dalam adegan.
8. Isi `Suasana Suara Keseluruhan`.
9. Isi `Musik Latar` dengan `N/A` jika tidak ada musik.
10. Simpan adegan dan jalankan.

Jika pengguna belum tahu cara menulis bagian-bagian tersebut, isi `Perintah kepada LLM`, lalu gunakan `Buat Prompt` sebagai bantuan. Hasilnya tetap perlu diperiksa sebelum dijalankan.
