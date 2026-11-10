# MINIMAX-H3_I2V

## Fungsi tampilan

Tab `MINIMAX-H3_I2V` digunakan untuk membuat video dari gambar awal.

## Alur I2V biasa

1. Pada tab `Meta`, pilih tipe adegan `minimax-h3_i2v`.
2. Siapkan gambar awal pada tab `Gambar Awal`.
3. Buka tab `MINIMAX-H3_I2V`.
4. Atur ukuran, LoRA, mode, dan jumlah step.
5. Susun prompt melalui editor interaktif.
6. Isi `Perintah kepada LLM` jika ingin meminta bantuan Gemini.
7. Simpan adegan.
8. Jalankan adegan melalui tombol proses.

Untuk I2V biasa, aplikasi menggunakan gambar awal terbaru yang tersedia pada adegan. Pastikan gambar yang ingin digunakan sudah menjadi gambar awal yang terakhir dibuat atau tersedia pada aset adegan.

## Pengaturan video

### Ukuran

Menentukan ukuran video keluaran.

### Pakai Lora

Centang `Pakai Lora` bila ingin menggunakan LoRA pada video. Jika tidak dicentang, LoRA 1 dan LoRA 2 dilewati sehingga video dibuat tanpa LoRA.

### LoRA dan Kekuatan

Memilih LoRA serta menentukan seberapa kuat pengaruhnya terhadap hasil video. LoRA kedua bersifat pilihan tambahan.

### Hapus Sound

Menghapus suara dari video hasil pembuatan jika diaktifkan.

### Mode Cepat

Menggunakan pengaturan pemrosesan MiniMax H3 yang lebih cepat.

### Jumlah Step

Menentukan jumlah langkah pemrosesan. Nilai yang lebih besar dapat memengaruhi waktu proses dan hasil video.

## Editor prompt interaktif

Editor digunakan untuk menjelaskan isi video melalui kartu bidikan.

Setiap bidikan memiliki bagian berikut:

- waktu mulai dan selesai;
- gambaran visual;
- aksi;
- kamera;
- dialog atau lirik;
- suara dalam adegan.

Editor juga memiliki pengaturan suara untuk seluruh video:

- `Suasana Suara Keseluruhan`;
- `Musik Latar`.

### Bidikan pertama

Bidikan pertama harus dimulai dari `0.00` detik dan menggambarkan kondisi gambar awal. Jelaskan perubahan yang terjadi setelah gambar awal tersebut.

### Menambah dan menghapus bidikan

- Tekan `Tambah` untuk membuat bidikan baru.
- Tekan `Hapus` untuk menghapus bidikan.
- Minimal harus ada satu bidikan.

### Aturan waktu bidikan

- Waktu selesai harus lebih besar daripada waktu mulai.
- Bidikan berikutnya harus berada setelah bidikan sebelumnya.
- Bidikan tidak boleh saling bertumpang tindih.
- Waktu bidikan tidak boleh melewati durasi adegan.

Gunakan `Akhir = durasi` untuk mengatur waktu selesai bidikan terakhir agar sama dengan durasi adegan.

### Gambaran Visual

Jelaskan subjek, komposisi, pakaian, lingkungan, pencahayaan, properti, dan perubahan visual yang terlihat.

Contoh:

```text
A woman stands beside a window, holding a red book. The room is softly lit by warm morning light.
```

### Aksi

Jelaskan gerakan subjek atau perubahan objek.

Contoh:

```text
She slowly opens the book and begins reading while turning one page.
```

### Kamera

Jelaskan pembingkaian serta gerakan kamera.

Contoh:

```text
The camera begins with a medium shot and slowly moves closer to her face.
```

### Dialog / Lirik

Masukkan dialog atau lirik jika ada. Jika tidak ada, tulis `No dialogue.`

Dialog dan lirik dapat menggunakan bahasa Indonesia atau bahasa asli yang harus terdengar di video.

### Suara dalam Adegan

Jelaskan suara yang berasal dari kejadian di dalam adegan, seperti suara halaman buku, langkah kaki, pintu, atau angin.

### Suasana Suara Keseluruhan

Jelaskan suara lingkungan yang berlangsung sepanjang video.

### Musik Latar

Jelaskan musik yang hanya didengar oleh penonton. Isi `N/A` jika tidak ada musik latar.

## Meminta bantuan membuat prompt

Jika ingin Gemini membantu menyusun prompt, isi `Perintah kepada LLM` dengan arahan yang jelas, lalu tekan `Buat Prompt`.

Contoh:

```text
Buat video yang tenang dan realistis. Pertahankan wajah, pakaian, dan komposisi gambar awal. Gunakan gerakan kamera yang halus.
```

Gemini menggunakan `Deskripsi Adegan` dari tab `Meta`, pengaturan I2V, dan gambar awal yang digunakan oleh adegan. `Teks Suara` tidak menjadi bagian dari arahan prompt I2V.

`Deskripsi Adegan` membantu Gemini memahami konteks, tetapi boleh dikosongkan.

Setelah selesai, hasilnya ditampilkan pada editor. Periksa kembali isi bidikan, terutama gambaran gambar awal pada bidikan pertama, sebelum menyimpan atau menjalankan adegan.

## Menyimpan dan menjalankan adegan

Tekan tombol simpan setelah selesai mengubah pengaturan atau prompt.

Saat adegan dijalankan, aplikasi akan memeriksa durasi, gambar awal, prompt, pengaturan mode, dan koneksi ComfyUI sebelum memulai pembuatan video.

Pastikan:

- durasi berada antara 0 sampai 15 detik;
- minimal satu gambar awal tersedia;
- bidikan pertama dimulai dari 0.00 detik;
- prompt memiliki isi yang lengkap;
- jumlah step berada pada nilai yang diterima aplikasi;
- ComfyUI dapat diakses.

## Contoh penggunaan

1. Buat gambar seorang wanita berdiri di dekat jendela pada tab `Gambar Awal`.
2. Pilih tipe `minimax-h3_i2v` pada tab `Meta`.
3. Atur durasi menjadi `5` detik.
4. Pada editor, buat satu bidikan dari `0.00` sampai `5.00` detik.
5. Jelaskan kondisi awal wanita dan gerakan yang terjadi setelahnya.
6. Isi suara dalam adegan dan musik latar jika diperlukan.
7. Simpan, lalu jalankan adegan.
