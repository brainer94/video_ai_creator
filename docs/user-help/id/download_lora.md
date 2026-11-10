# DOWNLOAD LORA

## Fungsi tampilan

Dialog `Download LoRA` digunakan untuk menambahkan satu file LoRA ke ComfyUI. Kategori yang dipilih menentukan folder tempat file disimpan sehingga LoRA dapat muncul pada pilihan model yang sesuai.

## Alur kerja singkat

1. Salin alamat LoRA dari Hugging Face atau Civitai.
2. Tempel alamat tersebut pada `URL LoRA`.
3. Pilih `Kategori`.
4. Isi `Nama file` dengan nama file yang ingin digunakan.
5. Periksa `Folder tujuan`.
6. Tekan `Download LoRA`.
7. Tunggu sampai status menyatakan selesai.
8. Pilih LoRA tersebut pada tab adegan yang membutuhkannya.

## Isi dialog

### URL LoRA

Masukkan URL file atau halaman download LoRA dari Hugging Face atau Civitai.

Gunakan alamat yang dapat dibaca oleh ComfyUI-Model-Manager. Untuk file privat, aksesnya harus sudah tersedia pada ComfyUI-Model-Manager.

### Kategori

Pilih tujuan penggunaan LoRA:

- `MiniMax H3`;
- `Flux 2`;
- `Z Image`.

### Nama file

Masukkan nama file, biasanya dengan akhiran `.safetensors`. Gunakan nama file yang sama dengan yang ingin dipilih nanti pada daftar LoRA.

Jangan memakai nama yang sama dengan LoRA lain bila ingin menyimpan keduanya.

### Folder tujuan

Bagian ini menunjukkan folder ComfyUI yang dipilih berdasarkan kategori. Pengguna tidak perlu menulis folder tersebut secara manual.

### Status download

Menampilkan pemeriksaan koneksi, proses antrean, persentase download, serta pesan berhasil atau gagal.

## Setelah download selesai

Setelah file selesai diunduh, aplikasi memperbarui daftar LoRA ComfyUI. Jika nama belum muncul pada pilihan LoRA, tunggu pembaruan selesai lalu tutup dan buka kembali pilihan tersebut atau ulangi pemeriksaan pada `Konfigurasi Umum`.

## Jika download gagal

- pastikan URL dapat dibuka dan menunjuk ke LoRA yang benar;
- pastikan kategori sesuai dengan model yang akan memakai LoRA;
- pastikan ComfyUI dan ComfyUI-Model-Manager sedang aktif;
- periksa pesan pada area status;
- bila ComfyUI baru saja direstart, tunggu sampai benar-benar siap lalu coba lagi.

Token atau akses privat Hugging Face/Civitai mengikuti konfigurasi ComfyUI-Model-Manager. Aplikasi tidak meminta token tersebut di dialog ini.
