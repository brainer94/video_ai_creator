# IMAGE EDIT

## Fungsi tampilan

Tab `Image Edit` digunakan untuk mengubah satu atau beberapa gambar berdasarkan instruksi teks. Gambar yang ingin diubah dipilih dari aset adegan, lalu hasil edit disimpan kembali sebagai aset baru.

## Pilihan Model

Field `Model` tersedia di dalam tab yang sama:

- `Minimax H3 Image`
- `Qwen 2.1 Image`

Scene lama yang belum menyimpan pilihan model tetap menggunakan `Qwen 2.1 Image`.

## Alur kerja singkat

1. Pilih `Model`.
2. Pilih ukuran keluaran jika memakai `Qwen 2.1 Image`.
3. Pilih gambar pada bagian `Image 1` sampai `Image 10`.
4. Isi `Positive Prompt` dengan perubahan yang diinginkan.
5. Isi `Negative Prompt` jika memakai `Qwen 2.1 Image`.
6. Atur `Jumlah Edit`.
7. Tekan `Edit Gambar`.
8. Periksa hasilnya pada tab `Aset`.

## Minimax H3 Image

Pada `Minimax H3 Image`, gambar pertama adalah gambar utama yang diedit dan menentukan ukuran keluaran. Gambar pertama diproses ke sekitar `4 MP`, kemudian dimensinya disesuaikan ke kelipatan `32` dengan rasio tetap.

Gambar tambahan `Image 2` sampai `Image 10` dikirim langsung sebagai referensi tambahan. Slot kosong tidak dikirim sebagai gambar palsu; gambar yang terisi dikompakkan berdasarkan urutan pilihan.

Untuk engine ini:

- `Negative Prompt` disembunyikan karena workflow tidak memakai negative conditioning;
- kontrol ukuran dan seed disembunyikan;
- token referensi prompt memakai `<Picture 1>`, `<Picture 2>`, dan seterusnya;
- `Buat Prompt` MiniMax memakai blok `system_prompt` dan `task_prompt` dari `minimax_h3_image_edit/edit-en.txt`, lalu dikirim ke Gemini bersama gambar referensi multimodal. Workflow JSON hanya digunakan untuk eksekusi ComfyUI.

## Memilih gambar

Gunakan bagian `Image 1` sampai `Image 10` untuk memilih gambar yang akan diedit. Tidak semua slot harus diisi. Gunakan hanya slot yang diperlukan dan pastikan gambar yang dipilih memang berasal dari adegan aktif. Gambar yang benar-benar dipilih dikirim berurutan tanpa placeholder.

## Menulis instruksi edit

### Positive Prompt

Jelaskan perubahan yang diinginkan secara langsung, misalnya mengganti pakaian, mengubah latar, menambahkan objek, atau memperbaiki pencahayaan.

Sebutkan bagian yang harus tetap dipertahankan bila perubahan hanya berlaku pada sebagian gambar.

### Negative Prompt (Qwen 2.1 Image)

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

`Ukuran` menentukan ukuran hasil akhir untuk `Qwen 2.1 Image`. Pada `Minimax H3 Image`, ukuran mengikuti gambar pertama setelah resize internal sekitar 4 MP dan penyesuaian multiple 32.

Jika `Random Seed` aktif pada `Qwen 2.1 Image`, hasil dapat berbeda pada setiap proses. Untuk mencoba kembali hasil yang sama, matikan `Random Seed` dan isi `Seed Statik` dengan angka positif. Pada `Minimax H3 Image`, seed dibuat internal oleh runtime dan kontrolnya tidak ditampilkan.

## Menyimpan dan menjalankan

Simpan adegan sebelum menjalankan edit gambar. Pastikan:

- ComfyUI dapat diakses melalui `Konfigurasi Umum`;
- minimal satu gambar edit sudah dipilih;
- `Positive Prompt` sudah berisi instruksi;
- ukuran keluaran sudah sesuai jika menggunakan `Qwen 2.1 Image`;
- jumlah edit tidak lebih besar dari yang diperlukan.

Hasil edit dapat dilihat dan dipilih kembali melalui tab `Aset`.

## Model ComfyUI

`Minimax H3 Image` memakai diffusion model dan VAE MiniMax H3 Image serta text encoder MiniMax H3 yang sama dengan workflow video. Model dapat dipilih dari katalog pada `Konfigurasi Umum` melalui kelompok `MiniMax H3 Image`.
