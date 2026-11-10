# I2V

## Fungsi tampilan

`I2V` adalah jalur sederhana untuk menyusun beberapa gambar menjadi satu video.

Berbeda dengan `MINIMAX-H3_I2V`, jalur `I2V` tidak meminta model video membuat gerakan baru dari prompt. Aplikasi menampilkan gambar-gambar yang tersedia secara berurutan dan menahan setiap gambar selama sebagian durasi video.

## Mengapa tidak ada tab I2V khusus?

Pada scene tipe `i2v`, pengaturan gambar dilakukan melalui tab `Gambar Awal`, `Prompt Tambahan`, dan `Aset`. Karena jalur ini hanya menyusun gambar yang sudah tersedia, tidak diperlukan tab pengaturan I2V khusus.

Jalur I2V yang memakai model MiniMax H3 memiliki tab terpisah bernama `MINIMAX-H3_I2V`. Pastikan tipe adegan yang dipilih pada tab `Meta` sesuai dengan hasil yang diinginkan.

## Alur kerja singkat

1. Pada tab `Meta`, pilih tipe adegan `i2v`.
2. Atur durasi antara `1` sampai `15` detik.
3. Buat atau tambahkan gambar pada aset adegan.
4. Jika perlu, gunakan `Prompt Tambahan` untuk membuat gambar tambahan.
5. Periksa urutan gambar pada tab `Aset`.
6. Simpan adegan.
7. Jalankan adegan melalui tombol proses.

## Gambar yang digunakan

I2V menggunakan semua file gambar yang berada langsung di folder aset utama adegan.

Gambar tidak dipilih melalui slot satu per satu. Karena itu, file gambar yang tidak ingin dimasukkan ke video sebaiknya tidak diletakkan di folder utama adegan.

Format gambar yang dapat digunakan meliputi PNG, JPG, JPEG, dan WEBP.

## Urutan gambar

Urutan gambar mengikuti urutan abjad nama file, bukan urutan waktu dibuat dan bukan urutan klik pengguna.

Contoh:

```text
01_pembuka.png
02_tokoh_masuk.png
03_tokoh_berbicara.png
04_penutup.png
```

Dengan penamaan tersebut, gambar akan tampil dalam urutan yang diharapkan.

Jika nama file tidak memiliki nomor awal, urutan dapat terlihat seperti berikut:

```text
akhir.png
awal.png
tengah.png
```

Urutan tersebut mengikuti abjad, sehingga tidak selalu sama dengan urutan cerita. Gunakan awalan angka dengan jumlah digit yang konsisten, misalnya `01`, `02`, `03`, agar urutan mudah dikendalikan.

## Durasi dan pembagian waktu

Durasi ditentukan pada tab `Meta` dan harus berupa bilangan bulat antara `1` sampai `15` detik.

Aplikasi membagi jumlah frame video secara merata ke seluruh gambar. Jika ada empat gambar, setiap gambar akan tampil selama kurang lebih seperempat durasi video.

Jalur ini menggunakan 16 frame per detik. Perpindahan dari satu gambar ke gambar berikutnya berupa pergantian tampilan, bukan gerakan halus yang dibuat oleh model video.

## Ukuran video

Ukuran keluaran I2V mengikuti ukuran yang dipilih pada tab `Gambar Awal`.

Saat gambar memiliki ukuran atau rasio yang berbeda, aplikasi menyesuaikannya ke kanvas video tanpa meregangkan gambar. Ruang yang tersisa diisi agar semua gambar memiliki ukuran frame yang sama.

## Membuat gambar tambahan

Gunakan tab `Prompt Tambahan` jika membutuhkan beberapa gambar pendukung untuk rangkaian video.

Setiap slot menyediakan:

- `Prompt Positif` untuk menjelaskan gambar;
- `Prompt Negatif` untuk menjelaskan hal yang ingin dihindari;
- `Buat Prompt` untuk meminta bantuan Gemini;
- `Buat Image` untuk membuat gambar.

Setelah gambar dibuat, periksa hasilnya pada tab `Aset`. Karena semua gambar di folder utama akan digunakan oleh I2V, pastikan hanya gambar yang memang ingin dimasukkan ke rangkaian yang berada di sana.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah mengatur durasi, ukuran, atau aset gambar.

Sebelum menjalankan adegan, pastikan:

- tersedia minimal satu gambar di folder aset utama;
- semua gambar yang berada di folder utama memang ingin dimasukkan ke video;
- nama file sudah diberi awalan angka jika urutan cerita penting;
- durasi berada antara `1` sampai `15` detik;
- ukuran pada tab `Gambar Awal` sudah sesuai.

## Contoh penggunaan

1. Buat empat gambar untuk pembuka, tokoh masuk, aksi utama, dan penutup.
2. Pastikan nama file menjadi `01_pembuka.png`, `02_masuk.png`, `03_aksi.png`, dan `04_penutup.png`.
3. Pada tab `Meta`, pilih `i2v` dan atur durasi menjadi `8` detik.
4. Pada tab `Gambar Awal`, pilih ukuran video yang diinginkan.
5. Periksa keempat gambar pada tab `Aset`.
6. Simpan, lalu jalankan adegan.

Video akhir akan menampilkan keempat gambar tersebut secara berurutan, dengan waktu tampil yang dibagi sepanjang durasi video.
