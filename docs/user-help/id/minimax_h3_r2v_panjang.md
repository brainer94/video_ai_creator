# MINIMAX-H3_R2V-PANJANG

## Fungsi tampilan

`MINIMAX-H3_R2V-PANJANG` digunakan untuk membuat video yang lebih panjang melalui beberapa proses yang saling tersambung.

Setiap proses membuat satu bagian video dan memiliki prompt sendiri. Setelah sebuah proses selesai, frame terakhir dari hasilnya dipakai secara otomatis sebagai referensi tambahan untuk proses berikutnya. Dengan cara ini, perubahan adegan dapat dilanjutkan dari bagian sebelumnya.

Tersedia empat proses: `Proses 1`, `Proses 2`, `Proses 3`, dan `Proses 4`.

## Alur kerja singkat

1. Pada tab `Meta`, pilih tipe adegan `minimax-h3_r2v-panjang`.
2. Atur durasi adegan pada tab `Meta`. Durasi ini berlaku untuk setiap proses yang aktif.
3. Jika membutuhkan gambar referensi baru, buka tab `Gambar Awal` dan buat gambar tersebut.
4. Buka tab `MINIMAX-H3_R2V-PANJANG`.
5. Pilih referensi gambar, audio, dan video yang akan digunakan bersama.
6. Tentukan jumlah proses melalui `Jumlah lanjutan`.
7. Susun prompt untuk setiap proses yang digunakan.
8. Atur pengaturan umum seperti ukuran, LoRA, mode, dan jumlah step.
9. Simpan adegan.
10. Jalankan rangkaian proses.

## Referensi global

Referensi yang dipilih pada bagian awal digunakan oleh seluruh proses yang aktif.

### Referensi gambar

Pilih sampai empat gambar global. Gambar-gambar ini dapat digunakan untuk menjaga identitas subjek, tampilan objek, pakaian, lingkungan, gaya visual, atau unsur lain yang ingin dipertahankan sepanjang rangkaian video.

Urutan slot gambar tetap penting. Gambar pada slot pertama menjadi `Picture 1`, gambar pada slot kedua menjadi `Picture 2`, dan seterusnya. Jika prompt menyebut nomor gambar, gunakan nomor sesuai urutan slot tersebut.

### Referensi audio

Pilih sampai tiga audio global. Audio dapat membantu model memahami karakter suara, ucapan, atau unsur audio lain yang perlu dipertahankan.

Urutan slot audio juga tetap penting. Audio pertama menjadi `Audio 1`, audio kedua menjadi `Audio 2`, dan audio ketiga menjadi `Audio 3`.

### Referensi video

Pilih paling banyak satu video global. Video dapat membantu memberikan contoh gerakan, komposisi, atau suasana visual.

Tidak harus mengisi semua jenis referensi. Namun, setidaknya satu referensi gambar, audio, atau video harus dipilih agar adegan dapat dijalankan.

Referensi global yang dipilih harus tetap tersedia di aset adegan saat proses dijalankan. Hindari memilih file yang sama lebih dari satu kali.

## Frame yang diteruskan antarproses

Frame terakhir dari proses sebelumnya bukan dipilih secara manual. Aplikasi mengambilnya otomatis setelah proses tersebut selesai.

Alurnya sebagai berikut:

```text
Proses 1 selesai
        ↓
Frame terakhir Proses 1 menjadi referensi tambahan Proses 2
        ↓
Proses 2 selesai
        ↓
Frame terakhir Proses 2 menjadi referensi tambahan Proses 3
        ↓
Proses 3 selesai
        ↓
Frame terakhir Proses 3 menjadi referensi tambahan Proses 4
```

Pada setiap proses setelah Proses 1, model menerima:

- semua referensi global yang dipilih;
- satu frame tambahan dari hasil proses sebelumnya.

Frame tambahan tersebut membantu proses berikutnya melanjutkan tampilan dari akhir video sebelumnya. Karena itu, tidak perlu menyediakan atau memilih slot khusus untuk frame tersebut.

Jika rangkaian dimulai dari Proses 1, frame untuk proses berikutnya akan tersedia secara otomatis setelah proses sebelumnya selesai. Jika rangkaian dimulai langsung dari proses lanjutan melalui `Run mulai dari tab`, hasil proses-proses sebelumnya harus sudah tersedia.

## Pengaturan umum

Pengaturan ini berada pada bagian awal rangkaian dan berlaku untuk seluruh proses.

### Ukuran

Menentukan ukuran video yang dibuat. Pilih ukuran yang sesuai dengan orientasi dan kebutuhan project.

### Pakai Lora

Centang `Pakai Lora` bila ingin menggunakan LoRA pada seluruh proses yang dijalankan. Jika tidak dicentang, LoRA 1 dan LoRA 2 dilewati pada setiap proses.

### LoRA dan Kekuatan

Pilih LoRA pertama jika ingin menambahkan gaya, karakter, atau ciri visual tertentu. `Kekuatan` mengatur seberapa besar pengaruh LoRA tersebut.

LoRA kedua bersifat opsional dan dapat digunakan untuk menggabungkan dua pengaruh visual. Atur kekuatannya sesuai kebutuhan.

### Hapus Sound

Jika diaktifkan, suara dari video hasil proses akan dihapus.

### Mode Cepat

Menggunakan pengaturan MiniMax H3 yang dirancang untuk pemrosesan lebih cepat.

### Jumlah Step

Menentukan jumlah langkah pemrosesan. Nilai yang lebih besar dapat membuat proses lebih lama dan dapat memengaruhi hasil video.

## Menentukan jumlah proses

`Jumlah lanjutan` menentukan berapa banyak proses yang digunakan:

- `0` berarti hanya `Proses 1`;
- `1` berarti `Proses 1` dan `Proses 2`;
- `2` berarti `Proses 1` sampai `Proses 3`;
- `3` berarti seluruh proses sampai `Proses 4`.

Tab proses yang tidak digunakan akan disembunyikan. Setiap proses yang aktif memiliki prompt dan hasil video bagiannya sendiri.

## Editor prompt setiap proses

Setiap proses memiliki editor prompt sendiri. Prompt pada satu proses tidak otomatis mengubah prompt pada proses lain.

Editor terdiri dari bagian-bagian berikut:

1. `Definisi Subjek`
2. `Ringkasan`
3. `Analisis Pemertahanan Referensi`
4. `Deskripsi Rinci`
5. `Suasana Suara Keseluruhan`
6. `Musik Latar`

Isi prompt untuk model menggunakan bahasa Inggris. Dialog, lirik, atau teks yang memang harus diucapkan atau ditampilkan dapat tetap menggunakan bahasa aslinya.

### Definisi Subjek

Jelaskan subjek utama dan hubungannya dengan referensi.

Contoh:

```text
<Picture 1> shows a woman standing in a kitchen. <Subject 1> is the woman.
<Picture 2> shows the kitchen background and its main objects.
```

Gunakan nomor referensi yang benar-benar dipilih. Jangan menyebut `<Picture 3>` jika hanya dua gambar global yang tersedia.

### Ringkasan

Jelaskan secara singkat kejadian utama yang ingin dibuat pada proses tersebut.

Contoh:

```text
The woman prepares tea in the kitchen while the camera slowly moves closer.
```

### Analisis Pemertahanan Referensi

Jelaskan bagian referensi yang harus dipertahankan, misalnya identitas wajah, pakaian, bentuk objek, tata ruang, pencahayaan, atau suasana.

Contoh:

```text
<Subject 1>: fully_preserved — preserve her identity, face, clothing, and hair.
<Picture 2>: fully_preserved — preserve the kitchen layout and lighting direction.
```

Untuk Proses 2 dan seterusnya, jelaskan juga bahwa adegan harus melanjutkan frame terakhir proses sebelumnya jika hal tersebut penting bagi alur video.

### Deskripsi Rinci

Bagian ini menjelaskan kejadian dari awal sampai akhir proses. Gunakan beberapa `Bidikan` jika adegan memiliki perubahan aksi, kamera, atau kejadian yang berbeda.

Setiap bidikan memiliki:

- waktu mulai dan selesai;
- gambaran visual;
- aksi;
- kamera;
- dialog atau lirik;
- suara yang berasal dari kejadian di dalam adegan.

### Suasana Suara Keseluruhan

Jelaskan suara lingkungan yang berlangsung sepanjang proses, misalnya suasana ruangan, suara angin, atau keramaian yang terus terdengar.

### Musik Latar

Jelaskan musik yang hanya didengar oleh penonton. Isi `N/A` jika tidak ada musik latar.

## Kartu Bidikan

### Menambah bidikan

Tekan `Tambah Bidikan` untuk menambahkan bagian baru pada linimasa proses.

Setiap bidikan diberi nomor otomatis, misalnya `Bidikan 1`, `Bidikan 2`, dan seterusnya.

### Menghapus bidikan

Tekan `Hapus` pada kartu bidikan yang ingin dihapus. Setiap proses yang digunakan harus tetap memiliki setidaknya satu bidikan.

### Waktu bidikan

Isi waktu dalam satuan detik.

Contoh:

```text
Bidikan 1: Mulai 0.00 — Selesai 1.00
Bidikan 2: Mulai 1.00 — Selesai 3.00
```

Aturan waktunya:

- bidikan pertama harus dimulai dari `0.00` detik;
- waktu selesai harus lebih besar daripada waktu mulai;
- bidikan berikutnya dimulai setelah bidikan sebelumnya;
- bidikan tidak boleh saling bertumpang tindih;
- waktu bidikan tidak boleh melewati durasi adegan yang berlaku pada proses tersebut.

Gunakan `Akhir = durasi` untuk mengatur waktu selesai bidikan terakhir sama dengan durasi proses.

### Gambaran Visual

Jelaskan subjek, komposisi, pakaian, lingkungan, pencahayaan, properti, serta perubahan visual yang terlihat.

### Aksi

Jelaskan gerakan subjek atau perubahan objek selama bidikan berlangsung.

### Kamera

Jelaskan pembingkaian dan gerakan kamera jika diperlukan.

### Dialog / Lirik

Masukkan dialog atau lirik jika ada. Jika tidak ada, tulis `No dialogue.`

### Suara dalam Adegan

Jelaskan suara yang berasal dari kejadian di dalam adegan, seperti langkah kaki, pintu, air, atau suara objek.

## Meminta bantuan membuat prompt

Jika ingin mendapatkan bantuan Gemini, atur `Jumlah lanjutan` sesuai jumlah proses yang ingin dibuat, isi `Perintah kepada LLM`, lalu tekan `Buat Prompt` pada salah satu proses.

Gemini akan menggunakan informasi adegan, referensi global, dan perintah yang diberikan untuk menyusun rangkaian prompt sesuai jumlah proses yang diminta.

Jika tombol ditekan pada Proses 3, Gemini akan membuat prompt Proses 1, Proses 2, dan Proses 3 sekaligus dalam satu rangkaian yang saling berkesinambungan. Jika hanya satu perintah yang diisi, perintah tersebut dipakai sebagai arahan umum untuk seluruh proses. Jika beberapa perintah diisi, masing-masing perintah digunakan sebagai arahan untuk proses yang sesuai.

Proses 1 tidak memiliki frame awal otomatis. Pada proses berikutnya, gambar tambahan yang disediakan aplikasi diperlakukan sebagai frame awal video proses tersebut. Hasil seluruh proses dimasukkan ke editor masing-masing setelah semua prompt berhasil divalidasi.

Periksa kembali hasilnya sebelum menyimpan, terutama:

- subjek yang harus dipertahankan;
- hubungan dengan referensi gambar, audio, dan video;
- kesinambungan dengan proses sebelumnya;
- urutan kejadian dan waktu setiap bidikan;
- dialog, suara dalam adegan, dan musik latar.

`Deskripsi Adegan` pada tab `Meta` membantu Gemini memahami konteks keseluruhan, tetapi boleh dikosongkan.

## Run mulai dari tab

Biasanya rangkaian dimulai dari `Tab 1 (normal)` atau `Proses 1`.

Gunakan `Run mulai dari tab` jika ingin membuat ulang mulai dari proses tertentu. Contohnya, setelah Proses 1 sudah berhasil dibuat, Anda dapat memilih Proses 2 untuk membuat ulang bagian lanjutan.

Saat memulai dari proses lanjutan:

- video dari semua proses sebelumnya harus sudah tersedia;
- frame terakhir dari proses sebelumnya akan digunakan sebagai referensi tambahan;
- proses yang dijalankan harus memiliki prompt yang valid;
- seluruh bagian video tetap akan digabungkan dalam urutan Proses 1, Proses 2, Proses 3, dan Proses 4.

Gunakan pilihan ini hanya jika hasil proses sebelumnya masih tersedia dan ingin dipakai kembali.

## Video akhir

Setiap proses aktif menghasilkan satu bagian video. Video akhir adalah gabungan dari seluruh bagian video yang aktif, disusun sesuai urutan prosesnya.

Contoh jika tiga proses aktif:

```text
Proses 1 → bagian video pertama
Proses 2 → bagian video kedua
Proses 3 → bagian video ketiga

Video akhir = Proses 1 + Proses 2 + Proses 3
```

Frame terakhir dari sebuah proses digunakan untuk menyambungkan proses berikutnya, tetapi tidak menjadi bagian video tambahan yang terpisah.

## Menyimpan dan menjalankan adegan

Simpan adegan setelah selesai mengubah referensi, pengaturan, atau prompt.

Sebelum dijalankan, pastikan:

- jumlah proses sudah sesuai kebutuhan;
- setidaknya satu referensi global dipilih;
- referensi global masih tersedia di aset adegan;
- setiap proses aktif memiliki prompt yang lengkap;
- bidikan pertama setiap proses dimulai dari `0.00` detik;
- waktu bidikan tersusun berurutan dan tidak bertumpang tindih;
- jumlah step berada pada nilai yang diterima aplikasi;
- hasil proses sebelumnya tersedia jika memakai `Run mulai dari tab` lanjutan;
- ComfyUI dapat diakses.

## Contoh penggunaan dua proses

1. Pada tab `Meta`, pilih `minimax-h3_r2v-panjang`.
2. Atur durasi adegan.
3. Pada `Jumlah lanjutan`, pilih `1` agar `Proses 1` dan `Proses 2` digunakan.
4. Pilih referensi global gambar, audio, atau video.
5. Pada `Proses 1`, susun prompt dari awal sampai akhir bagian pertama.
6. Simpan adegan, lalu jalankan rangkaian dengan satu proses aktif terlebih dahulu jika ingin memeriksa hasil Proses 1.
7. Pada `Proses 2`, susun prompt untuk kejadian yang melanjutkan akhir Proses 1.
8. Simpan adegan, lalu jalankan rangkaiannya.

Aplikasi akan memakai frame terakhir Proses 1 secara otomatis sebagai referensi tambahan untuk Proses 2. Video akhir akan menggabungkan bagian Proses 1 dan Proses 2 secara berurutan.
