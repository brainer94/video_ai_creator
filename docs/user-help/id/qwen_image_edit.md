# QWEN IMAGE EDIT

## Fungsi tampilan

Tab `Qwen Image Edit` digunakan untuk mengubah satu atau beberapa gambar berdasarkan instruksi teks. Gambar yang ingin diubah dipilih dari aset adegan, lalu hasil edit disimpan kembali sebagai aset baru.

## Alur kerja singkat

1. Pilih ukuran keluaran.
2. Pilih gambar pada bagian `Image 1` sampai `Image 10`.
3. Isi `Positive Prompt` dengan perubahan yang diinginkan.
4. Isi `Negative Prompt` bila ada hal yang ingin dihindari.
5. Atur `Jumlah Edit`.
6. Tekan `Edit Gambar`.
7. Periksa hasilnya pada tab `Aset`.

## Memilih gambar

Gunakan bagian `Image 1` sampai `Image 10` untuk memilih gambar yang akan diedit. Tidak semua slot harus diisi. Gunakan hanya slot yang diperlukan dan pastikan gambar yang dipilih memang berasal dari adegan aktif.

## Menulis instruksi edit

### Positive Prompt

Jelaskan perubahan yang diinginkan secara langsung, misalnya mengganti pakaian, mengubah latar, menambahkan objek, atau memperbaiki pencahayaan.

Sebutkan bagian yang harus tetap dipertahankan bila perubahan hanya berlaku pada sebagian gambar.

### Negative Prompt

Tuliskan hasil yang harus dihindari, misalnya wajah berubah, objek utama hilang, tangan cacat, atau tulisan tidak terbaca.

## Jumlah Edit

Menentukan berapa banyak hasil yang dibuat dari pilihan gambar dan prompt yang sama. Nilai yang lebih besar menghasilkan lebih banyak variasi dan dapat membutuhkan waktu serta ruang penyimpanan lebih besar.

## Meminta bantuan membuat prompt

Bagian `Gambar Referensi untuk Buat Prompt` digunakan untuk memilih gambar yang akan dilihat Gemini ketika membantu menyusun instruksi edit.

1. Pilih satu atau beberapa gambar pada bagian tersebut.
2. Isi `Prompt` dengan keinginan perubahan.
3. Tekan `Buat Prompt`.
4. Periksa hasilnya pada `Positive Prompt` sebelum menekan `Edit Gambar`.

`Buat Prompt` hanya bantuan. Instruksi edit tetap dapat ditulis dan disunting langsung.

## Ukuran dan hasil yang dapat diulang

`Ukuran` menentukan ukuran hasil akhir.

Jika `Random Seed` aktif, hasil dapat berbeda pada setiap proses. Untuk mencoba kembali hasil yang sama, matikan `Random Seed` dan isi `Seed Statik` dengan angka positif.

## Menyimpan dan menjalankan

Simpan adegan sebelum menjalankan edit gambar. Pastikan:

- ComfyUI dapat diakses melalui `Konfigurasi Umum`;
- minimal satu gambar edit sudah dipilih;
- `Positive Prompt` sudah berisi instruksi;
- ukuran keluaran sudah sesuai;
- jumlah edit tidak lebih besar dari yang diperlukan.

Hasil edit dapat dilihat dan dipilih kembali melalui tab `Aset`.
