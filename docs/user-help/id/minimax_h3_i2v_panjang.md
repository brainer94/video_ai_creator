# MINIMAX-H3_I2V-PANJANG

## Fungsi tampilan

Tab `MINIMAX-H3_I2V-PANJANG` digunakan untuk membuat video melalui beberapa proses yang saling tersambung. Setiap proses menghasilkan satu bagian video, kemudian seluruh bagian disusun menjadi satu video akhir.

Tersedia empat tab proses: `Proses 1`, `Proses 2`, `Proses 3`, dan `Proses 4`.

## Alur penggunaan

1. Pada tab `Meta`, pilih tipe adegan `minimax-h3_i2v-panjang`.
2. Tentukan durasi untuk setiap bagian video.
3. Buka tab `MINIMAX-H3_I2V-PANJANG`.
4. Tentukan jumlah proses melalui `Jumlah lanjutan`.
5. Pada setiap proses yang digunakan, pilih `Image awal (wajib)` dan `Image akhir (wajib)`.
6. Susun prompt pada setiap proses.
7. Atur `Run mulai dari tab` jika ingin melanjutkan dari proses tertentu.
8. Simpan adegan.
9. Jalankan rangkaian proses.

## Pengaturan utama

Pengaturan utama berada pada `Proses 1` dan berlaku untuk seluruh rangkaian.

### Ukuran

Menentukan ukuran video yang dibuat.

### Pakai Lora

Centang `Pakai Lora` bila ingin menggunakan LoRA pada seluruh proses yang dijalankan. Jika tidak dicentang, LoRA 1 dan LoRA 2 dilewati pada setiap proses.

### LoRA dan Kekuatan

Memilih LoRA serta menentukan seberapa kuat pengaruhnya. LoRA kedua dapat digunakan sebagai tambahan.

### Hapus Sound

Menghapus suara dari bagian video yang dibuat jika diaktifkan.

### Mode Cepat

Menggunakan pengaturan pemrosesan MiniMax H3 yang lebih cepat.

### Jumlah Step

Menentukan jumlah langkah pemrosesan. Nilai yang lebih besar dapat memengaruhi waktu proses dan hasil video.

## Jumlah lanjutan

`Jumlah lanjutan` menentukan jumlah proses yang dipakai:

- `0` berarti hanya `Proses 1`;
- `1` berarti `Proses 1` dan `Proses 2`;
- `2` berarti `Proses 1` sampai `Proses 3`;
- `3` berarti seluruh proses sampai `Proses 4`.

Tab proses yang belum digunakan akan disembunyikan. Prompt dan referensi pada setiap proses tetap terpisah.

## Image awal dan Image akhir

`Image Awal` adalah gambar yang menjadi frame pertama dari video pada proses tersebut.

`Image Akhir` adalah gambar yang menjadi frame terakhir dari video pada proses tersebut.

Dengan demikian, AI sudah diberikan dua kondisi yang harus dicapai:

1. Video dimulai dari `Image Awal`.
2. Video berakhir pada `Image Akhir`.
3. AI membuat alur gerakan dan kejadian di antara kedua gambar tersebut berdasarkan prompt.
4. Prompt digunakan untuk mengarahkan bagaimana perubahan dari gambar awal menuju gambar akhir berlangsung.

Pada setiap proses aktif, `Image awal (wajib)` dan `Image akhir (wajib)` harus dipilih.

### Jumlah pasangan gambar

I2V-Panjang dapat menggunakan satu sampai empat proses. Jumlah pasangan gambar mengikuti jumlah proses yang digunakan:

- 1 proses → 1 pasangan `Image Awal` dan `Image Akhir`;
- 2 proses → 2 pasangan;
- 3 proses → 3 pasangan;
- 4 proses → 4 pasangan.

Pilihan dapat berasal dari:

- gambar yang tersedia pada aset adegan;
- frame terakhir dari proses sebelumnya.

### Proses 1

Untuk `Proses 1`, pilih gambar awal dan gambar akhir dari aset adegan.

### Proses 2 sampai Proses 4

Untuk proses berikutnya, gunakan `Frame terakhir Proses N` sebagai `Image awal` jika ingin melanjutkan gerakan dari proses sebelumnya.

Pilihan frame tersebut baru dapat dipakai untuk membuat video setelah proses sebelumnya selesai dibuat. Jika frame belum tersedia, selesaikan proses sebelumnya terlebih dahulu.

`Image akhir` pada setiap proses tetap harus dipilih. Image akhir dapat berupa gambar dari aset adegan atau frame proses sebelumnya yang tersedia pada daftar.

### Hubungan antarproses

Contoh penggunaan dua proses:

```text
Proses 1:
Image Awal  → gambar A
Image Akhir → gambar B

Proses 2:
Image Awal  → Frame terakhir Proses 1
Image Akhir → gambar C
```

Dengan pengaturan tersebut, Proses 2 dimulai dari hasil akhir Proses 1 dan bergerak menuju gambar C.

## Editor prompt setiap proses

Setiap proses memiliki editor prompt sendiri. Perubahan pada satu proses tidak otomatis mengubah prompt proses lainnya.

Setiap bidikan memiliki:

- waktu mulai dan selesai;
- gambaran visual;
- aksi;
- kamera;
- dialog atau lirik;
- suara dalam adegan.

Editor juga memiliki pengaturan suara untuk bagian video tersebut:

- `Suasana Suara Keseluruhan`;
- `Musik Latar`.

### Bidikan pertama

Bidikan pertama harus dimulai dari `0.00` detik dan menggambarkan kondisi `Image awal` proses tersebut.

### Menambah dan menghapus bidikan

- Tekan `Tambah` untuk membuat bidikan baru.
- Tekan `Hapus` untuk menghapus bidikan.
- Minimal harus ada satu bidikan pada setiap proses yang digunakan.

### Aturan waktu bidikan

- Waktu selesai harus lebih besar daripada waktu mulai.
- Bidikan berikutnya harus berada setelah bidikan sebelumnya.
- Bidikan tidak boleh saling bertumpang tindih.
- Waktu bidikan tidak boleh melewati durasi bagian video.

Gunakan `Akhir = durasi` untuk mengatur waktu selesai bidikan terakhir agar sama dengan durasi bagian video.

### Gambaran Visual

Jelaskan subjek, komposisi, pakaian, lingkungan, pencahayaan, properti, dan perubahan visual yang terlihat.

### Aksi

Jelaskan gerakan subjek atau perubahan objek selama bagian video tersebut.

### Kamera

Jelaskan pembingkaian serta gerakan kamera.

### Dialog / Lirik

Masukkan dialog atau lirik jika ada. Jika tidak ada, tulis `No dialogue.`

### Suara dalam Adegan

Jelaskan suara yang berasal dari kejadian di dalam adegan, seperti langkah kaki, pintu, air, atau suara objek.

### Suasana Suara Keseluruhan

Jelaskan suara lingkungan yang berlangsung sepanjang bagian video tersebut.

### Musik Latar

Jelaskan musik yang hanya didengar oleh penonton. Isi `N/A` jika tidak ada musik latar.

## Meminta bantuan membuat prompt

Jika ingin Gemini membantu menyusun prompt untuk suatu proses, isi `Perintah kepada LLM` pada proses tersebut, lalu tekan `Buat Prompt`.

Gemini menggunakan `Deskripsi Adegan` dari tab `Meta`, pengaturan I2V, serta `Image awal` dan `Image akhir` proses yang dipilih.

Hasilnya ditampilkan pada editor proses yang sedang aktif. Periksa kembali isi bidikan, terutama kesesuaian antara prompt, image awal, dan image akhir.

`Deskripsi Adegan` membantu Gemini memahami konteks, tetapi boleh dikosongkan.

## Run mulai dari tab

Biasanya rangkaian dimulai dari `Proses 1`.

`Run mulai dari tab` dapat digunakan untuk melanjutkan dari proses tertentu, misalnya mulai dari `Proses 2` setelah `Proses 1` sudah pernah selesai dibuat.

Jika mulai dari proses lanjutan:

- bagian video dari proses sebelumnya harus sudah tersedia;
- frame terakhir proses sebelumnya harus tersedia jika dipakai sebagai referensi;
- proses yang dijalankan tetap akan digabungkan dengan bagian video sebelumnya.

Gunakan pilihan ini hanya jika proses sebelumnya sudah berhasil dibuat.

## Video akhir

Setiap proses menghasilkan satu bagian video. Video akhir adalah gabungan dari seluruh video pada proses yang aktif, disusun sesuai urutan prosesnya.

Contoh:

```text
Proses 1 → Video bagian pertama
Proses 2 → Video bagian kedua
Proses 3 → Video bagian ketiga
```

Jika tiga proses aktif, video akhir merupakan gabungan video Proses 1, Proses 2, dan Proses 3.

## Menyimpan dan menjalankan adegan

Tekan tombol simpan setelah selesai mengubah pengaturan, pilihan gambar, atau prompt.

Saat adegan dijalankan, aplikasi akan memeriksa durasi, pilihan gambar, prompt setiap proses aktif, pengaturan mode, dan koneksi ComfyUI sebelum memulai pembuatan video.

Pastikan:

- durasi berada antara 0 sampai 15 detik;
- setiap proses aktif memiliki `Image awal`;
- setiap proses aktif memiliki `Image akhir`;
- prompt setiap proses aktif memiliki isi yang lengkap;
- bidikan pertama setiap proses dimulai dari `0.00` detik;
- jumlah step berada pada nilai yang diterima aplikasi;
- proses sebelumnya sudah tersedia jika menggunakan `Run mulai dari tab`;
- ComfyUI dapat diakses.

## Contoh penggunaan dua proses

1. Pada tab `Meta`, pilih `minimax-h3_i2v-panjang`.
2. Atur `Jumlah lanjutan` menjadi `1`.
3. Pada `Proses 1`, pilih gambar awal dan gambar akhir dari aset adegan.
4. Susun prompt `Proses 1` dari awal sampai akhir bagian pertama.
5. Jalankan atau simpan pengaturan sesuai kebutuhan.
6. Pada `Proses 2`, pilih `Frame terakhir Proses 1` sebagai image awal.
7. Pilih image akhir untuk `Proses 2`.
8. Susun prompt `Proses 2` agar melanjutkan adegan dengan wajar.
9. Periksa kedua proses, simpan, lalu jalankan rangkaiannya.

Hasil akhir akan terdiri dari bagian Proses 1 dan Proses 2 secara berurutan.
