# MINIMAX-H3_S2V

## Fungsi tampilan

`MINIMAX-H3_S2V` digunakan untuk membuat video dari satu gambar awal dan satu audio speech.

Gambar awal menjadi tampilan dasar video. Audio speech menjadi suara utama yang harus diikuti oleh gerakan mulut atau gerakan subjek yang berbicara. Hasilnya dapat digunakan untuk membuat karakter atau subjek pada gambar terlihat berbicara mengikuti audio yang tersedia.

## Alur kerja singkat

1. Pada tab `Meta`, pilih tipe adegan `minimax-h3_s2v`.
2. Siapkan gambar awal pada tab `Gambar Awal` atau letakkan gambar di aset adegan.
3. Siapkan audio speech untuk adegan tersebut.
4. Buka tab `MINIMAX-H3_S2V`.
5. Atur ukuran, LoRA, mode, dan jumlah step jika diperlukan.
6. Susun isi prompt pada editor interaktif.
7. Isi `Perintah kepada LLM` jika ingin meminta bantuan Gemini.
8. Simpan adegan.
9. Jalankan adegan melalui tombol proses.

## Gambar awal

S2V memakai satu gambar sebagai tampilan awal dan referensi visual sepanjang video.

Aplikasi menggunakan gambar terbaru yang berada langsung di folder aset adegan. Jika ada beberapa gambar, gambar dengan waktu perubahan terakhir akan digunakan.

Karena itu, pastikan gambar yang ingin dipakai sudah menjadi gambar terbaru sebelum adegan dijalankan. Gambar tersebut dapat dibuat melalui tab `Gambar Awal` atau ditambahkan ke aset adegan.

Gambar awal sebaiknya sudah menampilkan subjek, posisi, pakaian, dan lingkungan yang ingin dipertahankan. Prompt kemudian menjelaskan gerakan yang boleh terjadi dari tampilan tersebut.

## Audio speech

S2V membutuhkan satu audio speech yang tersedia di folder aset adegan.

Audio speech yang dibuat oleh aplikasi biasanya sudah memakai penamaan yang benar. Jika menambahkan file secara manual, nama file harus diawali dengan `speech_`, misalnya:

```text
speech_001.wav
speech_tokoh_utama.mp3
```

Jika ada beberapa audio speech, aplikasi menggunakan audio speech terbaru.

Audio harus dapat dibaca dan durasinya tidak boleh lebih dari 15 detik. Durasi audio ini menjadi acuan utama panjang video S2V.

Isi ucapan pada audio harus sesuai dengan arahan di prompt. Jika prompt menjelaskan siapa yang berbicara, gunakan subjek dan bahasa yang sama dengan audio agar hasil sinkronisasi lebih konsisten.

## Pengaturan video

### Ukuran

Menentukan ukuran video keluaran. Pilih ukuran sesuai orientasi dan kebutuhan project.

### Pakai Lora

Centang `Pakai Lora` bila ingin menggunakan LoRA pada video. Jika tidak dicentang, LoRA 1 dan LoRA 2 dilewati sehingga video dibuat tanpa LoRA.

### LoRA dan Kekuatan

Pilih LoRA pertama jika ingin menambahkan gaya, karakter, atau ciri visual tertentu. `Kekuatan` mengatur seberapa besar pengaruh LoRA tersebut.

LoRA kedua bersifat opsional dan dapat digunakan untuk menggabungkan pengaruh visual tambahan.

### Ganti Speech

Jika diaktifkan, audio speech yang dipilih akan digunakan sebagai audio akhir video dan menggantikan audio yang dihasilkan bersama video.

Gunakan pilihan ini jika suara akhir harus sama persis dengan file speech yang disiapkan. Jika tidak diaktifkan, aplikasi mempertahankan audio yang ada pada hasil video dari model.

### Mode Cepat

Menggunakan pengaturan MiniMax H3 yang dirancang untuk pemrosesan lebih cepat. Mode ini menggunakan jumlah langkah khusus untuk mode cepat.

### Jumlah Step

Menentukan jumlah langkah pemrosesan. Nilai yang lebih besar dapat membuat proses lebih lama dan dapat memengaruhi hasil video.

Saat `Mode Cepat` aktif, jumlah step normal tidak digunakan.

## Editor prompt interaktif

Editor S2V berisi enam bagian yang membantu menjelaskan gambar, subjek, gerakan, dan audio speech:

1. `Definisi Subjek`
2. `Ringkasan`
3. `Analisis Pemertahanan Referensi`
4. `Deskripsi Rinci`
5. `Suasana Suara Keseluruhan`
6. `Musik Latar`

Untuk S2V, gunakan `<Picture 1>` untuk gambar awal dan `<Audio 1>` untuk audio speech. Kedua referensi tersebut sudah ditentukan oleh alur S2V, sehingga tidak perlu memilih beberapa gambar atau audio di tab ini.

Isi prompt untuk model menggunakan bahasa Inggris. Dialog, lirik, atau teks yang memang harus terdengar atau terlihat dapat tetap menggunakan bahasa aslinya.

### Definisi Subjek

Jelaskan subjek utama pada gambar awal dan hubungan subjek tersebut dengan audio speech.

Contoh:

```text
<Picture 1> shows a woman sitting at a desk. <Subject 1> is the woman.
<Audio 1> is the complete speech recording spoken by <Subject 1>.
```

Gunakan `<Picture 1>` dan `<Audio 1>` sesuai perannya. Jangan menambahkan nomor referensi lain yang tidak tersedia pada S2V.

### Ringkasan

Jelaskan secara singkat video yang ingin dibuat dan hubungan gerakan subjek dengan audio.

Contoh:

```text
[keyframe completion + audio reuse] Create a restrained talking portrait from <Picture 1>, with <Subject 1> speaking in sync with <Audio 1>.
```

### Analisis Pemertahanan Referensi

Jelaskan bagian gambar dan audio yang harus dipertahankan.

Contoh:

```text
<Picture 1>: fully_preserved — preserve the subject's identity, face, clothing, pose, lighting, background, and framing.
<Audio 1>: fully_copy — use the complete speech recording without changing its words or timing.
```

Bagian ini membantu menjaga agar subjek tidak berubah dan audio tetap digunakan secara utuh.

### Deskripsi Rinci

Jelaskan alur video dari awal sampai akhir dalam satu uraian yang berkesinambungan.

Untuk S2V, biasanya cukup gunakan satu bagian yang dimulai dengan `[Shot 1]`. Jelaskan bahwa video dimulai dari `<Picture 1>`, subjek bergerak seperlunya untuk mengikuti `<Audio 1>`, lalu berhenti setelah audio selesai.

Contoh:

```text
[Shot 1] The video begins exactly from <Picture 1>. The camera remains locked and the composition stays still. <Subject 1> moves only the lips and mouth naturally in sync with the speech from <Audio 1>. After the speech ends, <Subject 1> remains still until the video ends. Do not add unnecessary head, body, hand, camera, background, or object movement.
```

S2V tidak menggunakan kartu bidikan terpisah seperti editor T2V. Jika adegan membutuhkan perubahan yang lebih kompleks, tetap jelaskan urutannya secara jelas di dalam uraian ini.

### Suasana Suara Keseluruhan

Jelaskan penggunaan audio speech sepanjang video.

Untuk video bicara sederhana, tegaskan bahwa audio menggunakan `<Audio 1>` secara utuh dan tidak menambahkan suara lain yang dapat mengganggu ucapan.

Contoh:

```text
Use only the complete speech recording from <Audio 1>, synchronized with the lip movement of <Subject 1>. After the speech ends, maintain silence until the video ends. Do not add ambience or sound effects.
```

### Musik Latar

Jelaskan musik yang hanya didengar oleh penonton. Isi `N/A` jika tidak ada musik latar.

Untuk video speech yang mengutamakan kejelasan ucapan, `N/A` biasanya merupakan pilihan yang tepat.

## Meminta bantuan membuat prompt

Jika ingin mendapatkan bantuan Gemini, isi `Perintah kepada LLM` dengan arahan yang jelas, lalu tekan `Buat Prompt`.

Gemini akan menggunakan informasi adegan, gambar awal yang tersedia, dan aturan S2V untuk membantu mengisi prompt. Hasilnya akan dimasukkan ke editor yang sedang aktif.

Contoh perintah:

```text
Create a calm talking portrait. Preserve the face, clothing, pose, lighting, and background of the initial image. Keep the camera still and synchronize the mouth movement with the speech recording.
```

Periksa kembali hasilnya sebelum menyimpan, terutama:

- subjek yang harus dipertahankan;
- penggunaan `<Picture 1>` dan `<Audio 1>`;
- kesesuaian gerakan mulut dengan audio;
- isi `Deskripsi Rinci`;
- pengaturan suara keseluruhan dan musik latar.

`Deskripsi Adegan` pada tab `Meta` membantu Gemini memahami konteks, tetapi boleh dikosongkan.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah selesai mengubah gambar, audio, pengaturan, atau prompt.

Sebelum menjalankan adegan, pastikan:

- tersedia setidaknya satu gambar di folder aset utama adegan;
- gambar yang ingin digunakan merupakan gambar terbaru;
- tersedia audio speech dengan nama yang diawali `speech_`;
- audio speech dapat dibaca dan durasinya tidak lebih dari 15 detik;
- prompt memiliki isi yang lengkap;
- penggunaan `<Picture 1>` dan `<Audio 1>` sesuai;
- jumlah step berada pada nilai yang diterima aplikasi;
- ComfyUI dapat diakses.

## Contoh penggunaan

1. Buat atau tambahkan gambar seorang wanita yang duduk di depan meja pada tab `Gambar Awal`.
2. Pastikan audio speech untuk wanita tersebut sudah tersedia sebagai file yang diawali `speech_`.
3. Pada tab `Meta`, pilih `minimax-h3_s2v`.
4. Buka tab `MINIMAX-H3_S2V`.
5. Pilih ukuran dan LoRA jika diperlukan.
6. Pada `Definisi Subjek`, jelaskan bahwa `<Subject 1>` adalah wanita pada `<Picture 1>` dan `<Audio 1>` adalah ucapannya.
7. Pada `Deskripsi Rinci`, jelaskan gerakan bicara yang natural dan tetap menjaga komposisi gambar.
8. Pada `Suasana Suara Keseluruhan`, arahkan penggunaan audio speech secara utuh.
9. Simpan, lalu jalankan adegan.

Jika `Ganti Speech` diaktifkan, audio akhir video akan menggunakan file speech yang dipilih secara langsung.
