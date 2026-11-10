# GAMBAR AWAL

## Fungsi tampilan

Tab `Gambar Awal` digunakan untuk membuat gambar pertama yang menjadi dasar adegan. Gambar yang dihasilkan akan tersimpan sebagai aset pada adegan aktif.

Gambar ini dapat digunakan sebagai titik awal untuk MiniMax H3 I2V atau S2V, sebagai gambar sumber untuk `image_pan` dan `image_zoom`, serta sebagai salah satu gambar pada jalur video biasa.

## Alur kerja singkat

1. Pilih model gambar dan ukuran keluaran.
2. Tulis `Prompt Positif` untuk menjelaskan gambar yang diinginkan.
3. Isi `Prompt Negatif` bila ada hal yang ingin dihindari.
4. Pilih LoRA bila diperlukan.
5. Tekan `Buat Prompt` bila ingin meminta bantuan Gemini, atau susun prompt langsung.
6. Simpan adegan.
7. Tekan `Buat Gambar Awal` pada toolbar.
8. Periksa hasilnya pada tab `Aset`.

## Pengaturan gambar

### Model

Pilih model yang digunakan untuk membuat gambar. Pilihan yang tersedia adalah `Z-Image Turbo`, `Flux.2`, dan `Gemini`.

Model `Gemini` menggunakan pilihan model gambar Gemini pada kolom `Model Gemini`. Model lain menggunakan ComfyUI dan membutuhkan model yang sesuai sudah tersedia di sana.

### Ukuran

Menentukan ukuran gambar keluaran. Pilih ukuran yang sesuai dengan orientasi video dan kebutuhan adegan.

Ukuran gambar ditentukan melalui pilihan `Ukuran` pada tab ini.

### Random Seed dan Seed Statik

Jika `Random Seed` aktif, setiap pembuatan gambar dapat menghasilkan variasi baru.

Jika ingin mencoba kembali hasil yang sama, matikan `Random Seed` lalu isi `Seed Statik` dengan angka positif.

### Pakai Lora

Aktifkan bila ingin menggunakan LoRA untuk menambahkan gaya, karakter, atau ciri visual tertentu.

### Nama Lora

Pilih LoRA dari daftar yang tersedia untuk model yang sedang dipilih. LoRA harus sudah berada di ComfyUI agar dapat digunakan.

### Kekuatan Lora

Menentukan seberapa kuat pengaruh LoRA terhadap gambar. Mulailah dari nilai yang wajar, lalu sesuaikan bila ciri LoRA terlalu lemah atau terlalu dominan.

### Trigger Word Lora

Isi kata atau frasa pemicu jika petunjuk LoRA memerlukannya. Letakkan kata tersebut pada `Prompt Positif` agar ciri LoRA muncul sesuai tujuan.

## Menyusun prompt

### Prompt Positif

Jelaskan subjek, penampilan, lingkungan, pencahayaan, komposisi, gaya, dan detail penting lain yang harus terlihat pada gambar.

### Prompt Negatif

Tuliskan hal-hal yang ingin dihindari, misalnya anatomi buruk, tulisan acak, atau objek yang tidak diinginkan.

Tidak semua model membutuhkan prompt negatif. Jika kolom tidak digunakan oleh model yang dipilih, ikuti keadaan kolom yang ditampilkan aplikasi.

### Buat Prompt

Tekan `Buat Prompt` bila ingin meminta Gemini membantu menyusun prompt. Hasilnya dapat diperiksa dan diubah langsung sebelum gambar dibuat.

Prompt juga dapat ditulis sepenuhnya secara manual.

## Menyimpan dan membuat gambar

Simpan adegan setelah mengubah pengaturan atau prompt, lalu tekan `Buat Gambar Awal`.

Sebelum membuat gambar, pastikan:

- ComfyUI dapat diakses melalui `Konfigurasi Umum`;
- model yang dipilih sudah tersedia;
- LoRA yang dipilih sudah tersedia bila `Pakai Lora` aktif;
- prompt positif sudah menjelaskan gambar yang diinginkan.

Setelah selesai, buka tab `Aset` untuk melihat gambar dan menggunakannya pada proses video berikutnya.
