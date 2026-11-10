# IMAGE PAN

## Fungsi tampilan

`Image Pan` digunakan untuk membuat video dari satu gambar dengan gerakan kamera mendatar dari satu sisi ke sisi lainnya.

Jalur ini tidak membuat gambar baru dengan AI. Aplikasi menggerakkan area tampilan di atas gambar yang sudah tersedia, lalu menghasilkan video pendek.

## Alur kerja singkat

1. Pada tab `Meta`, pilih tipe adegan `image_pan`.
2. Siapkan gambar di aset adegan.
3. Atur durasi antara `1` sampai `15` detik.
4. Buka tab `Image Pan`.
5. Pilih ukuran portrait.
6. Pilih arah gerakan.
7. Simpan adegan.
8. Jalankan adegan melalui tombol proses.

## Gambar yang digunakan

Aplikasi menggunakan gambar terbaru yang berada langsung di folder aset adegan. Jika ada beberapa gambar, gambar dengan waktu perubahan terakhir akan digunakan.

Pastikan gambar memiliki komposisi yang cukup lebar agar gerakan pan dapat terlihat. Jika gambar terlalu sempit, gerakan dari satu sisi ke sisi lainnya akan sangat terbatas.

## Pengaturan tampilan

### Ukuran (Portrait)

Menentukan ukuran video keluaran dengan orientasi portrait. Tinggi gambar keluaran harus lebih besar daripada lebarnya.

Pilih ukuran yang sesuai dengan project. Gambar sumber akan disesuaikan agar tingginya memenuhi area video tanpa diregangkan.

### Arah

Menentukan arah gerakan kamera:

- `Dari Kanan`: video dimulai dari sisi kanan gambar lalu bergerak menuju sisi kiri;
- `Dari Kiri`: video dimulai dari sisi kiri gambar lalu bergerak menuju sisi kanan.

Gerakan pan berlangsung penuh dari sisi awal ke sisi akhir selama durasi video.

## Durasi

Durasi ditentukan pada tab `Meta` dan berlaku untuk video `Image Pan`.

Nilai yang tersedia adalah bilangan bulat antara `1` sampai `15` detik.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah mengubah durasi, ukuran, atau arah gerakan.

Sebelum menjalankan adegan, pastikan:

- tersedia minimal satu gambar di folder aset utama adegan;
- gambar yang ingin digunakan merupakan gambar terbaru;
- ukuran yang dipilih berorientasi portrait;
- arah gerakan sudah sesuai;
- durasi berada antara `1` sampai `15` detik.

## Contoh penggunaan

1. Tambahkan gambar pemandangan yang lebar ke aset adegan.
2. Pada tab `Meta`, pilih `image_pan` dan atur durasi menjadi `8` detik.
3. Buka tab `Image Pan`.
4. Pilih ukuran portrait.
5. Pilih `Dari Kanan` jika ingin tampilan bergerak dari kanan ke kiri.
6. Simpan, lalu jalankan adegan.

Hasilnya adalah video portrait yang menampilkan pergeseran mendatar secara halus pada gambar tersebut.
