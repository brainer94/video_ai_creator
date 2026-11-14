## Overview

Proyek ini menjalankan pipeline pembuatan konten video per scene berbasis project dari folder `api_production/<project_name>/scene_*`.

## Virtual Environment

Virtual environment proyek memakai `.venv` di root repo.

Membuat dan install dependency:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Aktivasi:
```powershell
.\.venv\Scripts\Activate.ps1
```

```cmd
.\.venv\Scripts\activate.bat
```

```bash
source ./.venv/bin/activate
```

## Scene Structure

Folder scene berada di `api_production/<project_name>/scene_<n>/`.

File utama:
- `project_settings.json`
- `scene_meta.json`
- `z_image_prompt.json`
- `z_image_extra_prompts.json`
- `qwen_image_edit_prompt.json` (untuk tab `Image Edit`)
- `minimax_h3_t2v_prompt.json` (untuk scene `minimax-h3_t2v`)
- `minimax_h3_i2v_prompt.json` (untuk scene `minimax-h3_i2v`)
- `minimax_h3_i2v_panjang_prompt.json` (untuk scene `minimax-h3_i2v-panjang`)
- `minimax_h3_r2v_prompt.json` (untuk scene `minimax-h3_r2v`)
- `minimax_h3_r2v_panjang_prompt.json` (untuk scene `minimax-h3_r2v-panjang`)
- `minimax_h3_s2v_prompt.json` (untuk scene `minimax-h3_s2v`)
- `image_pan_prompt.json` (untuk `image_pan`)
- `image_zoom_prompt.json` (untuk `image_zoom`)

Catatan pembuatan file scene:
- saat membuat scene baru, baik dari UI maupun CLI, file JSON prompt yang relevan dengan pipeline aktif dibuat otomatis

Catatan format prompt:

- semua slot prompt menyimpan nilai langsung berbahasa Inggris; tidak ada wrapper bahasa pada JSON;
- prompt terstruktur MiniMax T2V, I2V, dan R2V memakai `shots[]` dengan bentuk item yang sama;
- R2V menyimpan `style_opening` dan `shots[]`; aplikasi mengompilasinya menjadi `detailed_description` saat runtime;
- R2V-Panjang menyimpan empat prompt pada `prompts[]`; maksimal empat gambar global dikirim lebih dulu, lalu frame awal Proses 1 (opsional) atau frame terakhir proses sebelumnya ditambahkan sebagai image terakhir;
- editor prompt interaktif MiniMax berada langsung di dalam tab scene dan tidak menampilkan JSON mentah;
- tombol `Buat Prompt` memakai Gemini untuk menghasilkan prompt Inggris; runtime hanya memvalidasi dan menserialisasi, tanpa translasi;
- model Gemini untuk `Buat Prompt` disimpan pada `project_settings.json.prompt_generation.model`;
- tombol `Buat Prompt` tidak melakukan `Save Scene` terlebih dahulu; input dan konteks diambil dari nilai yang sedang tampil di UI;
- `lora_trigger_words` disimpan sebagai text biasa dan hanya disisipkan ke awal prompt positif saat runtime, bukan ditulis permanen ke field prompt.

### Image Edit

Tab `Image Edit` muncul pada scene yang menyediakan fitur edit gambar. UI tab tetap satu, tetapi field `Model` memilih `Minimax H3 Image` atau `Qwen 2.1 Image`. Semua pengaturan Image Edit disimpan per scene sehingga setiap scene dapat memiliki gambar referensi, engine, ukuran, seed, dan prompt yang berbeda. Scene lama tanpa field `engine` memakai `qwen_2_1`.

#### Edit Gambar

Image Edit menggunakan satu panel `Edit Gambar`. Untuk `Qwen 2.1 Image`, panel ini menyediakan:

- pilihan ukuran `368x640`, `480x848`, `720x1280`, `640x368`, `848x480`, dan `1280x720`
- `Random Seed` untuk menghasilkan variasi setiap kali proses dijalankan
- seed tetap untuk mengulang proses dengan pengaturan acuan yang sama
- sepuluh pilihan gambar referensi yang ditata dalam tiga kolom agar mudah digunakan
- `Positive Prompt` untuk menjelaskan perubahan yang diinginkan
- `Negative Prompt` untuk menjelaskan hal-hal yang tidak diinginkan
- `Jumlah Edit` untuk menentukan jumlah gambar yang dibuat

Untuk `Minimax H3 Image`, panel yang sama menyembunyikan `Negative Prompt`, pilihan ukuran, `Random Seed`, dan seed statik. UI menampilkan penjelasan bahwa ukuran output mengikuti gambar pertama setelah gambar tersebut di-resize ke sekitar `4 MP` dan dimensinya disesuaikan ke multiple `32`.

Sepuluh gambar referensi dapat diisi secara bebas dan tidak harus lengkap. Pilihan `(Tanpa gambar)` dapat digunakan pada slot yang tidak diperlukan. Contohnya, pengguna dapat mengisi hanya `Image 1` dan `Image 3` tanpa harus mengisi slot lainnya.

Gambar yang dipilih akan dikirim sesuai urutan slot yang terisi. Jika hanya `Image 1` dan `Image 3` yang dipilih, keduanya menjadi referensi pertama dan kedua pada workflow; slot kosong tidak dikirim sebagai gambar palsu.

Pada engine `Minimax H3 Image`, gambar pertama dikirim melalui alur `LoadImage → ResizeImageMaskNode scale total pixels=4 → ResizeImageMaskNode scale to multiple=32 → MiniMaxH3ImageConditioning.images.image_1`. Gambar tambahan 2–10 dibuat sebagai node `LoadImage` terpisah dan langsung dihubungkan ke `images.image_2` sampai `images.image_10` pada node conditioning. Gambar pertama menentukan width/height output; referensi tambahan tidak menentukan ukuran output.

`Jumlah Edit` bernilai `1` secara default dan harus lebih besar dari `0`. Jika diatur ke angka yang lebih besar, aplikasi mengirim workflow baru untuk setiap edit dan mengunduh hasil sebanyak angka tersebut. Pada `Qwen 2.1 Image`, `Random Seed` dapat memakai seed acak atau seed statik; pada `Minimax H3 Image`, seed dibuat internal oleh runtime.

#### Buat Prompt

Bagian `Buat Prompt` memiliki sepuluh pilihan gambar tambahan dan satu kolom instruksi. Bagian ini adalah pipeline terpisah dari `Edit Gambar`: gambar yang dipilih untuk menyusun prompt tidak otomatis menjadi gambar referensi workflow edit.

Gambar untuk `Buat Prompt` merupakan pilihan yang terpisah dari gambar untuk `Edit Gambar`. Gambar yang dikirim ke model bahasa tidak harus dipilih kembali sebagai gambar workflow. Dengan demikian, pengguna dapat memakai satu set gambar sebagai bahan analisis prompt, lalu memakai set gambar lain untuk proses edit akhir.

Model memberi urutan pada gambar berdasarkan urutan gambar yang dipilih. Untuk `Qwen 2.1 Image`, misalnya slot 1 dan slot 3 menjadi `<image1>` dan `<image2>`; untuk `Minimax H3 Image`, token yang sama menjadi `<Picture 1>` dan `<Picture 2>`. Urutan ini membantu pengguna memberi instruksi seperti memindahkan subjek dari satu gambar ke gambar lain atau mempertahankan bagian tertentu dari referensi tertentu.

Instruksi `Buat Prompt` dapat menjelaskan:

- objek atau orang yang ingin diubah
- gambar mana yang menjadi sumber subjek atau bahan referensi
- bagian yang harus dipertahankan
- perubahan pose, pakaian, warna, latar, komposisi, atau gaya
- hubungan antara beberapa gambar referensi

`Buat Prompt` menggunakan input gambar multimodal melalui Gemini. Pada engine `Qwen 2.1 Image`, model menerima instruksi Qwen Image Edit 2.1. Pada engine `Minimax H3 Image`, Gemini menerima `system_prompt` dan `task_prompt` dari blok bertanda di `minimax_h3_image_edit/edit-en.txt`; workflow JSON hanya dipakai untuk eksekusi ComfyUI dan bukan sumber payload prompt Gemini.

Untuk `Qwen 2.1 Image`, LLM mengembalikan JSON dengan key `prompt`. Untuk `Minimax H3 Image`, LLM mengembalikan `expanded_caption` dan `target_aspect_ratio`; `expanded_caption` disimpan ke `positive_prompt`, sedangkan rasio disimpan sebagai metadata. `negative_prompt` tidak diubah oleh tombol `Buat Prompt`. Prompt MiniMax memakai token referensi `<Picture 1>`, `<Picture 2>`, dan seterusnya sesuai urutan gambar yang dikirim ke payload Gemini.

Aturan khusus MiniMax H3 untuk tombol `Buat Prompt`:

- LLM menghasilkan object prompt langsung sesuai mode aktif;
- field angka, array timeline, identifier, dan token reference dipertahankan oleh validator;
- schema respons tidak menyertakan field non-prompt seperti `lora_name`, `width`, dan `height`;
- I2VA wajib memiliki anchor `Picture 1`, sedangkan T2VA tidak boleh memiliki alignment image;
- R2V memakai `style_opening` dan `shots[]` dengan item shot yang sama seperti T2VA/I2VA;
- hasil valid langsung dimuat ke editor dan disimpan pada slot prompt.

Schema prompt MiniMax H3 T2VA/I2VA:

- `positive_prompt` adalah object JSON langsung dengan `mode`, `shots`, `overall_soundscape`, dan `non_diegetic_music`;
- setiap item `shots` wajib memiliki `shot_id`, `start`, `end`, `visual`, `action`, `camera`, `dialogue`, dan `diegetic_sound`;
- `shot_id` berbentuk string seperti `Shot 1`; `start` dan `end` berbentuk angka;
- I2VA juga wajib memiliki alignment `Picture 1` pada awal prompt; T2VA tidak boleh memiliki alignment image;
- `remove_sound` adalah boolean teknis di level root prompt dan tidak dikirim ke ComfyUI.

Schema prompt MiniMax H3 R2V:

- `positive_prompt` adalah object JSON langsung dengan section Ref2VA, `style_opening`, dan `shots[]`;
- setiap item R2V `shots[]` memakai struktur yang sama seperti T2VA/I2VA;
- runtime mengompilasi `style_opening + shots[]` menjadi section `detailed_description`;
- semua section Ref2VA memakai teks Inggris dan token reference aktif yang sama.

Field utama:
- `scene_meta.json`
  - `scene_title`
  - `scene_description` (opsional)
  - `scene_type`
  - `duration_seconds`
  - `voice_text`
  - `gemini_tts_model`
  - `gemini_tts_voice_id` (dipakai oleh model Gemini 3.8)
  - `gemini_tts_voice_label` (label lokal suara Gemini 3.8)
  - `voice_character`
- `project_settings.json`
  - `project_description`
  - `video_size.width`
  - `video_size.height`
  - `prompt_generation.model`
  - `voice.voice_provider` (fixed `gemini`)
  - `caption.generate_caption`
  - `cover` (struktur sama seperti `z_image_prompt.json`)
- `z_image_prompt.json`
  - `image_model`
  - `gemini_model_id` (khusus saat `image_model=gemini`)
  - `lora_trigger_words`
  - `positive_prompt`
  - `negative_prompt`
  - `width`
  - `height`
  - `use_random_seed`
  - `seed`
  - `lora_name`
  - `strength_model`

Nilai `image_model` yang didukung:
- `z-image turbo`
- `flux.2`
- `gemini`
- `image_pan_prompt.json`
  - `width` (portrait only)
  - `height` (portrait only)
  - `direction` (`from_right` / `from_left`)
- `image_zoom_prompt.json`
  - `width`
  - `height`
  - `zoom_direction` (`in` / `out`)
  - `focal_point` (`center`, `top_left`, `top_center`, `top_right`, `center_left`, `center_right`, `bottom_left`, `bottom_center`, `bottom_right`)
  - `zoom_strength` (`1.0` sampai `1.5`)
Kebutuhan prompt per `scene_type`:
- `minimax-h3_t2v`
  - membutuhkan `scene_meta.json` dan `minimax_h3_t2v_prompt.json`
  - durasi scene berupa angka desimal `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame
  - seluruh durasi dijalankan oleh satu workflow MiniMax H3 T2V
  - FPS MiniMax H3 ditetapkan `24`
- `minimax-h3_i2v`
  - membutuhkan `scene_meta.json`, `z_image_prompt.json`, `minimax_h3_i2v_prompt.json`, dan minimal satu gambar di root folder scene
  - durasi scene berupa angka desimal `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame
  - memakai gambar terbaru dari root folder scene sebagai `Picture 1` untuk workflow MiniMax H3 I2VA
  - FPS MiniMax H3 ditetapkan `24`
- `minimax-h3_i2v-panjang`
  - membutuhkan `scene_meta.json`, `z_image_prompt.json`, `minimax_h3_i2v_panjang_prompt.json`, dan minimal satu gambar di root folder scene
  - durasi scene berupa angka desimal `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame per stage
  - memakai alur MiniMax H3 I2VA berantai; `continuations` bernilai integer `0` sampai `3`
  - `continuations=0` menjalankan satu stage; nilai `1`, `2`, dan `3` menjalankan masing-masing 2, 3, dan 4 stage
  - setiap stage aktif wajib memilih image referensi awal dan image referensi akhir; tidak ada opsi untuk meniadakan last frame
  - frame terakhir setiap stage dipakai sebagai `Picture 1` untuk stage berikutnya
  - setiap stage memakai prompt berbeda dari array `prompts` yang berisi tepat 4 prompt
  - prompt stage aktif berupa object I2VA langsung dalam bahasa Inggris
  - hasil semua stage digabung, lalu color match diterapkan pada video gabungan
  - FPS MiniMax H3 ditetapkan `24`
- `minimax-h3_r2v`
  - membutuhkan `scene_meta.json`, `minimax_h3_r2v_prompt.json`, dan minimal satu reference image, video, atau audio sesuai manifest prompt
  - durasi scene berupa angka desimal `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame
  - FPS MiniMax H3 ditetapkan `24`
  - setelah video selesai dibuat, frame pertama dan terakhir disimpan di folder scene dengan pola `<nama_file_video>_first_frame.png` dan `<nama_file_video>_last_frame.png`
- `minimax-h3_r2v-panjang`
  - membutuhkan `scene_meta.json` dan `minimax_h3_r2v_panjang_prompt.json`
  - durasi scene berupa angka desimal `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame per proses
  - memakai empat proses R2V berantai; `continuations` bernilai integer `0` sampai `3`
  - reference image, audio, dan video dipilih sekali secara global untuk semua proses; maksimal empat gambar global dipakai agar satu slot Picture tersedia untuk image awal/carry
  - Proses 1 dapat memilih satu `initial_image` opsional; image ini ditambahkan setelah seluruh Picture global sebagai frame pertama
  - proses 2–4 otomatis menambahkan frame terakhir proses sebelumnya setelah seluruh Picture global; frame ini tidak dipilih manual dan tidak ditulis ke `references.images`
  - setiap proses memakai prompt Ref2VA berbeda dari array `prompts` yang berisi tepat 4 prompt
  - `run_start_stage` dapat menjalankan ulang dari proses tertentu jika segment dan frame proses sebelumnya sudah tersedia
  - hasil semua proses digabung, lalu color match diterapkan pada video gabungan
  - FPS MiniMax H3 ditetapkan `24`
- `minimax-h3_s2v`
  - membutuhkan `scene_meta.json`, `z_image_prompt.json`, `minimax_h3_s2v_prompt.json`, minimal satu gambar di root folder scene, dan minimal satu file audio speech berawalan `speech_`
  - durasi voice dikirim sebagai float ke workflow; output video dipertahankan utuh setelah diunduh
  - durasi audio speech tidak boleh lebih dari 15 detik; jika melebihi batas, scene diblokir
  - FPS MiniMax H3 ditetapkan `24`
  - workflow memakai `minimax_h3_r2v_api.json` secara in-memory dan menghapus referensi Picture 2, Picture 3, Video 1, Audio 2, dan Audio 3
  - jika `fast_mode=true`, workflow S2V memakai template FastH3 R2V dengan konfigurasi model omnireference FastH3
  - Picture 1 berasal dari gambar root terbaru dan Audio 1 berasal dari audio speech root terbaru

Mode MiniMax H3:
- `Mode Cepat` tersedia pada tab T2V, I2V, R2V, S2V, I2V-Panjang, dan R2V-Panjang. Pada scene panjang, pilihan ini berlaku untuk seluruh proses yang dijalankan.
- `Mode Cepat` memakai workflow Fast MiniMax H3 dan selalu memakai 8 step; pengaturan jumlah step normal tidak digunakan pada mode ini.
- FastH3 R2V/S2V memakai `api_template/minimax_fasth3_r2v_api.json`, UNet `MINIMAX-H3/fasth3_omniref_8step_pruned_int8_convrot.safetensors`, Sigma Shift video `12`, Sigma Shift audio `3`, dan Model Sparse Attention dengan `start_percent=0.00`.
- Jika `Mode Cepat` tidak dipilih, scene memakai workflow MiniMax H3 normal dan pengaturan jumlah step yang tersedia pada tab tersebut tetap digunakan.

- semua `scene_type`
  - `scene_title` wajib diisi; `scene_description` bersifat opsional
- `i2v`
  - membutuhkan `scene_meta.json`, `z_image_prompt.json` (untuk ukuran target video), dan minimal satu gambar di root folder scene
- `image_pan`
  - membutuhkan `scene_meta.json`, `z_image_prompt.json`, dan minimal satu gambar di root folder scene
  - `width`/`height` pada `image_pan_prompt.json` wajib portrait (tinggi > lebar)
  - durasi diambil dari `scene_meta.duration_seconds`
  - `direction` wajib `from_right` atau `from_left`
- `image_zoom`
  - membutuhkan `scene_meta.json`, `image_zoom_prompt.json`, dan minimal satu gambar di root folder scene
  - `width`/`height` pada `image_zoom_prompt.json` bebas mengikuti rasio target video
  - durasi diambil dari `scene_meta.duration_seconds`
  - `zoom_direction` wajib `in` atau `out`
  - `focal_point` wajib salah satu nilai yang didukung di `image_zoom_prompt.json`
  - `zoom_strength` wajib di antara `1.0` sampai `1.5`

Catatan sumber image:
- `minimax-h3_i2v`
  - memakai satu gambar terbaru dari root folder scene sebagai input first frame
  - durasi workflow MiniMax H3 I2VA mengikuti durasi scene desimal (`0.0` sampai `15.0`); durasi `0.0` menghasilkan output minimum 5 frame
  - FPS workflow MiniMax H3 ditetapkan `24`
- `i2v`
  - memakai semua gambar dari root folder scene
- `image_pan`
  - membuat video dari satu gambar awal dengan pan horizontal sesuai arah (`from_right` / `from_left`)
  - pan selalu menempuh penuh dari sisi ke sisi dalam durasi scene
  - frame selalu mengikuti tinggi penuh gambar sumber (full height), lalu bergerak ke samping
  - mode default `stable_pan` direkomendasikan untuk gerakan yang lebih halus
  - fps mengikuti scene type `i2v` (`16`)
- `image_zoom`
  - membuat video dari satu gambar awal dengan zoom in atau zoom out sesuai `zoom_direction`
  - titik fokus zoom mengikuti `focal_point` agar anchor zoom tetap konsisten
  - `zoom_strength` mengatur seberapa jauh zoom bergerak dalam rentang `1.0` sampai `1.5`
  - mode default `stable_pan` direkomendasikan untuk hasil yang lebih stabil
  - fps mengikuti scene type `i2v` (`16`)

Catatan voice dan caption:
- `voice_text`
  - dipakai sebagai sumber TTS
  - dipakai juga sebagai sumber caption
- `voice_character`
  - dipilih per scene dari karakter suara:
    - `lily`, `lily_ngaji`, `lily_arab`
- `gemini_tts_model`
  - default dan kompatibilitas scene lama: `gemini-3.1-flash-tts-preview`
  - pilihan tambahan: `gemini-3.8-flash-tts`
- `gemini_tts_voice_id` dan `gemini_tts_voice_label`
  - hanya digunakan ketika model adalah `gemini-3.8-flash-tts`
  - UI menampilkan nama voice dari Gemini, misalnya `Bodi` atau `Koda`
  - `gemini_tts_voice_id` menyimpan ID canonical untuk request API; label UI tidak dikirim sebagai nama voice
- prompt lain seperti `positive_prompt`, `negative_prompt`, dan prompt grup edit/image disimpan sebagai nilai langsung berbahasa Inggris
- konfigurasi provider voice bersifat global per project di `project_settings.json.voice`:
  - `voice_provider=gemini` tetap menjadi provider runtime
  - model TTS dipilih per scene melalui `scene_meta.json` (language `id-ID`)
- konfigurasi caption bersifat global per project di `project_settings.json.caption`:
  - `generate_caption`
  - boolean
  - default `true`
  - jika aktif, caption dibakar saat final compose ke `combined/combined_all.mp4`, setelah penggabungan audio dan optional upscale selesai
  - caption tidak membuat file `__captioned` tambahan pada alur otomatis; video final ditimpa dengan versi yang sudah bercaption

Catatan trimming video:
- seluruh output scene MiniMax (`minimax-h3_t2v`, `minimax-h3_i2v`, `minimax-h3_s2v`, dan `minimax-h3_r2v`) dipertahankan utuh setelah download; frame alignment `17n+5` adalah bagian dari hasil generasi, bukan padding pascaproses yang dibuang
- khusus `minimax-h3_s2v` dengan provider Gemini, setelah WAV TTS dibuat:
  - sample rate harus `24 kHz`; jika bukan, proses menampilkan warning dan padding tidak diterapkan
  - durasi WAV dikonversi ke frame video dengan `round(sample_count * 24 / 24000)`
  - target alignment MiniMax mengikuti `frame_count % 17 == 5` pada 24 FPS
  - jika target alignment berikutnya masih berada di bawah atau sama dengan batas `15 detik`, silence ditambahkan di bagian akhir WAV
  - jika penambahan silence akan melewati `15 detik`, WAV dipotong ke target alignment-safe sebelumnya
  - target alignment-safe terbesar yang tidak melewati `15 detik` adalah `345 frame = 14.375 detik`; `360 frame = 15 detik` bukan alignment-safe
  - WAV yang sudah alignment-safe tidak diubah lagi pada pemrosesan berikutnya (operasi bersifat idempoten)
- dengan audio yang sudah alignment-safe, durasi audio mengikuti frame alignment output S2V dan video tidak perlu dipotong setelah download
- scene type lain tidak dipotong otomatis mengikuti speech

## Audio Scene dan Final Compose

Scene berikut menghasilkan video scene yang sudah memiliki audio setelah eksekusi scene selesai:

- `minimax-h3_i2v`
- `minimax-h3_t2v`

Mix audio scene mengikuti pola berikut:

```text
video ComfyUI
+ voice scene
= video scene ber-audio
```

Untuk `minimax-h3_i2v` dan `minimax-h3_t2v`:

- `remove_sound=true`: audio bawaan ComfyUI dihapus terlebih dahulu, kemudian voice di-mix
- `remove_sound=false`: audio bawaan ComfyUI dipertahankan dan di-mix bersama voice

Setelah mix berhasil, `scene_meta.json` diberi marker `audio_composed=true`. Saat `generate_compose.py` membuat final compose, video bertanda tersebut hanya diekspor dengan audio yang sudah ada; voice tidak ditambahkan lagi. Hal ini mencegah double mix.

Untuk `minimax-h3_s2v` dan `minimax-h3_r2v`, final compose hanya memilih satu video terbaru di root scene. Video lama yang masih berada di root tidak ikut digabung.

## Server Config

Konfigurasi default/global ComfyUI disimpan di `server_config.json`:

```json
{
  "comfyui": {
    "url": "",
    "host": "nextgenserver",
    "port": 8188
  }
}
```

Alamat ComfyUI hanya dikonfigurasi secara global melalui tombol `Konfigurasi Umum`. Field `url` dapat berisi `host:port` atau URL `http(s)` lengkap. URL tunnel Vast.ai dapat menyertakan query token dari tombol `Copy URL`. Jika `url` kosong, aplikasi memakai kombinasi `host` dan `port`.

Contoh:
```json
{
  "comfyui": {
    "url": "https://comfyui.example.trycloudflare.com/?token=TOKEN_SEMENTARA",
    "host": "nextgenserver",
    "port": 8188
  }
}
```

Pemakaian:
- alamat global dipakai oleh `main.py`, script generate image, `scripts/generate_cover_image.py`, dan `scene_manager_ui.py`
- URL tunnel bertoken dibuka sekali oleh client ComfyUI untuk membuat session cookie, lalu session tersebut dipakai untuk workflow, upload, history, output, log, dan ComfyUI-Manager
- token tidak ditulis ke log request; nilai token tetap berada pada konfigurasi global yang diberikan pengguna
- model `prompt_generation` bersifat per-project dan dibaca dari `project_settings.json`
- default model Gemini untuk `prompt_generation` adalah `gemini-3.1-flash-lite`
- konfigurasi model diubah lewat dialog `Konfigurasi Project`

### Konfigurasi Umum ComfyUI

Tombol paling kiri `Konfigurasi Umum` memakai ikon komputer/pengaturan dan selalu aktif, walaupun belum ada project yang dibuka. Dialog ini berisi URL ComfyUI global di bagian atas dan kelompok model di bawahnya:

- `MiniMax H3`
- `MiniMax H3 Mode Cepat`
- `MiniMax H3 Image`
- `Flux 2`
- `Z Image Turbo`
- `Qwen Image Edit`

Beberapa kelompok MiniMax berbagi text encoder dan VAE. Project menghapus duplikasi sebelum membuat task download. Saat dialog dibuka, project memeriksa kelengkapan kelompok yang tersedia. Kelompok yang seluruh filenya sudah ada akan otomatis tercentang dan dikunci; kelompok yang hanya sebagian tersedia tetap dianggap belum lengkap dan dapat dipilih untuk melanjutkan.

Saat aplikasi dijalankan, dan setiap kali URL global diganti, dialog `Log Proses` dibuka dan menampilkan pemeriksaan secara bertahap: koneksi ComfyUI, pemasangan `ComfyUI-Model-Manager`, restart dan kesiapan server, kelengkapan model, serta daftar LoRA. Jika ada masalah, detailnya ditulis di log proses; project tidak memakai popup warning untuk audit ini.

Pemeriksaan startup juga memeriksa kelompok model yang tersedia dan daftar LoRA melalui `object_info`. Jika ada kelompok model yang belum lengkap, status tersebut ditulis ke `Log Proses`; daftar LoRA kemudian di-refresh untuk seluruh scene yang aktif.

Download model kemudian dijalankan melalui endpoint `ComfyUI-Model-Manager` (`POST /model-manager/model`) dan dipantau melalui `GET /model-manager/download/task`. Custom node memulai task segera, menyimpan task yang belum selesai, dan mendukung resume untuk file parsial. Setelah task selesai, project memeriksa ulang inventory model melalui endpoint custom node. Project tidak memerlukan SSH dan tidak bergantung pada model whitelist Manager untuk URL model yang dikelola katalog project.

Model disimpan pada subfolder prefix yang dipakai workflow, misalnya `models/diffusion_models/MINIMAX-H3/`, `models/text_encoders/FLUX2/`, atau `models/vae/QWEN/`.

Tombol `Download LoRA` tersedia di dialog `Konfigurasi Umum`. Pengguna memasukkan URL Hugging Face atau Civitai, memilih kategori `MiniMax H3`, `Flux 2`, atau `Z Image`, lalu menentukan nama file target. File disimpan ke `models/loras/MINIMAX-H3/`, `models/loras/FLUX.2/`, atau `models/loras/Z-IMAGE/`. Project memeriksa inventory dan task aktif sebelum membuat download agar file atau task yang sama tidak diduplikasi. Setelah selesai, inventory diverifikasi dan daftar LoRA di-refresh melalui `object_info`.

## Project CLI

Script: `scripts/project_cli.py`

Fungsi:
- membuat project baru dari CLI dengan struktur dan format file yang sama seperti UI
- menambah scene baru ke project yang sudah ada dengan pilihan `scene_type` yang sama seperti UI
- backend pembuatan project dan scene dipakai bersama oleh UI dan CLI agar format JSON tetap konsisten
- tersedia launcher tipis di folder `api_production`:
  - `api_production/project_cli.py`
  - `api_production/project_cli.bat`
  - launcher ini mengasumsikan source code ada di parent directory dari `api_production`
  - launcher harus dijalankan dari dalam folder `api_production`

Subcommand:
- `create-project`
  - default membuat project kosong, hanya `project_settings.json`
  - bisa memakai `--with-default-scene` untuk mengikuti perilaku tombol `Project Baru` di UI dan otomatis membuat `scene_1`
  - bisa mengisi:
    - `project_description`
    - `video_size.width`
    - `video_size.height`
    - `prompt_generation.model`
    - `voice.voice_provider` (fixed `gemini`)
    - `caption.generate_caption`
- `create-scene`
  - menambah scene baru berurutan (`scene_1`, `scene_2`, dst)
  - bisa mengisi:
    - `scene_title`
    - `scene_description`
    - `voice_text`
    - `scene_type`
    - `duration_seconds`
  - setelah scene dibuat, ukuran project otomatis disinkronkan ke file prompt scene yang relevan

Pilihan `scene_type`:
- `minimax-h3_t2v`
- `minimax-h3_i2v`
- `minimax-h3_i2v-panjang`
- `minimax-h3_s2v`
- `minimax-h3_r2v`
- `minimax-h3_r2v-panjang`
- `i2v`
- `image_pan`
- `image_zoom`

Contoh:
```powershell
.\.venv\Scripts\python.exe scripts\project_cli.py create-project --project demo_project
.\.venv\Scripts\python.exe scripts\project_cli.py create-project --project demo_project --description "Video edukasi anak" --width 360 --height 640 --prompt-generation-model gemini-3.1-flash-lite --voice-provider gemini --generate-caption true
.\.venv\Scripts\python.exe scripts\project_cli.py create-project --project demo_project --with-default-scene
.\.venv\Scripts\python.exe scripts\project_cli.py create-scene --project demo_project --scene-type i2v --title "Intro Gambar" --scene-description "Pembuka video dari gambar." --voice-text "Halo teman-teman! Hari ini kita mulai." --duration 10
```

Contoh dari folder `api_production`:
```powershell
.\project_cli.bat create-project --project demo_project
.\project_cli.bat create-scene --project demo_project --scene-type image_zoom --title "Zoom Intro" --scene-description "Close-up magnet merah biru." --voice-text "Halo teman-teman! Hari ini kita belajar magnet, benda seru yang bisa menarik klip kertas dan benda logam kecil di sekitar kita!" --duration 10
.\project_cli.bat create-scene --project demo_project --scene-type i2v --title "Intro Gambar" --scene-description "Pembuka video dari gambar." --voice-text "Halo teman-teman! Hari ini kita mulai." --duration 10
.\project_cli.bat create-scene --project demo_project --scene-type minimax-h3_r2v-panjang --title "R2V Panjang" --duration 10.5
```

Untuk scene MiniMax, `--duration` dapat berupa angka desimal hingga empat angka di belakang koma sesuai validasi scene.

## Main Runner

Script utama: `main.py`

Fungsi:
- `scene_type=minimax-h3_t2v`
  - satu workflow MiniMax H3 T2V dijalankan untuk seluruh durasi scene
  - tidak ada upload frame terakhir atau stage I2V lanjutan
- `scene_type=minimax-h3_i2v`
  - ambil satu gambar terbaru dari root folder scene
  - upload image ke ComfyUI
  - generate video dari `minimax_h3_i2v_prompt.json` menggunakan workflow MiniMax H3 I2V
- `scene_type=i2v`
  - ambil semua gambar dari root folder scene
  - compose gambar menjadi video sederhana
  - jika `project_settings.caption.generate_caption=true`, caption dibakar saat final compose
- `scene_type=image_pan`
  - membaca `image_pan_prompt.json`
  - mengambil satu gambar terbaru dari root folder scene sebagai sumber pan horizontal
  - arah pan ditentukan oleh `direction` (`from_right` atau `from_left`)
  - mode capture:
    - `stable_pan` (default): pan gambar dengan hasil gerak lebih halus
  - jika `project_settings.caption.generate_caption=true`, caption dibakar saat final compose
- `scene_type=image_zoom`
  - membaca `image_zoom_prompt.json`
  - mengambil satu gambar terbaru dari root folder scene sebagai sumber zoom
  - zoom ditentukan oleh `zoom_direction` (`in` atau `out`)
  - titik fokus zoom ditentukan oleh `focal_point`
  - mode capture:
    - `stable_pan` (default): zoom gambar dengan hasil gerak lebih halus
  - jika `project_settings.caption.generate_caption=true`, caption dibakar saat final compose

Argumen:
- `--server`, `-s`
  - ComfyUI server `host:port`
- `--project`, `-p`
  - nama project di dalam `api_production`
- `--scene`, `-S`
  - nama scene, repeatable
- `--loop`, `-L`
  - jumlah loop, minimal `1`

Contoh:
```powershell
.\.venv\Scripts\python.exe main.py --server 127.0.0.1:8188 --project demo_project
.\.venv\Scripts\python.exe main.py --server 127.0.0.1:8188 --project demo_project --scene scene_1
.\.venv\Scripts\python.exe main.py --server 127.0.0.1:8188 --project demo_project --scene scene_1 --scene scene_2
```

## Scene Manager UI

Script: `scene_manager_ui.py`

Fungsi utama:
- project-based workspace:
  - `Project Baru` membuat folder project baru di `api_production/<project_name>`
  - project baru otomatis dibuat dengan `project_settings.json` dan `scene_1`
  - `Buka Project` memilih project yang sudah ada
  - `Tutup Project` menutup project aktif
  - nama project harus unik (tidak boleh duplikat)
- tombol `Konfigurasi Project` untuk mengatur:
  - `Deskripsi Project`
  - `Ukuran Video Project`
  - `Model Prompt Generation`
    - jalur prompt hanya menggunakan Gemini
    - model disimpan pada `project_settings.json.prompt_generation.model`
  - `Voice Project`
  - `Caption Project`
  - `Cover`
  - pada bagian `Cover`, ukuran cover otomatis mengikuti `Ukuran Video Project` dan dropdown ukuran cover dinonaktifkan
- tombol paling kiri `Konfigurasi Umum` selalu aktif untuk mengatur URL ComfyUI global, memeriksa koneksi, memasang ComfyUI-Model-Manager, melihat kelengkapan model, dan memperbarui daftar LoRA
- menampilkan daftar scene dari project aktif
- drag-and-drop untuk reorder scene
- tambah, sisipkan, dan hapus scene
- edit metadata scene
- edit prompt image
- tab `Prompt Tambahan` untuk 3 prompt image tambahan berbasis aturan `Gambar Awal`
- tab `Image Edit` untuk edit gambar berbasis referensi multimodal dengan pilihan engine `Minimax H3 Image` dan `Qwen 2.1 Image`
- untuk voice, tersedia field:
- `Pilihan Suara Scene` (per scene): 3 karakter suara
- group `Audio` berisi proses generate voice/sound untuk scene atau semua scene
- tombol `Upscale Video` di group `Scene` untuk upscale video terakhir pada root scene aktif
- edit ukuran image
- edit pengaturan seed image
- edit Lora image
- pilih model image:
  - `Z-Image Turbo`
  - `Flux.2`
  - `Gemini`
- menampilkan aset media per scene
- klik sekali pada aset membuka preview:
  - `Image` langsung tampil sebagai preview
  - `Video` tampil sebagai thumbnail preview dulu
  - `Suara` tampil sebagai ikon speaker
- klik ganda pada aset menjalankan media:
  - `Image` tetap hanya preview
  - `Video` langsung diputar
  - `Suara` langsung diputar
- klik pada preview membuka file dengan aplikasi default sistem operasi
- klik ganda pada preview memiliki perilaku yang sama
- hapus aset dari menu klik kanan
- jalankan proses image, scene, voice, sound, dan compose
- tombol `Save` untuk backup project aktif menjadi ZIP
- menampilkan log proses
- memakai backend pembuatan project/scene yang sama dengan `scripts/project_cli.py`, tetapi perilaku `Project Baru` di UI tetap otomatis membuat `scene_1`

Perilaku UI:
- operasi scene hanya aktif jika project sudah dibuka
- scene dengan tipe yang tidak didukung hanya menampilkan tab `Meta` dan `Aset`; Save, autosave, dan eksekusi diblok sampai pengguna memilih tipe yang didukung secara eksplisit
- panel `Tampilan` untuk preview gambar/video hanya muncul saat tab `Aset` aktif dan memakai sekitar setengah area editor; pada tab lain panel tersebut disembunyikan agar editor tengah melebar
- konfigurasi cover disimpan global per project di `project_settings.json.cover`
- hasil generate cover disimpan ke `api_production/<project_name>/cover/cover.png`
- scene yang belum memenuhi syarat dijalankan ditampilkan dengan nama berwarna merah di `Daftar Adegan`; tooltip nama scene berisi semua masalah dalam beberapa baris
- `Jalankan Adegan` hanya menjalankan scene aktif
- tombol batch sekarang bernama `Jalankan Beberapa Adegan`; tombol ini membuka daftar scene dengan checkbox sehingga pengguna dapat memilih scene yang ingin dijalankan
- scene terpilih dijalankan mengikuti urutan daftar scene; scene yang tidak dicentang tidak ikut diproses
- scene bermasalah ditandai merah dan tooltip-nya menampilkan alasan masalah; jika scene bermasalah tetap dipilih, proses batch diblok sampai masalah diperbaiki atau scene tersebut tidak dipilih
- daftar LoRa dimuat sekali saat UI dijalankan, lalu dipakai dari memory cache untuk semua dropdown LoRa
- saat startup UI atau URL ComfyUI diganti, `Log Proses` terbuka otomatis dan menampilkan langkah pemeriksaan serta detail error; daftar LoRa tidak dimuat jika koneksi gagal
- dukungan progres WebSocket ComfyUI dipisahkan ke `scripts/comfyui_ws.py` dan saat ini disabled; jalur aktif tidak mengimpor atau memulai listener WebSocket
- dependensi `websocket-client` tetap tercantum di `requirements.txt`, tetapi jalur WebSocket masih disabled dan tidak diimpor atau dijalankan oleh UI aktif
- callback pemuatan LoRa dan log diproses di thread UI; request jaringan berjalan di background
- daftar model Gemini untuk gambar scene dan cover memakai pilihan bawaan saat jendela dibuka, lalu diperbarui di background dan dibagikan melalui cache selama sesi UI; pilihan model yang sudah tersimpan tetap dipertahankan
- ketika UI ditutup, callback ke jendela dihentikan; request background yang sudah berjalan ditunggu hingga selesai atau timeout sebelum objek thread Qt dibersihkan
- grup toolbar menyediakan satu tombol `Log ComfyUI`
- dialog `Log ComfyUI` berukuran sekitar dua pertiga layar, berada di tengah, dan mengambil 200 baris log terakhir melalui API native ComfyUI; kode warna ANSI dibersihkan sebelum ditampilkan
- dialog log bersifat read-only dan melakukan refresh async setiap 5 detik; waktu refresh terakhir ditampilkan
- dialog `Log Proses` menampilkan operasi UI dan langkah audit koneksi, Model Manager, model, dan LoRA secara berurutan; progres inferensi ComfyUI ditampilkan di `Log ComfyUI`
- posisi scroll vertikal dan horizontal dipertahankan saat isi log diperbarui, tanpa memaksa scrollbar ke baris paling akhir
- endpoint log yang digunakan adalah `GET /internal/logs/raw` pada ComfyUI
- apabila API log native tidak tersedia, dialog menampilkan error dan tetap mencoba refresh setiap 5 detik
- `voice` dan `sound` bersifat opsional
- `voice` hanya wajib jika `voice_text` diisi
  - untuk model `gemini-3.1-flash-tts-preview`, pilihan suara tetap melalui `voice_character`, termasuk `lily_arab` (Lily - Arab)
  - untuk model `gemini-3.8-flash-tts`, pilihan suara diambil dari Gemini Voices API dan ditampilkan berdasarkan nama voice saja
- language TTS runtime dipaksa ke `id-ID`
- label input prompt di UI berbahasa Indonesia, sedangkan isi prompt yang disimpan berbahasa Inggris; editor MiniMax memakai form interaktif
- ukuran video project menjadi sumber ukuran untuk tab `Image Pan` dan `Image Zoom`
- dropdown ukuran pada tab `Image Pan` dan `Image Zoom` dikunci (disabled) dan hanya menampilkan ukuran project aktif
- ukuran pada tab `Gambar Awal` ditentukan secara scene-local melalui dropdown pada tab tersebut
- scene type `minimax-h3_i2v` menampilkan tab berurutan:
  - `Meta`
  - `Gambar Awal`
  - `Image Edit`
  - `MINIMAX-H3_I2V`
  - `Aset`
- scene type `minimax-h3_i2v-panjang` menampilkan tab berurutan:
  - `Meta`
  - `Gambar Awal`
  - `Image Edit`
  - `MINIMAX-H3_I2V-PANJANG`
  - `Aset`
- tab `MINIMAX-H3_I2V-PANJANG` menyediakan:
  - input `Lanjutan` integer `0` sampai `3`
  - empat editor prompt interaktif: `Prompt 1`, `Prompt 2`, `Prompt 3`, dan `Prompt 4`
  - prompt yang tidak termasuk jumlah lanjutan dibuat disabled di UI
  - urutan input: `Prompt 1`, `Lanjutan`, `Prompt 2`, `Prompt 3`, `Prompt 4`, kemudian `Jumlah Step`
  - `Buat Prompt` memakai LLM untuk menghasilkan object Inggris sesuai aturan JSON MiniMax H3 I2VA
- scene type `minimax-h3_r2v-panjang` menampilkan tab berurutan:
  - `Meta`
  - `Gambar Awal`
  - `Image Edit`
  - `MINIMAX-H3_R2V-PANJANG`
  - `Aset`
- tab `MINIMAX-H3_R2V-PANJANG` menyediakan empat tab proses dengan layout seperti I2V-Panjang. Reference global dan frame awal Proses 1 opsional dipilih pada Proses 1; proses berikutnya otomatis menampilkan frame carry sebagai Picture tambahan.
- scene type `minimax-h3_s2v` menampilkan tab berurutan:
  - `Meta`
  - `Gambar Awal`
  - `MINIMAX-H3_S2V`
  - `Aset`
- urutan tab selalu di-reset ke urutan canonical saat berpindah scene sehingga tidak dipengaruhi scene yang sebelumnya dibuka
- tab `Gambar Awal` memiliki dropdown ukuran aktif untuk menentukan ukuran gambar awal setiap scene
- tab MiniMax T2V dan I2V masing-masing menyediakan:
  - `Ukuran` yang mengikuti ukuran video project
  - FPS MiniMax H3 ditetapkan `24`
  - `Lora` dan kekuatannya
  - `Editor Prompt` interaktif untuk menyusun prompt Inggris langsung
  - tombol `Buat Prompt`
- tab `MINIMAX-H3_S2V` tidak menampilkan CFG atau Negative Prompt; prompt positif memakai object Ref2VA langsung dan tombol `Buat Prompt` mengikuti schema enam field Ref2VA
- tab `MINIMAX-H3_R2V` menyediakan `Ukuran`, FPS `24`, dua LoRA, manifest reference, dan prompt positif Ref2VA
- tab `MINIMAX-H3_S2V` menyediakan `Ukuran`, FPS `24`, dua LoRA, dan prompt positif Ref2VA
- saat model image `Gemini` dipilih:
  - field `Model Gemini` (image only) ditampilkan untuk memilih model Gemini spesifik
  - negative prompt dinonaktifkan
  - pengaturan seed statik dinonaktifkan
  - pengaturan Lora image dinonaktifkan
- tab `Prompt Tambahan` menyediakan 3 grup:
  - `Prompt Positif`
  - `Prompt Negatif`
  - tombol `Buat Image`
  - semua grup memakai aturan model/ukuran/seed/Lora/Gemini yang sama seperti tab `Gambar Awal`
- `Generate Caption` default aktif untuk project baru dan disimpan di `project_settings.json.caption`
- timing caption dihitung per-scene lalu caption dibakar sekali saat final compose jika `project_settings.caption.generate_caption` aktif
- untuk scene type `i2v`, `image_pan`, dan `image_zoom`:
  - durasi scene dapat diisi sebagai angka integer antara `1` sampai `15` detik
- untuk `image_pan`:
  - tab `Gambar Awal` tetap tersedia
  - tab `Image Pan` ditampilkan dengan input: `ukuran` (portrait-only), `direction`
  - durasi diatur dari field durasi scene di tab `Metadata`
  - tombol `Generate Image Awal` tetap aktif
- untuk `image_zoom`:
  - tab `Gambar Awal` tetap tersedia
  - tab `Image Zoom` ditampilkan dengan input: `ukuran`, `zoom_direction`, `focal_point`, `zoom_strength`
  - durasi diatur dari field durasi scene di tab `Metadata`
  - tombol `Generate Image Awal` tetap aktif
- saat `Compose Semua Adegan`, dialog compose juga menyediakan dropdown `Upscale`:
  - `Tanpa upscale`
  - `1.5x`
  - `2x`
  - jika dipilih `1.5x` atau `2x`, video final `combined_all.mp4` akan di-upscale langsung tanpa mengekspor frame PNG
- dialog compose menyediakan checkbox `Compose Lagu` untuk menyusun timeline audio speech scene yang didukung.
- tombol `Upscale Video` pada group `Scene` membuka dialog kecil untuk memilih `1.5x` atau `2x`
- hasil tombol `Upscale Video` disimpan sebagai file video baru di root scene aktif tanpa mengekspor frame PNG
- tab prompt yang masih aktif mempunyai tombol `Buat Prompt` yang meminta LLM membuat prompt Inggris sesuai tipe prompt
- tombol `Buat Prompt` pada semua tab MiniMax memakai referensi scene yang sesuai dan memuat object hasil langsung ke editor interaktif
- setelah Buat Prompt MiniMax berhasil, hasil langsung dimuat tanpa menunggu reload scene dan tanpa Save Scene pendahuluan
- setelah proses selesai dari UI, akan muncul popup:
  - informasi keberhasilan beserta file output yang terdeteksi
  - atau ringkasan error jika proses gagal

Menjalankan UI:
```powershell
.\.venv\Scripts\python.exe scene_manager_ui.py
.\run_ui.bat
```

Linux/macOS:
```bash
./.venv/bin/python scene_manager_ui.py
./run_ui.sh
```

Catatan:
- `run_ui.bat` otomatis memakai Python dari `.venv` sehingga tidak perlu aktivasi manual virtual environment.
- `run_ui.sh` otomatis memakai Python dari `.venv` dan menjalankan UI di background.

## Image Models

Implementasi domain image:
- `z_image/z_image.py`
- `flux2/flux2.py`
- `gemini/gemini_image.py`

Model yang tersedia:
- `Z-Image Turbo`
  - template normal: `api_template/z_image_api.json`
  - template Lora: `api_template/z_image_lora_api.json`
  - punya positive dan negative prompt
- `Flux.2`
  - template normal: `api_template/flux2_api.json`
  - template Lora: `api_template/flux2_lora_api.json`
  - tidak memakai negative prompt
- `Gemini`
  - generate image via Gemini API (tanpa ComfyUI workflow)
  - model Gemini spesifik dipilih dari `gemini_model_id`
  - request image size memakai mode strict `1K`
  - hasil diproses ke ukuran target scene/image dengan metode `scale + center crop` (tanpa stretching)
  - `json_api` disimpan sebagai `gemini_flash_05k`
  - tidak memakai negative prompt
  - tidak memakai seed statik dan Lora image

Resolusi image yang tersedia:
- `368x640`
- `480x848`
- `720x1280`
- `640x368`
- `848x480`
- `1280x720`

## Generate Initial Image

Script: `scripts/generate_initial_image.py`

Fungsi:
- membaca `z_image_prompt.json`
- prompt UI disimpan sebagai nilai langsung berbahasa Inggris dan runtime memakai nilai tersebut tanpa translasi
- `lora_trigger_words` dari `z_image_prompt.json` otomatis ditambahkan ke awal prompt positif saat generate gambar utama maupun prompt tambahan
- bisa juga membaca file prompt tambahan berbasis group untuk generate image alternatif dengan aturan model scene yang sama
- jalur model dipilih otomatis dari `z_image_prompt.json`
- jika model image scene adalah model biasa / ComfyUI:
  - membangun workflow image sesuai model yang dipilih
  - mengirim workflow ke ComfyUI
  - mendownload image hasil ke folder scene
- jika model image scene adalah `Gemini`:
  - generate image via Gemini API
  - simpan image hasil ke folder scene sesuai ukuran target scene (scale + center crop)

Contoh:
```powershell
.\.venv\Scripts\python.exe scripts\generate_initial_image.py --server 127.0.0.1:8188 --project demo_project --scene scene_1
.\.venv\Scripts\python.exe scripts\generate_initial_image.py --project demo_project --scene scene_1 --prompt-file z_image_extra_prompts.json --prompt-index 1
```

## Generate Cover Project

Script: `scripts/generate_cover_image.py`

Fungsi:
- membaca konfigurasi cover dari `project_settings.json.cover`
- saat tombol `Generate Cover` dijalankan, prompt cover disinkronkan dulu:
  - runtime hanya menormalisasi slot prompt lama ke nilai langsung saat project lama pertama kali dibaca
  - untuk ComfyUI, yang dikirim adalah nilai prompt langsung berbahasa Inggris
- perilaku ini berlaku sama untuk `positive_prompt` dan `negative_prompt`
- generate image cover sesuai model image (`ComfyUI` atau `Gemini`)
- menyimpan hasil final sebagai `api_production/<project_name>/cover/cover.png`

Contoh:
```powershell
.\.venv\Scripts\python.exe scripts\generate_cover_image.py --server 127.0.0.1:8188 --project demo_project
```

## Voice dan Sound

### Generate Voice

Script: `scripts/generate_voice.py`

Fungsi:
- membaca provider voice global dari `project_settings.json.voice`:
  - `gemini`
- membaca `voice_text` dan konfigurasi TTS per scene dari `scene_meta.json`
- jika model `gemini-3.1-flash-tts-preview`, memakai profile dan payload lama tanpa perubahan
- jika model `gemini-3.8-flash-tts`, memakai voice ID dari `gemini_tts_voice_id` dan transcript asli tanpa profile TXT lama
- prompt style dipilih dari `voice_character` (Lily/Lily - Ngaji/Lily - Arab)
- profile Gemini bisa diedit lewat file TXT di folder `gemini_voice_profile/`:
  - `Lily.txt`, `Lily Ngaji.txt`, `Lily Arab.txt`
- format TXT mengikuti pola prompt Gemini TTS: `# AUDIO PROFILE`, scene, director notes, sample context, lalu `#### TRANSCRIPT`
- `voice_text` runtime ditempel otomatis tepat di bawah `#### TRANSCRIPT`
- jika file TXT kosong atau tidak ada, sistem fallback ke profile bawaan di kode
- katalog voice Gemini 3.8 diambil dari Gemini Voices API dengan filter `language_code=en-US`; label UI hanya menggunakan nama voice seperti `Bodi` atau `Koda`
- saat menjalankan semua scene sekaligus, sistem mencoba mode konsisten per `voice_character`:
  - scene dikelompokkan berdasarkan `voice_character`
  - grup yang berisi lebih dari satu scene digabung menjadi satu transcript
  - grup yang hanya berisi satu scene tetap digenerate per scene
  - menyisipkan token `SCENEBREAKTOKEN` sebagai instruksi jeda panjang antar scene
  - menghasilkan satu WAV gabungan dan menyimpannya di `api_production/<project_name>/voice_combined/`
  - membagi WAV berdasarkan jeda panjang, lalu trim silence, snap akhir ke zero crossing, dan memberi fade-out pendek untuk mengurangi bunyi klik
  - jika deteksi jeda panjang gagal, proses fallback ke generate per scene
- scene yang memakai `gemini-3.8-flash-tts` diproses per scene dan tidak digabung dengan `SCENEBREAKTOKEN`
- file output voice selalu memakai awalan `speech_`

Contoh:
```powershell
.\.venv\Scripts\python.exe scripts\generate_voice.py --server 127.0.0.1:8188 --project demo_project --scene scene_1
.\.venv\Scripts\python.exe scripts\generate_voice.py --server 127.0.0.1:8188 --project demo_project
```

Contoh `keys.cfg`:
```ini
GEMINIKEY=isi_api_key_gemini
```

Catatan key Gemini:
- pencarian key Gemini dilakukan dengan urutan:
  - `GEMINIKEY` di `keys.cfg`
  - `GEMINI_API_KEY` di `keys.cfg` atau environment variable
  - `GOOGLE_API_KEY` di `keys.cfg` atau environment variable

## Caption Otomatis

Script pendukung: `scripts/generate_caption.py`

Fungsi:
- membaca `voice_text` dari `scene_meta.json`
- membersihkan audio tags seperti `[warmly]` agar tidak ikut tampil di subtitle
- memakai `faster-whisper` di CPU untuk membantu timing caption
- membagi caption menjadi beberapa potongan pendek
- burn subtitle sekali ke video final project setelah compose dan optional upscale

Perilaku:
- caption timing dihitung per-scene, tetapi burn dilakukan sekali ke `combined/combined_all.mp4` setelah final compose jika `project_settings.caption.generate_caption=true`
- sumber teks caption selalu dari `voice_text`
- `faster-whisper` hanya membantu menentukan waktu caption; isi teks tidak diambil dari hasil transkripsi
- caption final dibakar langsung ke video menggunakan renderer Pillow
- timing caption tetap dihitung berdasarkan audio dan voice text masing-masing scene, lalu diberi offset sesuai posisi scene pada timeline final
- pada `compose-song`, timing caption mengikuti chunk audio yang menjadi master timeline
- ukuran font caption memakai tinggi video final setelah upscale:
  - `font_size = ceil(final_height / 640 * 24)`
  - tinggi `640` menghasilkan font `24`
  - tinggi `368` menghasilkan font `14`
  - tinggi `848` menghasilkan font `32`
  - tinggi `1280` menghasilkan font `48`
- caption Arab dan non-Arab memakai font `Arial`, ukuran font, outline, dan margin bawah yang sama secara proporsional
- posisi caption dinaikkan sekitar `10%` dari tinggi video final agar tidak terlalu dekat dengan tepi bawah
- caption Arab dan non-Arab dirender dengan Pillow yang sama; Arabic memakai shaping RTL, sedangkan teks non-Arab memakai arah normal
- overlay Pillow dioptimalkan dengan band transparan bawah dan satu layer video, bukan satu PNG Full HD untuk setiap caption
- burn caption dilakukan setelah background music dan upscale final agar posisi dan ukuran mengikuti dimensi aktual `combined_all.mp4`

### Caption bahasa Arab

- setiap entry caption diperiksa berdasarkan karakter Unicode Arab
- teks Arab dipertahankan dalam urutan logis persis seperti sumbernya; aplikasi tidak membalik karakter atau urutan kata secara manual
- entry Arab dirender menggunakan Pillow dengan Arabic shaping dan arah `rtl`, kemudian ditempel sebagai overlay ke video
- entry non-Arab dirender menggunakan Pillow yang sama dengan entry Arab
- jika satu video memiliki entry Arab dan non-Arab, semua entry masuk ke satu layer overlay yang sama
- teks campuran Arab dengan tanda baca atau angka tetap diberi anchor RTL agar urutan bacanya stabil
- scene yang sudah memiliki video caption lama harus diproses ulang agar perubahan renderer Arab diterapkan

Catatan:
- `faster-whisper` akan mengunduh model saat pertama kali dipakai
- model default caption saat ini adalah `base`

## Compose Video

Script: `scripts/generate_compose.py`

Fungsi:
- compose per scene ke folder `api_production/<project_name>/combined` dengan mix audio:
  - `minimax-h3_s2v` dan `minimax-h3_r2v`: mempertahankan speech/audio bawaan video dan tidak mencampurkan ulang file `speech_*`
  - `minimax-h3_i2v` dan `minimax-h3_t2v`: mempertahankan audio hasil ComfyUI lalu mencampurkannya dengan file `speech_*`
  - video root MiniMax tetap merupakan video asli hasil ComfyUI; master audio tidak dicampurkan dan tidak menimpa file video pada tahap generation
  - saat Compose Scene/Compose All dijalankan, master audio ComfyUI dibuat dari video root ke `.comfy_audio_source/audio.wav` jika cache belum ada, lalu dipakai untuk membangun mix tanpa menggandakan audio scene
  - Compose All memakai satu video final terbaru untuk scene MiniMax H3
  - scene type lain: mix speech ke video scene
- merge semua hasil scene di `combined` menjadi `combined_all.mp4`
- dari setiap nomor scene, hanya video output terbaru yang dipakai untuk proses merge; file output scene lama tidak ikut digabungkan
- jika `project_settings.caption.generate_caption=true`, caption timing setiap scene dikumpulkan setelah video scene siap, lalu caption dibakar sekali ke `combined_all.mp4` setelah merge, background music, dan upscale final
- ukuran master compose selalu diambil dari `project_settings.json.video_size`, bukan dari resolusi video scene pertama
- FPS master compose dipilih dari FPS tertinggi seluruh video scene terbaru yang akan digabungkan; scene dengan FPS lebih rendah dinormalisasi ke FPS tersebut
- setiap video scene dinormalisasi ke ukuran master project menggunakan `scale + pad`; aspect ratio dipertahankan dan video sumber tidak ditimpa
- sebelum merge dengan `-c copy`, parameter audio utama (codec, sample rate, jumlah channel, dan layout) dibandingkan; jika berbeda antar-scene, setiap video dinormalisasi ke AAC stereo `44100 Hz` agar konfigurasi AAC tidak berubah di tengah `combined_all.mp4`
- jika `--compose-song` aktif, semua video scene selalu dinormalisasi dan di-re-encode sebelum penggabungan, walaupun fps, resolusi, dan signature audio awalnya sama; hal ini mencegah encoder padding membuat celah audio di batas scene
- opsi `--compose-song` menjadikan audio `speech_chunk_*` dari setiap scene sebagai master timeline: semua chunk didekode, di-resample ke `44100 Hz` stereo, timestamp di-reset, lalu digabung tanpa jeda; setiap video scene dipotong/diatur mengikuti durasi chunk audionya
- pada `--compose-song`, video scene dinormalisasi ke FPS master tertinggi sebelum retime audio; hasil concat video-only dipaksa kembali ke FPS master tersebut sebelum audio Lagu di-mux
- pada mode `--compose-song`, audio scene bawaan video tidak dipakai sebagai timeline akhir; video scene digabung tanpa audio, kemudian master audio Lagu di-mux sebagai AAC `192 kbps`, `44100 Hz`, stereo
- pada merge akhir bisa menambahkan background music opsional:
  - file music dari folder `music` dengan ekstensi `.m4a`, `.mp3`, `.wav`
  - music bisa kosong (tidak dipilih)
  - volume music bisa diatur dari `0.00` sampai `2.00`
  - music dipotong jika lebih panjang dari video
  - music diulang jika lebih pendek dari video
  - fade out `0.5` detik pada akhir setiap segmen music (termasuk saat loop dan akhir video)
  - track music dinormalisasi ke `44100 Hz` stereo sebelum di-mix dengan audio utama
  - audio utama dan music diubah ke format `44100 Hz` stereo sebelum `amix`; speech/audio scene tetap dipertahankan sebagai track utama
- jika folder `cover` berisi gambar, gambar pertama dipakai sebagai intro `2 frame` di awal video final
- merge akhir dibuat sederhana:
  - jika fps, resolusi master, dan signature audio scene seragam, concat langsung `-c copy`
  - jika fps, resolusi, atau signature audio berbeda, normalisasi lalu merge
  - jika `Compose Lagu` aktif, selalu gunakan jalur normalisasi dan re-encode khusus Lagu
- upscale `1.5x` atau `2x` dilakukan setelah `combined_all.mp4` selesai dibuat
  - project `368x640` menghasilkan final `368x640`, lalu `2x` menghasilkan `736x1280`
  - project `480x848` menghasilkan final `480x848`, lalu `2x` menghasilkan `960x1696`
- mode `--compose-per-scene` membuat satu output untuk setiap scene tanpa membuat `combined_all.mp4`:
  - hanya video terbaru berdasarkan waktu modifikasi di folder scene yang digunakan
  - scene yang sudah memiliki audio compose diekspor tanpa mencampurkan ulang voice/sound
  - music yang sama di-loop atau dipotong agar sesuai durasi masing-masing video scene
  - volume music dan scale diterapkan pada setiap output scene secara terpisah
  - output tetap disimpan sebagai `combined/Scene_<nomor>_<judul>.mp4`

Di UI:
- tersedia tombol `Compose Semua Adegan`
- saat `Compose Semua Adegan`, muncul dialog untuk memilih music, volume, dan checkbox `Compose Lagu`
- tersedia tombol `Compose Per Scene`; dialognya memiliki pilihan music, volume, dan scale tanpa opsi `Compose Lagu`
- `Compose Per Scene` menghasilkan satu video per scene dari video terbaru dan tidak membuat `combined_all.mp4`
- tombol `2x` di group Compose menjalankan upscale GAN untuk root scene yang memiliki `upscale=true`
Contoh:
```powershell
.\.venv\Scripts\python.exe scripts\generate_compose.py --project demo_project --scene scene_1
.\.venv\Scripts\python.exe scripts\generate_compose.py --project demo_project --scene scene_1 --scene scene_2
.\.venv\Scripts\python.exe scripts\generate_compose.py --project demo_project
.\.venv\Scripts\python.exe scripts\generate_compose.py --project demo_project --music-file ".\\music\\Another Night (Corporate).m4a" --music-volume 1.00
.\.venv\Scripts\python.exe scripts\generate_compose.py --project demo_project --compose-per-scene --music-file ".\\music\\Another Night (Corporate).m4a" --music-volume 1.00 --upscale-factor 1.5
.\.venv\Scripts\python.exe scripts\generate_compose.py --project song_allah_mendengar_semua_doa --compose-song
```

Catatan:
- `ffmpeg` dan `ffprobe` harus tersedia di `PATH`
- jangan menjalankan `generate_compose.py` paralel untuk project yang sama karena semua proses menulis ke folder `combined` yang sama

## Backup Production ZIP

Script: `backup_production.py`

Fungsi:
- membuat file ZIP yang berisi satu folder project aktif
- output disimpan ke folder `backup_production`
- nama file ZIP selalu `<project_name>.zip`

Argumen:
- `--project`, `-p`
  - nama project yang akan dibackup

Contoh:
```powershell
.\.venv\Scripts\python.exe backup_production.py --project demo_project
```

Di UI:
- tombol `Save` ada di grup `Backup`
- saat diklik, UI akan konfirmasi backup project aktif dengan nama file tetap `<project_name>.zip`

## MiniMax H3 T2V Workflow

Scene type: `minimax-h3_t2v`

Implementasi adapter:

- `minimax_h3_t2v/minimax_h3_t2v.py`
- `api_template/minimax_h3_t2v_api.json`

File prompt scene:

- `minimax_h3_t2v_prompt.json`

File memakai satu `positive_prompt` object JSON langsung berbahasa Inggris. Scene MiniMax H3 tidak memakai `negative_prompt`. Konfigurasi `lora_name` dan `lora_strength` harus berasal dari folder `MINIMAX-H3` di ComfyUI.

Setiap tab MiniMax H3 memiliki input `Jumlah Step` di bawah prompt. Untuk kompatibilitas dengan file scene lama, nilainya tetap disimpan pada key `h3_cache.steps`:

```json
"h3_cache": {
  "steps": 20
}
```

Nilai `h3_cache.steps` diterapkan ke input `steps` pada `BasicScheduler` untuk workflow normal.

#### Penggunaan LoRA

Semua tab MiniMax H3 menyediakan checkbox `Pakai Lora` di atas pilihan LoRA. Checkbox ini secara bawaan tidak aktif. Jika tidak dicentang, jalur LoRA 1 dan LoRA 2 dilewati dan workflow memakai model dasar secara langsung. Jika dicentang, kedua pilihan LoRA dan kekuatannya digunakan sesuai konfigurasi scene.

Nilai checkbox disimpan pada key `use_lora`.

#### Mode Cepat FastH3

Tab MiniMax H3 T2V, I2V, R2V, S2V, I2V-Panjang, dan R2V-Panjang menyediakan checkbox `Mode Cepat`. Nilainya disimpan sebagai `fast_mode` pada file prompt. Jika aktif, runtime memilih template FastH3 berikut:

- T2V: `api_template/minimax_fasth3_t2v_api.json` melalui `minimax_h3_t2v/minimax_h3fast_t2v.py`;
- I2V: `api_template/minimax_fasth3_i2v_api.json` melalui `minimax_h3_i2v/minimax_h3fast_i2v.py`;
- R2V/S2V: `api_template/minimax_fasth3_r2v_api.json` melalui builder R2V.

Mode ini hanya mengekspos prompt, durasi, resolusi, LoRA 1, dan LoRA 2. FastH3 selalu memakai 8 step dan FPS `24`; input jumlah step disembunyikan dan tidak digunakan pada Mode Cepat. Pada scene panjang, satu `fast_mode` pada prompt root berlaku seragam untuk seluruh proses dan frame carry tetap diinjeksi oleh runtime pada proses berikutnya.

Koneksi model normal tetap melewati kedua LoRA secara berurutan:

```text
UNETLoader → LoRA 2 → LoRA 1 → BasicScheduler/BasicGuider
```

LoRA 1 tidak boleh dihubungkan langsung ke `UNETLoader`, karena hal tersebut akan membypass LoRA 2.

Validasi field Steps: integer `4`-`50`.

Aturan durasi:

- durasi scene adalah angka `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame;
- seluruh durasi dijalankan oleh satu workflow T2V;
- contoh `13.2` menjalankan T2V selama `13.2` detik.

Secara default audio hasil ComfyUI dipertahankan di video root, lalu saat Compose dibuat sebagai master `.comfy_audio_source/audio.wav` jika cache belum ada dan dicampur dengan speech.

Kontrol audio:

- tab `MINIMAX-H3_T2V` memiliki checkbox `Hapus Sound` untuk output T2V;
- setelah file video selesai diunduh, seluruh frame hasil generasi dipertahankan;
- jika `Hapus Sound` dicentang, audio output dihapus sebelum proses audio scene berikutnya.

Node workflow utama:

- T2V:
  - durasi: node `133`, input `value`
  - jalur model: `127` ke `136` lalu `135`
  - node Steps: `124`, dioverwrite dari konfigurasi tab
  - resolusi: node `115` (`ResolutionSelector`)
  - FPS workflow tetap `24` pada node `130`; expression frame pada node `132` menggunakan FPS `24`
- LoRA: node `135`
- LoRA kedua: node `136`; konfigurasi disimpan sebagai `lora_name_2` dan `lora_strength_2`

Untuk scene `minimax-h3_s2v` dan `minimax-h3_r2v`, saat LoRA aktif jalur model adalah `127` ke `157` lalu `156`, dan node Steps `124` dioverwrite dari konfigurasi tab. Saat LoRA tidak aktif, kedua node tersebut dihapus dari payload dan node pemakai model kembali langsung ke `127`. S2V menggunakan adapter R2V yang sama.

Prompt MiniMax H3 mengikuti:

- `api_production/AGENT-SKILLS/MINIMAX-H3/SKILL.md`
- `api_production/AGENT-SKILLS/MINIMAX-H3/references/base-en.txt`
- `api_production/AGENT-SKILLS/SCENE-MINIMAX-H3-T2V.md`

## MiniMax H3 I2V Workflow

Scene type: `minimax-h3_i2v`

- durasi berupa angka `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame
- tab berurutan: `Meta`, `Gambar Awal`, `Image Edit`, `MINIMAX-H3_I2V`, `Aset`
- gambar terbaru di root scene menjadi `Picture 1` dan input node `LoadImage`
- hanya workflow MiniMax H3 I2VA yang dijalankan; tidak ada stage T2V
- setelah output ComfyUI diunduh, seluruh frame hasil generasi MiniMax dipertahankan;
- secara default audio hasil ComfyUI dipertahankan di video root dan baru dicampur dengan speech saat Compose; master audio dibuat saat Compose di `.comfy_audio_source/audio.wav`
- tab `MINIMAX-H3_I2V` memiliki checkbox `Hapus Sound`; jika aktif, audio output ComfyUI dihapus setelah video selesai diunduh dan sebelum proses audio scene berikutnya; Compose tidak membuat master dari video yang sudah tidak memiliki audio
- prompt utama ada di `minimax_h3_i2v_prompt.json` dan tidak memiliki `negative_prompt`
- prompt I2VA langsung divalidasi memakai aturan prompt MiniMax H3 dan menolak format yang tidak valid
- LoRA pertama dan kedua dibaca dari `lora_name`/`lora_strength` serta `lora_name_2`/`lora_strength_2` pada file prompt dan folder `MINIMAX-H3`
- ukuran scene pada prompt JSON diterjemahkan ke `aspect_ratio` dan `megapixels` pada node `ResolutionSelector`
- FPS workflow ditetapkan `24`; nilai FPS diterapkan ke node `132` dan expression frame node `134`
- tombol `Buat Prompt` memakai `SCENE-MINIMAX-H3-I2V.md`, `MINIMAX-H3/SKILL.md`, `MINIMAX-H3/references/base-en.txt`, serta mode I2VA
- checkbox `Mode Cepat` memilih workflow FastH3 tanpa mengubah schema prompt dan tetap memakai dua LoRA yang sama

## MiniMax H3 I2V Panjang Workflow

Scene type: `minimax-h3_i2v-panjang`

- workflow dasar setiap stage memakai `api_template/minimax_h3_i2v_api.json`; jika `fast_mode` aktif, semua stage memakai `api_template/minimax_fasth3_i2v_api.json`
- tombol `Buat Prompt` memakai `SCENE-MINIMAX-H3-I2V-PANJANG.md`, `MINIMAX-H3/SKILL.md`, `MINIMAX-H3/references/base-en.txt`, serta mode I2VA dengan instruksi first/last frame
- setiap stage aktif menerima dua image referensi dalam urutan first frame lalu last frame
- first frame dan last frame dapat dipilih dari image lokal atau frame terakhir stage sebelumnya; keduanya wajib valid
- setelah stage selesai, frame terakhir diekstrak dan di-upload kembali sebagai input stage berikutnya
- jumlah stage adalah `continuations + 1`, dengan maksimum 4 stage
- file `minimax_h3_i2v_panjang_prompt.json` mempunyai struktur root:

```json
{
  "continuations": 1,
  "run_start_stage": 1,
  "prompts": [
    {},
    {},
    {},
    {}
  ],
  "stage_references": [
    {
      "first": {"source": "scene", "name": "awal.png"},
      "last": {"source": "scene", "name": "akhir.png"}
    },
    {
      "first": {"source": "stage_last", "stage": 1, "name": ""},
      "last": {"source": "scene", "name": "akhir-2.png"}
    },
    {
      "first": {"source": "stage_last", "stage": 2, "name": ""},
      "last": {"source": "scene", "name": "akhir-3.png"}
    },
    {
      "first": {"source": "stage_last", "stage": 3, "name": ""},
      "last": {"source": "scene", "name": "akhir-4.png"}
    }
  ]
}
```

- `prompts` selalu berisi tepat 4 item; hanya item sampai `continuations + 1` yang dijalankan
- setelah scene berhasil menjalankan proses, final dibangun dari semua file yang tersedia dengan pola `minimax_h3_i2v_panjang_segment_<nomor>.mp4`
- segment diurutkan berdasarkan nomor secara numerik; video dengan nama lain, final lama, dan file temporary tidak ikut digabungkan
- minimal satu segment harus tersedia dan valid; segment yang ditemukan tetapi kosong atau tidak valid membuat finalisasi scene gagal dan file final lama tidak ditimpa
- `run_start_stage` menentukan proses awal: `1` menjalankan normal, sedangkan `2`, `3`, atau `4` menjalankan proses mulai dari tab tersebut sampai proses aktif terakhir
- saat partial run, validasi prompt hanya dilakukan untuk proses mulai dari `run_start_stage` sampai proses aktif terakhir
- untuk partial run, segment video dari proses sebelum `run_start_stage` harus sudah ada; file frame terakhir akan digunakan jika ada atau dibuat ulang dari segment tersebut
- setiap proses yang selesai selalu menyimpan frame terakhirnya agar dapat dipakai sebagai referensi pada run berikutnya
- setiap item memakai schema I2VA dan `mode: "I2VA"`
- setiap stage aktif harus memiliki `first` dan `last` pada `stage_references`; nilai `source: "none"` tidak valid
- FastH3 I2V tetap menginjeksi `last_frame` secara dinamis pada setiap stage lanjutan; FastH3 memakai 8 step dan tidak memakai input Steps normal
- setiap prompt lanjutan divalidasi secara runtime sebelum stage dijalankan
- semua segment yang tersedia digabung berurutan menjadi `minimax_h3_i2v_panjang_final.mp4`, terlepas dari nilai `continuations` atau `run_start_stage`
- color match dilakukan setelah seluruh stage digabung, menggunakan frame pertama video gabungan sebagai referensi
- utilitas CLI `scripts/color_match_video.py` juga dapat digunakan untuk memproses video terhadap frame pertamanya; audio dipertahankan
- contoh: `.\.venv\Scripts\python.exe scripts\color_match_video.py --project ohyes --scene 3`
- audio ComfyUI dan voice tetap mengikuti aturan Compose scene MiniMax H3

## MiniMax H3 R2V Panjang Workflow

Scene type: `minimax-h3_r2v-panjang`

- memakai empat proses R2V berantai dengan template `api_template/minimax_h3_r2v_api.json` yang sama pada setiap proses
- file prompt `minimax_h3_r2v_panjang_prompt.json` memiliki `prompts[4]`, `prompt_instructions[4]`, `continuations`, `run_start_stage`, dan reference global
- maksimal empat Picture global dikirim dalam urutan `references.images`; `references.initial_image` opsional dipakai hanya Proses 1 sebagai Picture setelah semua Picture global
- proses 2–4 menambahkan frame terakhir proses sebelumnya sebagai Picture setelah semua Picture global
- frame carry diekstrak dari segment proses sebelumnya, tidak dipilih manual, dan tidak ditulis ke `references.images`
- maksimal tiga Audio global dan satu Video global dipakai pada seluruh proses
- `run_start_stage` hanya boleh melewati proses yang segment dan frame carry-nya sudah tersedia
- setiap proses aktif memvalidasi prompt Ref2VA dan manifest token sebelum workflow dikirim
- segment disimpan sebagai `minimax_h3_r2v_panjang_segment_<nomor>.mp4`; semua segment yang tersedia digabung secara numerik menjadi `minimax_h3_r2v_panjang_final.mp4`
- color match dilakukan setelah penggabungan segment
- frame terakhir setiap proses tetap disimpan sebagai `minimax_h3_r2v_panjang_frame_<nomor>.png` untuk proses berikutnya atau partial run
- mode suara, FastH3, LoRA, cache, dan resolusi berlaku global untuk seluruh proses

## MiniMax H3 R2V Workflow

Template workflow:

- `api_template/minimax_h3_r2v_api.json`
- FastH3: `api_template/minimax_fasth3_r2v_api.json`
- node utama: `136` (`MiniMaxH3ReferenceToVideo`)
- prompt dikirim langsung ke `136.inputs.prompt`
- resolusi dibaca dari node `115` (`ResolutionSelector`)
- durasi dibaca dari node `132` (`PrimitiveFloat`)
- durasi menerima angka desimal `0.0` sampai `15.0` dengan maksimal 4 angka desimal; durasi `0.0` menghasilkan output minimum 5 frame
- FPS workflow ditetapkan `24`; nilai FPS diterapkan ke node `130` dan expression frame node `131`
- LoRA pertama memakai node `156`, sedangkan LoRA kedua memakai node `157`
- field prompt `lora_name`/`lora_strength` dan `lora_name_2`/`lora_strength_2` diisi melalui dropdown UI
- output video disimpan melalui node `92`
- setelah proses selesai, frame pertama dan terakhir video diekstrak ke file dengan pola `<nama_file_video>_first_frame.png` dan `<nama_file_video>_last_frame.png` di folder scene
- jika `fast_mode=true`, workflow memakai FastH3 Ref2VA dengan 8 step, Sigma Shift `12/3`, dan Model Sparse Attention mulai `0.00`

Workflow ini memakai mode full-reference `Ref2VA` dari skill `MINIMAX-H3`. Pada file prompt scene, authoring memakai `style_opening` dan `shots[]` dengan item shot yang sama seperti `T2VA`/`I2VA`. Sebelum dikirim ke ComfyUI, adapter mengompilasi keduanya menjadi section runtime `detailed_description`. Payload runtime tetap mempunyai enam section Ref2VA berikut secara berurutan:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

Semua section ditulis dalam bahasa Inggris. Bahasa asli hanya dipertahankan untuk dialog, lirik, dan teks yang terlihat di dalam scene. JSON authoring tidak lagi memakai wrapper bahasa atau metadata translasi.

Tab R2V dapat memilih maksimal 5 gambar, 3 audio, dan 1 video sebagai reference. Reference yang dipilih diberi nomor berurutan mulai dari `Picture 1`, `Audio 1`, atau `Video 1`; reference yang tidak dipilih tidak dikirim ke workflow.

- Gambar memakai dropdown bernomor `Picture 1` sampai `Picture 5`; audio memakai `Audio 1` sampai `Audio 3`. Tombol naik/turun menukar urutan slot yang terisi.
- Urutan slot mengikuti array `references.images` dan `references.audios` dalam `minimax_h3_r2v_prompt.json`. Struktur JSON tetap sama; hanya daftar pilihan file di dropdown yang diurutkan abjad, bukan referensi terpilih.
- Slot diisi berurutan tanpa celah dan file yang sudah dipakai tidak ditawarkan pada slot lain. Memilih `(Tidak dipakai)` menghapus slot tersebut dan menggeser referensi sesudahnya ke atas.
- Save, reload scene, dan refresh aset mempertahankan urutan. File referensi yang hilang tetap berada di slot semula dengan label `tidak ditemukan`, sehingga nomor referensi lain tidak berubah otomatis.
- Buat Prompt memakai urutan yang sama dengan ComfyUI. Perubahan referensi menampilkan pengingat untuk memeriksa nomor pada prompt; hasil LLM tidak diterapkan jika scene atau susunan referensi berubah selama proses Buat Prompt.

### Pemetaan input R2V

| Label prompt | Slot workflow |
| --- | --- |
| `<Picture 1>` | `ref_images.ref_image_0` |
| `<Picture 2>` | `ref_images.ref_image_1` |
| `<Picture 3>` | `ref_images.ref_image_2` |
| `<Picture 4>` | `ref_images.ref_image_3` |
| `<Picture 5>` | `ref_images.ref_image_4` |
| `<Video 1>` | `ref_videos.ref_video_0` |
| audio sinkron dari `<Video 1>` | `ref_video_audios.ref_video_audio_0` |
| `<Audio 1>` | `ref_audios.ref_audio_0` |
| `<Audio 2>` | `ref_audios.ref_audio_1` |
| `<Audio 3>` | `ref_audios.ref_audio_2` |

`<Picture N>`, `<Video N>`, dan `<Audio N>` memiliki penomoran independen. Audio yang ikut di dalam `Video 1` dapat diberi label audio tersendiri apabila perannya perlu dijelaskan secara eksplisit, misalnya:

```text
<Video 1> is the source video for the target video edit.
<Audio 4> is the synchronized audio track of <Video 1> and is reused in the target video.
```

`<Audio 4>` adalah label semantik prompt, bukan berarti audio tersebut masuk ke `ref_audios.ref_audio_3`. Koneksi teknisnya tetap `ref_video_audios.ref_video_audio_0`.

### Aturan label referensi

- `<Subject N>` mengidentifikasi orang, hewan, objek, lingkungan, pakaian, pose, aksi, atau konten visual yang digunakan dalam video.
- `<Picture N>` digunakan jika gambar menjadi frame awal, keyframe, frame akhir, atau anchor komposisi/storyboard.
- `<Video N>` digunakan untuk sumber editing, continuation, gerakan kamera, cut, ritme, atau struktur temporal.
- `<Audio N>` digunakan untuk audio yang disalin atau direferensikan: musik, voice timbre, dialog, lirik, sound effect, beat, atau continuity.
- Jika karakter dari `Video 1` dipakai sebagai konten visual, karakter tersebut tetap diberi `<Subject N>`; `<Video 1>` hanya menandai sumber video.
- Label yang sudah ditetapkan harus konsisten di keenam section.
- Token dalam tanda `<...>` tidak boleh diubah, termasuk `<Subject N>`, `<Picture N>`, `<Video N>`, dan `<Audio N>`.

### Bentuk payload runtime Ref2VA

Contoh minimal payload yang dikirim ke workflow setelah `style_opening + shots[]` dikompilasi:

```text
subject_definitions:
<Subject 1> is the woman whose appearance comes from <Picture 1> and whose movement comes from <Video 1>.
<Picture 1> is the opening composition reference for [Shot 1].
<Video 1> is the source video for the target video edit.
<Audio 1> is the standalone voice-timbre reference for <Subject 1> (S1).
<Audio 4> is the synchronized audio track of <Video 1> and is reused in the target video.

summary:
[video editing + audio reuse + keyframe completion] The target video adapts <Video 1> while preserving <Subject 1>, beginning from the composition established by <Picture 1>, and reusing the synchronized audio from <Audio 4>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - the subject's identity and clothing are retained.
<Picture 1> ([Shot 1] first frame): fully_preserved - its opening composition is retained.
<Video 1> (source video structure): partially_preserved - its movement and timing are adapted.
<Audio 1>: reference - its voice timbre guides <Subject 1> (S1) without copying the signal.
<Audio 4>: fully_copy - the synchronized audio from <Video 1> is reused in the target video.

detailed_description:
The target video uses a cinematic live-action style with soft natural lighting.
[Shot 1] The scene begins from <Picture 1>. <Subject 1> stands in the same position and clothing while the adapted motion and temporal structure of <Video 1> unfold. The synchronized audio from <Audio 4> remains audible throughout the shot. <Subject 1> (S1) speaks using the voice timbre referenced from <Audio 1>, saying, <d>[English] Welcome home.</d>

overall_soundscape:
The copied ambient layer from <Audio 4> continues throughout the target video.

non_diegetic_music:
N/A
```

Aturan tambahan:

- `summary` dimulai dengan task-type dalam tanda kurung siku, misalnya `[reference generation]`, `[video editing + audio reuse]`, atau gabungan beberapa task type.
- Jangan menganggap keberadaan video/audio otomatis berarti `video editing` atau `audio reuse`; gunakan task type sesuai peran sebenarnya.
- `retention_analysis` memakai marker tetap: `fully_preserved`, `partially_preserved`, `attribute_transfer`, `weak_reference`, `fully_copy`, `reference`, atau `weak_reference`.
- `detailed_description` adalah bagian utama dan menjelaskan video berdasarkan urutan playback, shot, komposisi, subjek, aksi, kamera, suara, dialog, serta titik penggunaan referensi.
- T2V, I2V, dan R2V memakai rentang waktu eksplisit pada setiap shot: `[Shot N] From X.XX to Y.YY seconds, ...`. Parser R2V tetap menerima format lama `[Shot N] At MM:SS.mmm, ...` untuk kompatibilitas project lama.
- Speaker memakai ID stabil `(S1)`, `(S2)`, dan seterusnya. Dialog/lyrics ditulis dalam `<d>[Language] ...</d>`.
- Dialog dan lirik lengkap hanya ditulis di `detailed_description`, bukan di `overall_soundscape` atau `non_diegetic_music`.

Adapter `minimax_h3_r2v/minimax_h3_r2v.py` menyediakan builder workflow in-memory sesuai manifest referensi scene. Adapter ini dipakai oleh scene `minimax-h3_s2v`.

## MiniMax H3 S2V Workflow

Scene type: `minimax-h3_s2v`

Scene ini memakai tab dan alur S2V MiniMax H3, dengan perbedaan berikut:

- tab `Gambar Awal` tetap tersedia;
- tab utama bernama `MINIMAX-H3_S2V`;
- urutan tab: `Meta`, `Gambar Awal`, `MINIMAX-H3_S2V`, `Aset`;
- tab utama memiliki `Ukuran`, dua LoRA, `Prompt Positif`, dan `Buat Prompt`; FPS workflow tetap `24` tanpa dropdown UI;
- tidak ada `CFG` dan `Prompt Negatif`;
- workflow sumber default adalah `api_template/minimax_h3_r2v_api.json`;
- hanya Picture 1 dan Audio 1 yang digunakan.

Pemetaan input runtime:

- gambar terbaru di root scene di-upload ke node `143` (`Picture 1`), lalu masuk ke `ref_images.ref_image_0`;
- audio speech terbaru yang berawalan `speech_` di root scene di-upload ke node `153` (`Audio 1`), lalu masuk ke `ref_audios.ref_audio_0`;
- workflow hanya menggunakan Picture 1 pada node `143` dan Audio 1 pada node `153`.

Durasi:

- durasi scene tidak ditentukan dari dropdown Meta;
- durasi dibaca dari file audio speech yang dipilih memakai `ffprobe`;
- audio dengan durasi lebih dari `15` detik membuat scene tidak dapat dijalankan;
- durasi audio dimasukkan langsung ke node `132` (`PrimitiveFloat`), yang menjadi sumber panjang frame node `131`;
- setelah output video diunduh, seluruh frame hasil generasi dipertahankan; penyesuaian durasi dilakukan pada WAV sebelum workflow dikirim.
- FPS workflow ditetapkan `24` pada node `130` dan expression frame node `131`.
Ukuran mengikuti mapping `ResolutionSelector` MiniMax H3 yang sama dengan scene MiniMax H3 lainnya. Prompt memakai mode `Ref2VA` dengan enam section skill MINIMAX: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, dan `non_diegetic_music`.

## Format Prompt MiniMax H3

### Editor Interaktif

Tab MiniMax H3 menampilkan editor prompt interaktif langsung di dalam tab scene, berdampingan dengan `Buat Prompt`. Editor ini membantu menyusun shot, timeline, visual, aksi, kamera, dialog, suara diegetik, dan dua audio global tanpa menampilkan JSON kepada pengguna.

- editor T2VA dan I2VA menyimpan object langsung dengan struktur `mode`, `shots`, `overall_soundscape`, dan `non_diegetic_music`;
- editor I2V-Panjang tersedia pada setiap stage dan tetap mempertahankan `prompts[4]` serta `stage_references[4]`;
- editor Ref2VA untuk R2V dan S2V mempertahankan section Ref2VA; seluruh section tersedia melalui scroll vertikal editor;
- editor R2V memakai kartu bidikan yang dapat ditambah atau dihapus dan mengompilasinya ke `detailed_description` saat runtime;
- scene baru mengisi prompt default langsung dalam bahasa Inggris;
- JSON tetap disimpan sesuai schema scene dan dikelola internal oleh aplikasi; `Buat Prompt` memakai LLM hanya untuk membuat prompt Inggris;
- runtime tidak menerjemahkan prompt.
- FL2VA dan L2VA masih menjadi profile panduan, bukan mode runtime yang dapat dipilih, karena validator dan serializer saat ini hanya menerima T2VA/I2VA untuk prompt terstruktur.

Kontrak file yang disimpan untuk T2VA/I2VA:

```json
{
  "positive_prompt": {
    "mode": "T2VA",
    "shots": [],
    "overall_soundscape": "...",
    "non_diegetic_music": "..."
  },
  "lora_name": "MINIMAX-H3/example.safetensors",
  "lora_strength": 1.0,
  "width": 368,
  "height": 640
}
```

Aturan bahasa dan sinkronisasi:

- label UI berbahasa Indonesia, tetapi isi prompt yang disimpan dan dikirim ke workflow berbahasa Inggris;
- `Buat Prompt` meminta LLM mengembalikan object langsung sesuai schema mode aktif;
- Save hanya memvalidasi dan menyimpan object prompt langsung;
- runtime menserialisasi object tersebut ke format text yang diminta MiniMax, tanpa translasi.

Struktur satu item `shots`:

```json
{
  "shot_id": "Shot 1",
  "start": 0.0,
  "end": 2.5,
  "visual": "Deskripsi komposisi, subjek, lingkungan, gaya, dan pencahayaan.",
  "action": "Aksi atau perubahan keadaan subjek selama shot.",
  "camera": "Framing, posisi, atau gerakan kamera.",
  "dialogue": "Dialog pada shot atau string kosong.",
  "diegetic_sound": "Suara yang benar-benar terjadi di dalam adegan."
}
```

Aturan multi-shot:

- `shots` minimal berisi satu item
- `shot_id` wajib string berurutan: `Shot 1`, `Shot 2`, dan seterusnya
- shot pertama mulai pada `0.0`; waktu harus meningkat, tidak tumpang tindih, dan akhir shot terakhir mengikuti durasi stage
- setiap shot wajib mempunyai `visual`, `action`, `camera`, `dialogue`, dan `diegetic_sound`
- `overall_soundscape` dan `non_diegetic_music` berada di luar `shots` karena berlaku untuk keseluruhan video
- perubahan kecil jarak/sudut sebaiknya dinyatakan sebagai camera motion dalam shot yang sama; cut baru harus memberikan informasi visual, ruang, keadaan, sudut pandang, atau waktu yang baru
- identitas karakter, pakaian, objek, layout, pencahayaan, serta ID pembicara harus konsisten lintas shot

T2VA tidak memiliki field `reference`. I2VA wajib menambahkan:

```json
"reference": {
  "instruction": "fully referenced",
  "picture": "Picture 1",
  "source": "[Shot 1]",
  "time": 0.0
}
```

Saat dikirim ke ComfyUI, object prompt langsung diserialisasi menjadi tiga bagian:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description:
[Shot 1] From 0.00 to 2.50 seconds, visual: ...; action: ...; camera: ...; dialogue: ...; diegetic sound: ....
[Shot 2] From 2.50 to 5.00 seconds, visual: ...; action: ...; camera: ...; dialogue: ...; diegetic sound: ....

overall_soundscape: ...

non_diegetic_music: ...
```

Baris reference hanya ada untuk I2VA. T2VA langsung dimulai dari `integrated_multimodal_description`.

Token yang wajib dipertahankan persis selama authoring dan serialisasi JSON MiniMax:

- semua substring dalam `<...>`, termasuk `<Subject N>`, `<Picture N>`, `<Video N>`, `<Audio N>` dan nomor aktualnya
- token kontrol `<d>`, `</d>`, `<scenetrans>`, dan `<cutoff>`
- identifier `[Shot N]`, `(S1)`, `(S2)`, `(S1,S2)`, serta mode `T2VA`, `I2VA`, `FL2VA`, `L2VA`, dan `Ref2VA`

Mapping ukuran scene MiniMax H3 ke `ResolutionSelector`:

| Ukuran | `aspect_ratio` | `megapixels` |
| --- | --- | ---: |
| `368x640` | `9:16 (Portrait Widescreen)` | `0.2` |
| `480x848` | `9:16 (Portrait Widescreen)` | `0.4` |
| `544x960` | `9:16 (Portrait Widescreen)` | `0.5` |
| `608x1056` | `9:16 (Portrait Widescreen)` | `0.6` |
| `640x1152` | `9:16 (Portrait Widescreen)` | `0.7` |
| `672x1216` | `9:16 (Portrait Widescreen)` | `0.8` |
| `720x1280` | `9:16 (Portrait Widescreen)` | `0.9` |
| `768x1344` | `9:16 (Portrait Widescreen)` | `0.98` |
| `640x368` | `16:9 (Widescreen)` | `0.2` |
| `848x480` | `16:9 (Widescreen)` | `0.4` |
| `960x544` | `16:9 (Widescreen)` | `0.5` |
| `1056x608` | `16:9 (Widescreen)` | `0.6` |
| `1152x640` | `16:9 (Widescreen)` | `0.7` |
| `1216x672` | `16:9 (Widescreen)` | `0.8` |
| `1280x720` | `16:9 (Widescreen)` | `0.9` |
| `1344x768` | `16:9 (Widescreen)` | `0.98` |

Semua mapping memakai `multiple=32`. Karena itu, output aktual node `ResolutionSelector` MiniMax dapat dibulatkan ke ukuran kompatibel terdekat yang lebih kecil, misalnya target UI/project `368x640` dapat menghasilkan raw output MiniMax `352x608`. Final Compose kemudian menormalkan kembali video ke ukuran `project_settings.json.video_size` menggunakan `scale + pad`.

Text encoder MiniMax H3:

- `api_template/minimax_h3_t2v_api.json` memakai node `128` (`CLIPLoader`)
- `api_template/minimax_h3_i2v_api.json` memakai node `130` (`CLIPLoader`)
- `api_template/minimax_h3_r2v_api.json` memakai node `128` (`CLIPLoader`)
- ketiga workflow memakai encoder yang sama:

```text
MINIMAX-H3/qwen3vl_32b_minimax_h3_int8_convrot.safetensors
```

- `type` loader adalah `minimax` dan `device` adalah `default`
- `minimax-h3_i2v-panjang` menggunakan template I2V yang sama pada setiap stage
- `minimax-h3_r2v-panjang` menggunakan template R2V yang sama pada setiap proses
- `minimax-h3_s2v` menggunakan workflow R2V secara in-memory sehingga memakai encoder R2V yang sama

Mapping ini berlaku untuk `minimax-h3_t2v`, `minimax-h3_i2v`, `minimax-h3_i2v-panjang`, `minimax-h3_s2v`, `minimax-h3_r2v`, dan `minimax-h3_r2v-panjang`. Nilai `width` dan `height` tetap disimpan di file prompt scene; workflow JSON meneruskannya melalui node `115` (`ResolutionSelector`) sebagai kombinasi `aspect_ratio`, `megapixels`, dan `multiple`.

Pada workflow MiniMax, expression jumlah frame selalu menggunakan FPS `24`. Formula frame mengikuti grid valid `frame_count % 17 == 5`, sehingga durasi aktual dapat sedikit lebih panjang dari durasi input. Seluruh frame tersebut merupakan bagian dari output generasi dan tidak dipotong oleh aplikasi.

Timeout runtime:

- workflow ComfyUI per call: `7200` detik
- call LLM: `600` detik
- call Gemini TTS: `600` detik
- tidak ada timeout tambahan per scene; jika satu scene mengirim beberapa workflow, setiap workflow memiliki timeout sendiri

## Logging

File logging utama:
- `logging_config.py`

Log runtime default:
- `content_creation.log`
- kegagalan HTTP saat mengirim workflow ke ComfyUI menyertakan status, URL, dan body respons server (maksimal 4000 karakter) agar error validasi node/LoRA dapat ditelusuri


## Catatan MiniMax H3 (alur prompt dan dialog)

Dokumentasi ini menjadi ringkasan aturan terbaru untuk seluruh scene MiniMax H3.

- File prompt scene yang didukung mencakup `minimax_h3_t2v_prompt.json`, `minimax_h3_i2v_prompt.json`, `minimax_h3_i2v_panjang_prompt.json`, `minimax_h3_s2v_prompt.json`, `minimax_h3_r2v_prompt.json`, dan `minimax_h3_r2v_panjang_prompt.json`.
- Referensi ringkas yang dikirim ke LLM untuk tombol `Buat Prompt` disesuaikan dengan scene: `SCENE-GENERAL.md` serta dokumen scene dan prompt khususnya. Aturan dialog bersama berasal dari `MINIMAX-H3-DIALOG.md`.
- S2V hanya boleh memakai reference aktif `<Picture 1>` dan `<Audio 1>`. R2V memakai manifest reference aktif secara dinamis, dengan batas maksimal 5 Picture, 3 Audio, dan 1 Video. R2V-Panjang memakai maksimal 4 Picture global lalu menambahkan `initial_image` Proses 1 atau frame carry sebagai Picture berikutnya sesuai proses. Token reference yang tidak aktif tidak boleh dikembalikan oleh LLM.
- Referensi `SCENE-GENERAL.md` mengikuti request `Buat Prompt`: `Context` berisi judul, tipe, target, mode, dan parameter scene yang tersedia; `Prompt`, `ADDITIONAL INSTRUCTION FROM UI`, serta manifest/gambar referensi disertakan jika tersedia. LLM menyusun prompt Inggris untuk target aktif sesuai schema respons.
- Validasi saat save dan runtime berfokus pada object prompt langsung yang valid; tidak ada translasi runtime.

### Aturan dialog MiniMax H3

Gunakan speaker stabil seperti `(S1)` dan `(S2)`, lalu tulis dialog aktual dalam format:

`<d>[Bahasa] Kalimat dialog.</d>`

Blok `<d>...</d>` dipertahankan persis saat prompt dikompilasi dan dikirim ke workflow. Tanda baca dan isi dialog mengikuti bahasa asli yang ditulis pengguna. Aturan lengkapnya ada di `api_production/AGENT-SKILLS/MINIMAX-H3-DIALOG.md`.
