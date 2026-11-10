# MINIMAX-H3_T2V

## Fungsi tampilan

`MINIMAX-H3_T2V` digunakan untuk membuat video MiniMax H3 hanya dari prompt teks.

Tidak diperlukan gambar awal, audio speech, atau video referensi. Isi prompt menjelaskan subjek, lingkungan, gerakan, kamera, dialog, dan suara yang ingin dibuat dalam video.

## Alur kerja singkat

1. Pada tab `Meta`, pilih tipe adegan `minimax-h3_t2v`.
2. Atur durasi adegan.
3. Buka tab `MINIMAX-H3_T2V`.
4. Pilih ukuran, LoRA, mode, dan jumlah step jika diperlukan.
5. Susun prompt melalui kartu bidikan.
6. Isi `Perintah kepada LLM` jika ingin meminta bantuan Gemini.
7. Simpan adegan.
8. Jalankan adegan melalui tombol proses.

## Pengaturan video

### Durasi

Durasi T2V dapat diatur antara `0` sampai `15` detik, dengan maksimal empat angka di belakang koma.

Durasi yang dipilih pada tab `Meta` menjadi acuan linimasa seluruh bidikan. Pastikan bidikan terakhir berakhir pada durasi tersebut.

### Ukuran

Menentukan ukuran video keluaran. Pilih ukuran sesuai orientasi dan kebutuhan project.

### Pakai Lora

Centang `Pakai Lora` bila ingin menggunakan LoRA pada video. Jika tidak dicentang, LoRA 1 dan LoRA 2 dilewati sehingga video dibuat tanpa LoRA.

### LoRA dan Kekuatan

Pilih LoRA pertama jika ingin menambahkan gaya, karakter, atau ciri visual tertentu. `Kekuatan` mengatur seberapa besar pengaruh LoRA tersebut.

LoRA kedua bersifat opsional dan dapat digunakan untuk menggabungkan pengaruh visual tambahan.

### Hapus Sound

Jika diaktifkan, suara yang dihasilkan bersama video akan dihapus dari hasil video.

Gunakan pilihan ini jika video hanya membutuhkan gambar bergerak tanpa suara bawaan.

### Mode Cepat

Menggunakan pengaturan MiniMax H3 yang dirancang untuk pemrosesan lebih cepat. Mode ini menggunakan jumlah langkah khusus untuk mode cepat.

### Jumlah Step

Menentukan jumlah langkah pemrosesan. Nilai yang lebih besar dapat membuat proses lebih lama dan dapat memengaruhi hasil video.

Saat `Mode Cepat` aktif, jumlah step normal tidak digunakan.

## Editor prompt interaktif

Editor T2V menyusun prompt melalui kartu `Bidikan`. Setiap bidikan menjelaskan satu bagian dari alur video.

Setiap bidikan memiliki:

- waktu mulai dan selesai;
- gambaran visual;
- aksi;
- kamera;
- dialog atau lirik;
- suara yang berasal dari kejadian di dalam adegan.

Editor juga memiliki dua pengaturan suara untuk seluruh video:

- `Suasana Suara Keseluruhan`;
- `Musik Latar`.

Isi prompt untuk model menggunakan bahasa Inggris. Dialog, lirik, atau teks yang memang harus terdengar atau terlihat dapat tetap menggunakan bahasa aslinya.

## Kartu Bidikan

### Menambah bidikan

Tekan `Tambah` untuk menambahkan bidikan baru pada linimasa.

Setiap bidikan diberi nomor otomatis, misalnya `Bidikan 1`, `Bidikan 2`, dan seterusnya.

### Menghapus bidikan

Tekan `Hapus` pada kartu bidikan yang ingin dihapus. Minimal harus ada satu bidikan.

### Waktu bidikan

Isi waktu dalam satuan detik.

Contoh:

```text
Bidikan 1: Mulai 0.00 — Selesai 1.00
Bidikan 2: Mulai 1.00 — Selesai 3.00
Bidikan 3: Mulai 3.00 — Selesai 5.00
```

Saat dikirim ke model, setiap bidikan menggunakan format rentang waktu seperti berikut:

```text
[Shot 1] From 0.00 to 1.00 seconds
[Shot 2] From 1.00 to 3.00 seconds
```

Aturan waktunya:

- bidikan pertama harus dimulai dari `0.00` detik;
- waktu selesai harus lebih besar daripada waktu mulai;
- bidikan berikutnya harus berada setelah bidikan sebelumnya;
- bidikan tidak boleh saling bertumpang tindih;
- waktu bidikan tidak boleh melewati durasi adegan.

Gunakan `Akhir = durasi` untuk mengatur waktu selesai bidikan terakhir sama dengan durasi adegan.

### Gambaran Visual

Jelaskan subjek, komposisi, pakaian, lingkungan, pencahayaan, properti, serta perubahan visual yang terlihat.

Contoh:

```text
A woman stands beside a window, holding a red book. The room is softly lit by warm morning light.
```

### Aksi

Jelaskan gerakan subjek, reaksi, atau perubahan objek selama bidikan berlangsung.

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

Jelaskan suara yang berasal dari kejadian di dalam adegan, seperti langkah kaki, halaman buku, pintu, air, atau suara objek.

## Suasana suara dan musik

### Suasana Suara Keseluruhan

Jelaskan suara lingkungan yang berlangsung sepanjang video, termasuk suasana ruangan, angin, keramaian, atau suara lingkungan lain yang tidak hanya muncul pada satu bidikan.

Contoh:

```text
Soft room ambience and gentle outdoor wind continue throughout the video.
```

### Musik Latar

Jelaskan musik yang hanya didengar oleh penonton. Isi `N/A` jika tidak ada musik latar.

Contoh:

```text
N/A
```

Bedakan musik latar dari suara yang berasal dari kejadian di dalam adegan. Suara halaman buku atau langkah kaki ditulis pada `Suara dalam Adegan`, sedangkan musik yang hanya menjadi pengiring ditulis pada `Musik Latar`.

## Meminta bantuan membuat prompt

Jika ingin mendapatkan bantuan Gemini, isi `Perintah kepada LLM` dengan arahan yang jelas, lalu tekan `Buat Prompt`.

Gemini akan menggunakan informasi adegan, durasi, ukuran T2V, dan arahan tambahan tersebut untuk membantu mengisi prompt. Hasilnya akan dimasukkan ke editor yang sedang aktif.

Contoh perintah:

```text
Buat adegan sinematik yang tenang. Tampilkan perubahan dari suasana pagi hingga tokoh mulai membaca buku. Gunakan gerakan kamera yang halus dan pertahankan kesinambungan pencahayaan.
```

Periksa kembali hasilnya sebelum menyimpan, terutama:

- urutan kejadian;
- waktu mulai dan selesai setiap bidikan;
- kesinambungan subjek dan lingkungan;
- dialog atau lirik;
- suara dalam adegan, suasana suara keseluruhan, dan musik latar.

`Deskripsi Adegan` pada tab `Meta` membantu Gemini memahami konteks, tetapi boleh dikosongkan.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah selesai mengubah pengaturan atau prompt.

Sebelum menjalankan adegan, pastikan:

- durasi berada antara `0` sampai `15` detik;
- minimal ada satu bidikan;
- bidikan pertama dimulai dari `0.00` detik;
- waktu bidikan tersusun berurutan dan tidak bertumpang tindih;
- bidikan terakhir tidak melewati durasi adegan;
- setiap bidikan memiliki isi pada setidaknya satu bagian penjelasan;
- jumlah step berada pada nilai yang diterima aplikasi;
- ComfyUI dapat diakses.

T2V tidak membutuhkan gambar awal, audio speech, atau video referensi.

## Contoh penggunaan

1. Pada tab `Meta`, pilih `minimax-h3_t2v`.
2. Atur durasi menjadi `5` detik.
3. Buka tab `MINIMAX-H3_T2V`.
4. Buat `Bidikan 1` dari `0.00` sampai `2.00` detik untuk memperkenalkan tokoh dan lingkungan.
5. Tambahkan `Bidikan 2` dari `2.00` sampai `5.00` detik untuk menjelaskan aksi utama dan gerakan kamera.
6. Isi dialog, suara dalam adegan, atau musik latar bila diperlukan.
7. Gunakan `Akhir = durasi` untuk memastikan bidikan terakhir berakhir pada `5.00` detik.
8. Simpan, lalu jalankan adegan.
