# IMAGE ZOOM

## Fungsi tampilan

`Image Zoom` digunakan untuk membuat video dari satu gambar dengan gerakan kamera mendekat atau menjauh.

Jalur ini tidak membuat gambar baru dengan AI. Aplikasi membuat rangkaian frame dari gambar yang tersedia dengan memperbesar atau memperkecil tampilan secara bertahap.

## Alur kerja singkat

1. Pada tab `Meta`, pilih tipe adegan `image_zoom`.
2. Siapkan gambar di aset adegan.
3. Atur durasi antara `1` sampai `15` detik.
4. Buka tab `Image Zoom`.
5. Pilih ukuran video.
6. Pilih arah zoom.
7. Pilih titik fokus.
8. Atur kekuatan zoom.
9. Simpan adegan.
10. Jalankan adegan melalui tombol proses.

## Gambar yang digunakan

Aplikasi menggunakan gambar terbaru yang berada langsung di folder aset adegan. Jika ada beberapa gambar, gambar dengan waktu perubahan terakhir akan digunakan.

Pastikan bagian yang ingin ditonjolkan berada pada area gambar yang sesuai dengan titik fokus yang dipilih.

## Pengaturan tampilan

### Ukuran

Menentukan ukuran video keluaran. Pilih ukuran sesuai orientasi dan kebutuhan project.

### Arah Zoom

Menentukan arah gerakan kamera:

- `Zoom In (Default)`: tampilan dimulai lebih lebar lalu mendekat ke gambar;
- `Zoom Out`: tampilan dimulai lebih dekat lalu menjauh hingga tampilan lebih lebar.

### Titik Fokus

Menentukan bagian gambar yang dijaga sebagai pusat perhatian saat zoom berlangsung.

Pilihan yang tersedia:

- `Tengah`;
- `Atas Kiri`, `Atas Tengah`, `Atas Kanan`;
- `Tengah Kiri`, `Tengah Kanan`;
- `Bawah Kiri`, `Bawah Tengah`, `Bawah Kanan`.

Contohnya, pilih `Atas Kanan` jika subjek utama berada di bagian kanan atas gambar.

### Kekuatan Zoom

Menentukan seberapa jauh perubahan ukuran tampilan.

Nilai berada antara `1.0` sampai `1.5`:

- `1.0` menghasilkan gerakan paling ringan;
- nilai yang lebih besar menghasilkan gerakan zoom yang lebih kuat.

## Durasi

Durasi ditentukan pada tab `Meta` dan berlaku untuk video `Image Zoom`.

Nilai yang tersedia adalah bilangan bulat antara `1` sampai `15` detik.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah mengubah durasi, ukuran, arah zoom, titik fokus, atau kekuatan zoom.

Sebelum menjalankan adegan, pastikan:

- tersedia minimal satu gambar di folder aset utama adegan;
- gambar yang ingin digunakan merupakan gambar terbaru;
- arah zoom sudah sesuai;
- titik fokus berada di area subjek utama;
- kekuatan zoom berada antara `1.0` sampai `1.5`;
- durasi berada antara `1` sampai `15` detik.

## Contoh penggunaan

1. Tambahkan gambar seorang tokoh yang berada di bagian kanan atas gambar.
2. Pada tab `Meta`, pilih `image_zoom` dan atur durasi menjadi `6` detik.
3. Buka tab `Image Zoom`.
4. Pilih `Zoom In (Default)`.
5. Pilih titik fokus `Atas Kanan`.
6. Atur kekuatan zoom menjadi `1.3`.
7. Simpan, lalu jalankan adegan.

Hasilnya adalah video yang perlahan mendekati tokoh pada area kanan atas gambar.
