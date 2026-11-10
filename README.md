# Video AI Creator

Video AI Creator adalah aplikasi desktop untuk membuat video berbasis adegan. Pengguna dapat membuat project, menyiapkan gambar dan suara, menyusun prompt melalui editor interaktif, lalu menjalankan proses pembuatan video melalui ComfyUI.

Aplikasi ini juga menyediakan bantuan Gemini untuk menyusun prompt, pembuatan suara, pembuatan gambar, penggabungan video, serta pengelolaan model dan LoRA melalui ComfyUI.

## Kebutuhan

Siapkan hal-hal berikut sebelum memasang aplikasi:

- Windows 10/11 atau Linux desktop;
- Git untuk mengambil source project;
- Python 3.12 atau versi Python yang kompatibel dengan `requirements.txt`;
- FFmpeg dan FFprobe untuk pengolahan video dan audio;
- ComfyUI yang sudah berjalan dan dapat diakses dari komputer tempat aplikasi ini dijalankan;
- koneksi internet saat memasang dependency, memakai Gemini, atau mengunduh model;
- ruang penyimpanan yang cukup untuk model, LoRA, aset, dan hasil video.

File `requirements.txt` memasang komponen Python untuk:

- antarmuka desktop: PySide6;
- komunikasi HTTP dan API: Requests serta Tenacity;
- pengolahan gambar dan video: Pillow, NumPy, OpenCV, ImageIO, MoviePy, dan ImageIO-FFmpeg;
- transkripsi dan caption: Faster-Whisper;
- tampilan progres dan koneksi pendukung: TQDM dan WebSocket Client.

FFmpeg tetap harus dipasang sebagai program sistem karena dipakai langsung untuk menggabungkan video, memproses audio, mengambil frame, dan membaca informasi media. ComfyUI bukan bagian dari `requirements.txt`; ComfyUI dipasang dan dijalankan terpisah.

Kebutuhan GPU, driver NVIDIA, CUDA, dan VRAM mengikuti model yang dipakai di ComfyUI. Video AI Creator dapat dibuka tanpa GPU, tetapi proses generasi ComfyUI biasanya membutuhkan GPU yang sesuai.

Fitur berikut memerlukan Gemini API key:

- `Buat Prompt`;
- pembuatan suara Gemini;
- pembuatan gambar Gemini.

## Instalasi Windows

### 1. Pasang Git

Unduh Git dari [git-scm.com](https://git-scm.com/downloads), lalu pasang dengan pengaturan bawaan.

Buka PowerShell dan pastikan Git tersedia:

```powershell
git --version
```

### 2. Pasang Python

Unduh Python dari [python.org](https://www.python.org/downloads/). Saat memasang Python, aktifkan pilihan **Add Python to PATH**.

Pastikan Python tersedia:

```powershell
py --version
```

### 3. Pasang FFmpeg

Unduh FFmpeg dari [ffmpeg.org](https://ffmpeg.org/download.html), lalu tambahkan folder `bin` FFmpeg ke `PATH` Windows.

Alternatif jika `winget` tersedia:

```powershell
winget install --id Gyan.FFmpeg.Shared -e
```

Tutup dan buka kembali PowerShell, lalu periksa:

```powershell
ffmpeg -version
ffprobe -version
```

### 4. Ambil project

Clone repository project, lalu masuk ke foldernya:

```powershell
git clone <URL_REPOSITORY_PROJECT>
cd video_ai_creator
```

Jika menerima project dalam bentuk ZIP, ekstrak ZIP tersebut lalu buka PowerShell di folder `video_ai_creator`.

### 5. Buat virtual environment dan pasang dependency

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Jika PowerShell menolak menjalankan `Activate.ps1`, gunakan Python dari virtual environment secara langsung tanpa aktivasi:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 6. Masukkan Gemini API key

Buat file `keys.cfg` di folder utama project:

```ini
GEMINIKEY=isi_api_key_gemini_di_sini
```

Jangan membagikan atau mengunggah file tersebut. File `keys.cfg` sudah dikecualikan dari Git.

### 7. Jalankan aplikasi

```powershell
.\.venv\Scripts\python.exe scene_manager_ui.py
```

Atau jalankan:

```powershell
.\run_ui.bat
```

Saat belum ada project yang dibuka, aplikasi menampilkan panduan awal. Buat project baru melalui menu aplikasi, lalu buka project tersebut sebelum membuat adegan.

## Instalasi Linux

Contoh berikut menggunakan Linux berbasis Debian/Ubuntu.

### 1. Pasang Git, Python, dan FFmpeg

```bash
sudo apt update
sudo apt install -y git python3 python3-venv ffmpeg
```

Pastikan semuanya tersedia:

```bash
git --version
python3 --version
ffmpeg -version
ffprobe -version
```

Python 3.12 direkomendasikan. Jika `python3` pada distribusi Linux terlalu lama, pasang Python 3.12 dari sumber resmi distribusi tersebut terlebih dahulu.

### 2. Ambil project

```bash
git clone <URL_REPOSITORY_PROJECT>
cd video_ai_creator
```

Jika menerima project dalam bentuk arsip, ekstrak arsip tersebut lalu masuk ke folder project.

### 3. Buat virtual environment dan pasang dependency

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Masukkan Gemini API key

Buat file `keys.cfg` di folder utama project:

```ini
GEMINIKEY=isi_api_key_gemini_di_sini
```

Jangan memasukkan file tersebut ke repository atau membagikannya kepada orang lain.

### 5. Jalankan aplikasi

Linux harus memiliki sesi desktop agar jendela aplikasi dapat dibuka.

```bash
./.venv/bin/python scene_manager_ui.py
```

Atau:

```bash
chmod +x run_ui.sh
./run_ui.sh
```

## Koneksi ke ComfyUI

Video AI Creator tidak menjalankan atau menghentikan instance Vast.ai. ComfyUI harus sudah dijalankan terlebih dahulu, kemudian alamatnya dimasukkan melalui tombol **Konfigurasi Umum**.

Pada dialog tersebut:

1. isi `URL ComfyUI`;
2. tekan `Simpan & Periksa`;
3. baca hasil pemeriksaan di `Log Proses`;
4. unduh kelompok model yang dibutuhkan melalui `Download Model`;
5. gunakan `Download LoRA` jika membutuhkan LoRA tambahan.

Alamat dapat berupa `host:port` atau URL lengkap `http://` / `https://`.

### A. ComfyUI lokal

1. Pasang ComfyUI mengikuti panduan resmi di [repository ComfyUI](https://github.com/comfyanonymous/ComfyUI).
2. Jalankan ComfyUI pada komputer yang sama dengan Video AI Creator.
3. Pastikan halaman ComfyUI dapat dibuka di browser, biasanya melalui:

   ```text
   http://127.0.0.1:8188
   ```

4. Masukkan alamat berikut pada `Konfigurasi Umum`:

   ```text
   127.0.0.1:8188
   ```

Jika ComfyUI berjalan pada komputer lain di jaringan lokal, gunakan alamat IP komputer tersebut, misalnya `192.168.1.20:8188`. ComfyUI harus mengizinkan koneksi dari komputer Video AI Creator.

Setelah koneksi berhasil, aplikasi akan memeriksa ComfyUI-Model-Manager, model, dan daftar LoRA. Jika model belum lengkap, pilih kelompok model yang diperlukan dari dialog yang sama.

### B. ComfyUI di Vast.ai

1. Buat atau jalankan instance ComfyUI melalui console Vast.ai.
2. Tunggu sampai ComfyUI benar-benar selesai dijalankan.
3. Buka bagian **Advanced Connection Options** pada instance.
4. Salin URL koneksi ComfyUI dari tombol **Copy URL**. Pilih URL yang membuka tampilan ComfyUI, bukan URL Jupyter Terminal atau dokumentasi API wrapper.
5. Jika URL memiliki token, salin URL lengkap beserta bagian `?token=...`.
6. Tempel URL lengkap tersebut pada `URL ComfyUI` di **Konfigurasi Umum**.
7. Tekan `Simpan & Periksa` dan baca hasilnya pada `Log Proses`.

Contoh bentuk URL tunnel:

```text
https://contoh-subdomain.trycloudflare.com/?token=TOKEN_DARI_VAST
```

Jangan menghapus token dari URL. Login pada browser Vast.ai tidak otomatis memberikan akses API kepada aplikasi desktop, sehingga aplikasi harus memakai URL koneksi yang sudah membawa token atau autentikasi yang disediakan oleh instance.

Jika Vast.ai memberikan alamat IP dan port publik, alamat tersebut juga dapat digunakan, misalnya:

```text
http://ALAMAT_IP:PORT_PUBLIK
```

Pastikan port tersebut memang diarahkan ke port ComfyUI dan dapat dibuka dari komputer pengguna. URL Jupyter Terminal, URL `/docs` milik API wrapper, dan port yang tidak diarahkan ke ComfyUI tidak dapat digunakan sebagai URL ComfyUI.

Pengguna tetap mengatur siklus hidup instance melalui console Vast.ai. Setelah koneksi berhasil, model dan LoRA dapat dikelola dari **Konfigurasi Umum** tanpa SSH. ComfyUI-Model-Manager akan diperiksa dan dipasang bila diperlukan oleh aplikasi.

## Alur penggunaan pertama

1. Jalankan ComfyUI lokal atau Vast.ai.
2. Jalankan Video AI Creator.
3. Buka **Konfigurasi Umum** dan masukkan URL ComfyUI.
4. Unduh model yang diperlukan.
5. Buat project baru.
6. Buat atau pilih adegan.
7. Tambahkan gambar, audio, atau video referensi bila diperlukan.
8. Tulis prompt pada editor interaktif. Tombol `Buat Prompt` tersedia sebagai bantuan Gemini.
9. Simpan adegan, lalu tekan `Jalankan Adegan` atau `Jalankan Beberapa Adegan`.
10. Pantau kegiatan ComfyUI melalui `Log ComfyUI` dan kegiatan aplikasi melalui `Log Proses`.

## Bantuan dan masalah umum

- Jika aplikasi tidak dapat terhubung, buka **Konfigurasi Umum** dan periksa kembali URL ComfyUI.
- Jika ComfyUI belum berjalan, jalankan ComfyUI terlebih dahulu lalu simpan ulang konfigurasi.
- Jika model belum tersedia, gunakan `Download Model` dan tunggu sampai proses selesai.
- Jika LoRA belum muncul, pastikan pengunduhan selesai lalu perbarui pemeriksaan pada **Konfigurasi Umum**.
- Jika fitur Gemini gagal, periksa isi `keys.cfg` dan pastikan API key masih aktif.
- Jika pembuatan video gagal, buka `Log ComfyUI` untuk pesan dari ComfyUI dan `Log Proses` untuk langkah aplikasi.

Panduan penggunaan setiap tampilan tersedia melalui tombol **Bantuan** pada menu aplikasi.
