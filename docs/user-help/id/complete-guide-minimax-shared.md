# Panduan Bersama Penulisan Prompt MiniMax H3

Panduan ini berisi aturan yang digunakan bersama oleh mode T2VA, I2VA, dan FL2VA. Gunakan panduan khusus mode untuk aturan alignment gambar atau alur keyframe yang hanya berlaku pada mode tertentu.

## Bahasa dan bentuk prompt

Penjelasan dalam panduan ini menggunakan bahasa Indonesia agar mudah dipahami. Namun, prompt akhir yang dikirim ke model MiniMax H3 harus menggunakan bahasa Inggris, kecuali:

- dialog atau lirik yang memang diberikan dalam bahasa lain;
- teks yang terlihat di dalam adegan;
- nama atau istilah khusus yang harus dipertahankan.

Nama field dan token berikut harus dipertahankan persis:

- `integrated_multimodal_description`;
- `overall_soundscape`;
- `non_diegetic_music`;
- `[Shot N]`;
- `<Picture N>`;
- `<d>...</d>`;
- `<scenetrans>` dan `<cutoff>`.

Pada Video AI Creator, isi prompt dapat disusun melalui editor interaktif. Struktur akhirnya tetap mengikuti kontrak prompt MiniMax H3.

## Tiga bagian utama prompt

Prompt akhir memiliki tiga bagian berikut dan harus ditulis dalam urutan yang sama.

### `integrated_multimodal_description`

Bagian ini merupakan alur utama video dari awal hingga akhir. Isinya dapat mencakup:

- gaya visual;
- komposisi awal;
- penampilan dan posisi subjek;
- lingkungan dan properti penting;
- aksi dan perubahan keadaan;
- perpindahan shot atau cut;
- gerakan kamera;
- dialog, singing, atau voiceover;
- suara diegetik yang terjadi di dalam adegan.

Setiap detail harus berhubungan dengan sesuatu yang terlihat atau terdengar di video. Hindari membuat ringkasan cerita yang terlalu umum.

Awali `[Shot 1]` dengan gaya visual dan komposisi awal. Contoh gaya yang dapat digunakan adalah `Cinematic`, `live-action`, `2D-animated`, `3D CG`, `claymation`, `watercolor`, atau `vintage film`.

```text
[Shot 1] Live-action, cinematic, a medium-wide shot frames a baker opening the shutters of a small street bakery before sunrise.
```

### `overall_soundscape`

Bagian ini merangkum ambience, suara lingkungan, suara gerakan fisik, dan suara manusia non-verbal sepanjang video.

Gunakan satu sampai empat kalimat bahasa Inggris dalam satu paragraf. Jangan mengulang dialog, singing, atau musik diegetik yang sudah dijelaskan di bagian shot.

Contoh:

```text
overall_soundscape: Steady rain taps against the café windows while low room ambience continues underneath. The entrance bell rings once, followed by wet footsteps and the soft scrape of a chair.
```

Gunakan `N/A` hanya jika pengguna memang meminta seluruh video tanpa suara.

### `non_diegetic_music`

Bagian ini menjelaskan musik latar yang hanya didengar penonton dan tidak didengar oleh karakter di dalam adegan.

Gunakan satu sampai tiga kalimat bahasa Inggris. Jelaskan instrumen, tempo, ritme, dan perubahan dinamika. Hindari hanya menuliskan kata yang abstrak seperti “sedih” atau “menegangkan” tanpa menjelaskan karakter musiknya.

Contoh:

```text
non_diegetic_music: Sparse piano notes at a slow tempo, joined by sustained low strings that gradually increase in volume before fading out.
```

Gunakan `N/A` jika tidak ada musik non-diegetik.

## Shot dan timeline

Gunakan rentang waktu yang jelas untuk setiap shot. Shot pertama selalu dimulai pada `0.00` detik. Shot berikutnya dimulai tepat ketika shot sebelumnya berakhir.

```text
[Shot 1] From 0.00 to 3.50 seconds, the opening composition develops...
[Shot 2] From 3.50 to 5.00 seconds, the camera cuts to...
```

Aturan timeline:

1. Shot tidak boleh saling tumpang tindih.
2. Waktu mulai shot pertama adalah `0.00`.
3. Waktu mulai shot berikutnya sama dengan waktu akhir shot sebelumnya.
4. Shot terakhir harus berakhir pada durasi video yang ditentukan.
5. Setiap shot harus menambahkan informasi visual, perubahan keadaan, perpindahan sudut pandang, atau perkembangan waktu.

Untuk cut biasa, gunakan kalimat natural seperti:

- `the camera cuts to`;
- `the shot cuts to`;
- `the shot transitions to`;
- `the shot changes to`;
- `the shot switches to`.

Gunakan cross-dissolve, fade, atau wipe hanya jika memang diminta. Jika perubahan hanya berupa jarak atau sedikit perubahan sudut, lebih baik gunakan gerakan kamera daripada membuat cut baru.

## Gerakan kamera

Gerakan kamera sebaiknya ditulis sebagai bagian natural dari kalimat shot. Jangan menumpuk label gerakan kamera di akhir prompt tanpa menjelaskan objek atau arah yang diikuti.

| Jenis | Istilah prompt | Makna |
|---|---|---|
| Gerakan lensa | `Zoom In` / `Zoom Out` | Focal length berubah sementara posisi kamera tetap |
| Gerakan maju-mundur | `Push In` / `Pull Out` | Kamera bergerak mendekat atau menjauh |
| Putaran horizontal | `Pan Left` / `Pan Right` | Kamera tetap di tempat dan lensa berputar ke kiri atau kanan |
| Perpindahan horizontal | `Truck Left` / `Truck Right` | Seluruh kamera berpindah ke kiri atau kanan |
| Putaran vertikal | `Tilt Up` / `Tilt Down` | Lensa mengarah ke atas atau ke bawah |
| Perpindahan vertikal | `Pedestal Up` / `Pedestal Down` | Seluruh kamera bergerak naik atau turun |
| Gerak melingkar | `Arc Shot` | Kamera bergerak membentuk busur mengelilingi subjek |
| Mengikuti subjek | `Tracking Shot` | Kamera mengikuti subjek yang bergerak |
| Diam | `Static Shot` | Posisi kamera dan lensa tetap |
| Guncangan | `Shake Slightly` / `Shake Strongly` | Guncangan ringan atau kuat |
| Sudut pandang | `POV` | Kamera memakai sudut pandang subjek |
| Rotasi sumbu lensa | `Roll Clockwise` / `Roll Counterclockwise` | Kamera berputar searah atau berlawanan arah jarum jam |

Amplitude dan kecepatan dapat ditambahkan bila diperlukan:

- `with small amplitude` — perubahan dalam rentang kecil;
- `with large amplitude` — perubahan dalam rentang besar;
- `at slow speed` — gerakan lambat;
- `at fast speed` — gerakan cepat.

Amplitude sedang dan kecepatan normal biasanya tidak perlu ditulis.

Contoh:

```text
The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.
The camera pans right with large amplitude at fast speed, revealing the open doorway.
The camera holds a static shot as the runner exits the frame.
```

## Speaker, dialog, dan singing

Gunakan ID speaker yang stabil seperti `(S1)` dan `(S2)`. Speaker yang sama harus memakai ID yang sama pada seluruh shot. Subjek yang tidak pernah mengeluarkan suara tidak perlu diberi ID speaker.

Saat speaker pertama kali muncul, jelaskan identitas visual dan karakter suaranya secukupnya, misalnya usia, gender, posisi on-screen atau off-screen, pitch, timbre, kecepatan bicara, atau aksen.

Di dalam `<d>`, masukkan hanya tag bahasa dan isi dialog atau lirik yang sebenarnya diucapkan. Pertahankan setiap kata dan tanda baca yang diberikan pengguna tanpa menerjemahkan atau menulis ulang.

```text
The young woman with a quiet, breathy voice (S1) says: <d>[English] I get off at the next station.</d>
The two children (S1,S2) shout together, <d>[English] Wait for us!</d>
```

Untuk voiceover, gunakan frasa persis `says in an off-screen voiceover`. Setelah setiap blok voiceover, jelaskan bahwa karakter on-screen tidak menggerakkan bibir.

```text
The man (S1) says in an off-screen voiceover: <d>[English] I still remember that road.</d> while his lips remain completely closed.
```

Jika satu dialog atau lirik melewati cut, gunakan `<scenetrans>` pada titik sambungan di kedua bagian dan jelaskan bahwa audio terus berlanjut. Gunakan `<cutoff>` jika ucapan terpotong karena video berakhir.

Contoh penjelasan continuity:

- `continues seamlessly across the cut`;
- `continues uninterrupted into the next shot`;
- `carries over from the previous shot`;
- `remains audible across the transition`.

## Teks yang terlihat di layar

Banner, papan nama, label, subtitle, atau teks neon yang benar-benar terlihat di layar harus ditulis dalam tanda kutip ganda bahasa Inggris. Pertahankan isi dan tanda bacanya persis seperti yang diminta.

```text
A red neon sign reading "营业中" glows above the doorway.
```

Jangan mengubah teks layar menjadi ringkasan seperti “terdapat tulisan dalam bahasa asing”.

## Checklist bersama

Sebelum prompt digunakan, periksa hal berikut:

- urutan tiga bagian utama sudah benar;
- `[Shot 1]` dimulai dari `0.00` detik;
- rentang waktu setiap shot berurutan dan tidak tumpang tindih;
- gaya visual dan komposisi awal sudah dijelaskan;
- aksi, reaksi, kamera, dan suara ditempatkan pada shot yang tepat;
- ID speaker stabil dan tidak berganti di tengah video;
- dialog dan lirik berada di dalam `<d>`;
- teks yang terlihat di layar dipertahankan apa adanya;
- `overall_soundscape` tidak mengulang dialog;
- `non_diegetic_music` hanya membahas musik yang tidak didengar karakter;
- prompt akhir tetap berbahasa Inggris sesuai kontrak MiniMax H3.
