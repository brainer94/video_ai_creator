# Panduan Lengkap MiniMax H3 R2V

## Fungsi R2V

R2V (`Reference-to-Video-Audio`) membuat video dengan bantuan reference image, video, dan audio. Reference tidak hanya menjadi inspirasi umum, tetapi dapat dipakai untuk mempertahankan identitas subjek, lingkungan, gaya, gerakan, struktur video, atau karakter suara tertentu.

Mode ini memakai format prompt Ref2VA (`Reference-to-Video-Audio`). Prompt perlu menjelaskan hubungan antara reference dan video target dengan konsisten dari awal hingga akhir.

Gunakan [Panduan Bersama Penulisan Prompt MiniMax H3](complete-guide-minimax-shared.md) untuk aturan shot, timeline, kamera, dialog, suara, dan musik.

## Format di Video AI Creator dan format runtime

Video AI Creator menggunakan dua tingkat format:

1. **Format penyusunan di editor** — pengguna menyusun `style_opening`, empat section reference, dan kartu `shots[]` melalui editor interaktif.
2. **Format runtime** — aplikasi menggabungkan `style_opening` dan kartu shot menjadi `detailed_description`, lalu mengirim enam section Ref2VA dalam urutan yang diperlukan oleh MiniMax H3.

Enam section runtime adalah:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

Pada format authoring, bagian `detailed_description` disusun melalui `style_opening` dan `shots[]`. Isi adegan tidak perlu ditulis ulang hanya karena formatnya dikompilasi oleh aplikasi.

Reference aktif disimpan sebagai manifest scene. Untuk scene R2V biasa, aplikasi mendukung maksimal lima gambar, tiga audio, dan satu video, serta membutuhkan minimal satu reference aktif.

## Bahasa dan token tetap

Penjelasan panduan ini menggunakan bahasa Indonesia. Prompt akhir yang dikirim ke MiniMax H3 tetap harus berbahasa Inggris, kecuali dialog, lirik, atau teks yang memang harus dipertahankan dalam bahasa aslinya.

Nama section, field, dan token berikut harus dipertahankan persis:

- `subject_definitions`;
- `summary`;
- `retention_analysis`;
- `detailed_description`;
- `overall_soundscape`;
- `non_diegetic_music`;
- `<Subject N>`;
- `<Picture N>`;
- `<Video N>`;
- `<Audio N>`;
- `[Shot N]`;
- `<d>...</d>`;
- `<scenetrans>` dan `<cutoff>`.

Jangan membuat wrapper bahasa, key `id_new`, `id_old`, atau `en`. Runtime tidak menerjemahkan prompt; isi bahasa Inggris yang sudah disusun dikirim apa adanya.

## Reference aktif dan penomoran label

Gunakan hanya reference yang benar-benar tersedia pada manifest scene. Nomor label harus rapat dan mengikuti urutan reference aktif:

- gambar mengikuti urutan `references.images` dan menjadi `<Picture 1>`, `<Picture 2>`, dan seterusnya;
- audio mengikuti urutan `references.audios` dan menjadi `<Audio 1>`, `<Audio 2>`, dan seterusnya;
- video menjadi `<Video 1>` bila tersedia.

> Urutan token mengikuti urutan pilihan reference, bukan urutan abjad nama file.

Pertahankan label yang sama di `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, dan bagian audio. Jangan membuat label baru, mengganti nama label, melompati nomor, atau memakai label media yang tidak aktif.

### Jenis label

#### `<Subject N>`

`<Subject N>` mewakili isi visual yang benar-benar digunakan pada video target, bukan sekadar nama file reference. Contohnya:

- orang, hewan, atau objek;
- lingkungan dan latar;
- pakaian, properti, antarmuka, atau efek visual;
- gaya, aksi, ekspresi, atau pose.

Satu subject dapat dibentuk dari beberapa reference. Sebaliknya, satu reference dapat memberikan beberapa subject.

```text
<Subject 1> is the young woman in <Picture 1>, with long dark hair, a blue cardigan, and a thin silver necklace.
```

Jika satu subject berasal dari beberapa media, gabungkan sumbernya dan jelaskan peran setiap media.

```text
<Subject 1> is the woman whose appearance comes from <Picture 1> and whose walking motion comes from <Video 1>.
```

#### `<Picture N>`

Gunakan `<Picture N>` sebagai label mandiri ketika gambar berfungsi sebagai frame awal, keyframe, frame akhir, atau anchor komposisi tertentu.

```text
<Picture 2> is the first frame of [Shot 1], showing a woman seated beside a café window.
```

Jika gambar hanya digunakan untuk menentukan karakter, lingkungan, pakaian, atau gaya, masukkan sumbernya ke definisi `<Subject N>` tanpa membuat entri Picture terpisah.

Jika gambar berfungsi sebagai storyboard atau referensi perencanaan shot, jelaskan shot yang dipengaruhinya.

```text
<Picture 3> is a storyboard reference for [Shot 1] and [Shot 2], defining their viewpoint, subject placement, and shot order.
```

#### `<Video N>`

Gunakan `<Video N>` untuk hubungan yang berkaitan dengan keseluruhan video, misalnya:

- mengedit video sumber;
- melanjutkan video dari bagian akhirnya;
- mengikuti gerakan kamera, cut, ritme, atau struktur waktu video sumber.

```text
<Video 1> is the source video for the target video edit.
```

Jika orang, objek, lingkungan, aksi, atau efek dari video reference digunakan sebagai isi visual, masukkan isi tersebut ke `<Subject N>`. `<Video N>` menunjukkan asset atau struktur sumber dan tidak menggantikan subject.

#### `<Audio N>`

`<Audio N>` dapat digunakan untuk:

- menyalin seluruh atau sebagian sinyal audio;
- menjadikan musik sebagai reference gaya;
- menjadikan audio sebagai reference timbre dan cara bicara;
- menggunakan dialog, lirik, atau sound effect dari audio sumber;
- mengikuti beat, ritme, atau kesinambungan audio.

Jika audio reference secara jelas terkait dengan speaker tertentu, gunakan speaker ID yang sama dengan speaker target.

```text
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).
```

## `subject_definitions`

Section ini mendefinisikan setiap isi reference yang perlu dilacak pada section berikutnya. Setiap item sebaiknya memiliki baris sendiri dan menjelaskan:

- label reference;
- isi yang diwakili;
- peran reference pada video target;
- ciri utama yang harus dipertahankan;
- nama asset bila asalnya perlu dibuat jelas.

`retention_analysis` kemudian menjelaskan di mana item tersebut muncul dan seberapa jauh cirinya dipertahankan, dipindahkan, atau hanya dijadikan reference.

Jangan membuat entri Picture atau Video terpisah jika media tersebut hanya dipakai untuk mendefinisikan subject lain dan tidak akan dianalisis sebagai reference mandiri.

Contoh:

```text
subject_definitions:
<Subject 1> is the coffee-shop environment in <Picture 1>, featuring an exposed brick wall, an orange tufted sofa with patterned pillows, a neon sign, and a wooden coffee table.
<Subject 2> is the fluffy white Samoyed in <Picture 2>, <Picture 3>, and <Picture 4>, with thick white fur, pointed ears, a dark nose, and a curved tail.
<Subject 3> is the young blonde woman in <Video 1>, with long blonde hair and a light-pink button-down shirt with rolled-up sleeves.
<Subject 4> is the young man in <Video 2>, with short wavy brown hair and a dark-grey hoodie with drawstrings.
<Audio 1> is the voice-timbre reference for <Subject 3> (S1), containing a spoken English vocal layer.
```

## `summary`

Section ini merangkum video target dan hubungan reference dalam satu paragraf pendek berbahasa Inggris. Awali dengan prefix jenis tugas di dalam tanda kurung siku.

Jenis tugas yang tersedia:

| Prefix | Kapan digunakan |
|---|---|
| `[keyframe completion]` | Gambar menjadi frame pertama, keyframe, frame terakhir, atau anchor frame tertentu |
| `[reference generation]` | Reference memberi panduan karakter, gaya, scene, aksi, kamera, atau storyboard tanpa menjadi frame konkret |
| `[video editing]` | Video sumber diedit secara langsung |
| `[video continuation]` | Video baru melanjutkan atau memperpanjang video sumber |
| `[audio reuse]` | Sinyal audio yang sama digunakan kembali sebagian atau seluruhnya |
| `[audio reference]` | Audio hanya menjadi reference timbre, ritme, gaya musik, isi dialog, atau tekstur suara |

Jika beberapa hubungan berlaku sekaligus, gabungkan dengan ` + ` tanpa mengulang jenis tugas. Contohnya:

```text
[video continuation + keyframe completion] ...
```

Kehadiran video atau audio tidak otomatis berarti video diedit atau audio disalin. Gunakan `video editing` atau `video continuation` hanya jika memang itu peran video tersebut. Gunakan `audio reuse` jika sinyal audio benar-benar digunakan kembali.

Gunakan label yang sudah didefinisikan pada `subject_definitions`. Jangan memperkenalkan label reference baru di `summary`.

Untuk pekerjaan editing video, summary dapat dimulai dengan kalimat berikut setelah prefix:

```text
The target video is an edited version of <Video 1>.
```

Contoh:

```text
summary:
[reference generation + audio reference] The target video shows <Subject 3> eating a cookie in <Subject 1>. <Subject 4> enters with <Subject 2>, which lunges toward the cookie. The three-shot exchange uses <Audio 1> as the voice-timbre reference for <Subject 3> and ends with a canned audience laugh.
```

## `retention_analysis`

Section ini menjelaskan bagaimana setiap reference dipertahankan, disalin, dipindahkan, atau hanya dijadikan panduan pada video target. Gunakan satu baris untuk setiap label reference dan pertahankan makna yang sudah didefinisikan pada `subject_definitions`.

### Relationship marker untuk visual

Gunakan marker berikut untuk `<Subject N>`, `<Picture N>`, dan `<Video N>`:

| Marker | Makna |
|---|---|
| `fully_preserved` | Peran dan ciri yang didefinisikan dipertahankan sepenuhnya |
| `partially_preserved` | Reference tetap digunakan, tetapi sebagian ciri berubah atau hanya dipertahankan sebagian |
| `attribute_transfer` | Ciri reference dipindahkan ke subject target lain yang dapat dikenali |
| `weak_reference` | Hanya kemiripan umum pada gaya, kategori, komposisi, atau suasana yang dipertahankan |

Contoh subject:

```text
<Subject 1> (appears in [Shot 1], [Shot 3]): fully_preserved - the exposed brick wall, orange tufted sofa, patterned pillows, neon sign, and wooden coffee table are retained.
```

Contoh Picture:

```text
<Picture 2> ([Shot 1] first frame): fully_preserved - the seated pose, camera angle, and café-window composition are retained at the beginning of the shot.
```

Contoh struktur video:

```text
<Video 1> (cut and pacing structure): weak_reference - the target follows the source video's alternating close-up rhythm without copying its exact content.
```

### Relationship marker untuk audio

Gunakan marker berikut untuk `<Audio N>`:

| Marker | Makna |
|---|---|
| `fully_copy` | Audio sumber lengkap menjadi track audio final lengkap |
| `partially_copy` | Hanya sebagian timeline atau layer audio yang disalin, atau ada suara lain yang ditambahkan, dihapus, atau diganti |
| `reference` | Sinyal tidak disalin; hanya timbre, ritme, gaya musik, isi dialog, atau tekstur suara yang dijadikan panduan |
| `weak_reference` | Hanya kemiripan umum pada kategori atau suasana yang dipertahankan |

Contoh:

```text
<Audio 1>: fully_copy - <Audio 1> is reused 1:1 as the target video's complete final audio track.
```

```text
<Audio 2>: reference - the target speaker follows <Audio 2>'s voice timbre and measured delivery without copying the original signal.
```

Pilih marker berdasarkan peran reference yang sudah didefinisikan. Aksi, latar, atau kejadian baru pada video target tidak otomatis berarti reference kehilangan fidelity.

## `detailed_description` dan kartu shot

`detailed_description` adalah badan utama prompt runtime. Isinya menjelaskan visual, aksi, suara, dialog, dan penggunaan reference berdasarkan urutan playback video.

Di Video AI Creator, isi ini disusun melalui `style_opening` dan kartu `shots[]`:

- `style_opening` menjelaskan gaya visual global sebelum `[Shot 1]`;
- setiap kartu shot memiliki waktu mulai dan akhir;
- setiap kartu menjelaskan visual, action, camera, dialogue, dan diegetic sound;
- aplikasi menggabungkan kartu tersebut menjadi `detailed_description`.

### Pembukaan gaya

Untuk R2V, tulis satu atau dua kalimat bahasa Inggris sebelum `[Shot 1]` untuk menetapkan gaya visual, pencahayaan, warna, dan karakter visual global.

```text
The target video uses a realistic multi-camera sitcom style with warm indoor lighting.
[Shot 1] The scene opens in a crowded urban street...
```

### Format shot

Gunakan format rentang waktu eksplisit:

```text
[Shot 1] From 0.00 to 3.00 seconds, ...
[Shot 2] From 3.00 to 5.00 seconds, ...
```

Gunakan label reference ketika subject atau media pertama kali muncul, lalu gunakan label yang sama pada shot berikutnya tanpa mendefinisikan ulang identitasnya.

Gunakan phrasing natural untuk frame konkret:

```text
the shot begins from <Picture 1>
the shot's keyframe corresponds to <Picture 2>
the shot ends on <Picture 3>
```

Jika video sumber diedit atau dilanjutkan, gunakan `<Video N>` di bagian yang memang menerapkan hubungan editing atau continuation. Gunakan `<Audio N>` pada shot atau fase audio ketika hubungan audio tersebut aktif.

### Detail yang perlu ada dalam shot

Setiap shot sebaiknya menjelaskan sebanyak yang diperlukan tentang:

- komposisi dan posisi subjek;
- ciri subjek yang berasal dari reference;
- lingkungan, pencahayaan, dan properti;
- aksi dan perubahan keadaan;
- gerakan atau posisi kamera;
- dialog, singing, atau voiceover;
- suara diegetik dan penggunaan audio reference.

Untuk tugas generation, detailed description biasanya membutuhkan sekitar 350 sampai 500 kata bahasa Inggris bila kompleksitas adegan memungkinkan. Angka tersebut bukan target mekanis; dialog yang padat harus tetap memprioritaskan seluruh timeline ucapan. Untuk editing video, panjang deskripsi mengikuti kompleksitas video sumber.

Panduan gerakan kamera, speaker, dialog, dan suara yang lebih lengkap tersedia pada [panduan bersama](complete-guide-minimax-shared.md).

## Speaker, audio reference, dan dialog

Aturan speaker ID dan format dialog mengikuti panduan bersama. Dalam R2V, reference visual dan speaker dapat digunakan bersama:

```text
<Subject 2> (S1) turns toward the woman and says, <d>[English] Last summer, I went to my grandfather's house. He talked about you.</d>
```

`<Subject N>` menunjukkan subject yang berasal dari reference, sedangkan `(Sx)` menunjukkan speaker aktual pada video target.

Jika subject berbicara, gunakan bentuk `<Subject N> (Sx)`. Jika subject yang sama berbicara dari luar layar, gunakan label yang sama dan tambahkan keterangan `off-screen`. Jika speaker tidak berhubungan dengan subject yang telah didefinisikan, jelaskan karakter suara lalu gunakan speaker ID.

Jika `<Audio N>` hanya menjadi reference timbre, ritme, emosi, atau delivery, jangan menyalin dialog dari audio tersebut. Jika pengguna meminta dialog atau lirik audio disalin atau digunakan kembali, pertahankan kata-kata dan bahasa sumber di dalam `<d>`.

Jika audio langsung digunakan sebagai musik latar atau soundtrack dan tidak ada orang, karakter, narrator, atau sumber vokal mandiri yang menghasilkan suara tersebut, gunakan `<Audio N>` tanpa membuat speaker ID baru. Jika ada sumber vokal konkret, gunakan `(Sx)` yang stabil.

Jangan menulis speaker ID baru hanya karena terjadi pergantian shot. Jangan menulis dialog lengkap pada `overall_soundscape` atau `non_diegetic_music`.

## `overall_soundscape` dan `non_diegetic_music`

`overall_soundscape` merangkum ambience dan suara fisik sepanjang video. Dialog, singing, dan sound event yang terikat pada shot tertentu tetap berada di `detailed_description`.

```text
overall_soundscape: Quiet indoor room tone and a low ventilation hum continue throughout the video.
```

`non_diegetic_music` hanya membahas musik yang didengar penonton dan tidak didengar karakter.

```text
non_diegetic_music: A restrained solo-piano score at a slow tempo, with sustained low cello underneath and no swell.
```

Jika audio reference menyediakan ambience, sound effect, dan musik sekaligus, jelaskan hubungan copy atau reference pada section yang sesuai.

## Contoh lengkap R2V

Contoh berikut menggunakan prompt akhir berbahasa Inggris karena kontrak runtime MiniMax H3 memang menggunakan bahasa Inggris.

```text
subject_definitions:
<Subject 1> is the coffee-shop environment in <Picture 1>, featuring an exposed brick wall, an orange tufted sofa with patterned pillows, a neon sign, and a wooden coffee table.
<Subject 2> is the fluffy white Samoyed in <Picture 2>, <Picture 3>, and <Picture 4>, with thick white fur, pointed ears, a dark nose, and a curved tail.
<Subject 3> is the young blonde woman in <Video 1>, with long blonde hair and a light-pink button-down shirt with rolled-up sleeves.
<Subject 4> is the young man in <Video 2>, with short wavy brown hair and a dark-grey hoodie with drawstrings.
<Audio 1> is the voice-timbre reference for <Subject 3> (S1), containing a spoken English vocal layer.

summary:
[reference generation + audio reference] The target video shows <Subject 3> eating a cookie in <Subject 1>. <Subject 4> enters with <Subject 2>, which lunges toward the cookie. The three-shot exchange uses <Audio 1> as the voice-timbre reference for <Subject 3> and ends with a canned audience laugh.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2], [Shot 3]): fully_preserved - the exposed brick wall, orange tufted sofa, patterned pillows, neon sign, and wooden coffee table are retained.
<Subject 2> (appears in [Shot 1], [Shot 2]): fully_preserved - the Samoyed's thick white fur, pointed ears, dark nose, and curved tail are retained.
<Subject 3> (appears in [Shot 1], [Shot 2], [Shot 3]): fully_preserved - the blonde woman's identity, long hair, and light-pink shirt are retained.
<Subject 4> (appears in [Shot 1], [Shot 2]): fully_preserved - the young man's short wavy brown hair and dark-grey hoodie are retained.
<Audio 1>: reference - its vocal timbre guides the dialogue delivery of <Subject 3> without copying the original signal.

detailed_description:
The target video uses a realistic multi-camera sitcom style with warm indoor lighting.
[Shot 1] A medium shot establishes <Subject 1>, the coffee shop with its exposed brick wall, orange tufted sofa, patterned pillows, neon sign, and wooden coffee table. <Subject 3> (S1), the young woman with long blonde hair and a light-pink button-down shirt with rolled-up sleeves, sits on the sofa holding a chocolate-chip cookie. From the left, <Subject 4>, the young man with short wavy brown hair and a dark-grey hoodie with drawstrings, enters holding the leash of <Subject 2>, the thick-furred white Samoyed with pointed ears, a dark nose, and a curved tail. The dog lunges toward the cookie and pulls the leash taut. <Subject 3> (S1) jerks her hand back and, using the clear youthful voice timbre referenced from <Audio 1>, exclaims with light annoyance, <d>[English] Hey! Watch your dog!</d> She closes her lips and guards the cookie while <Subject 4> pulls the dog back.
[Shot 2] From 3.00 to 5.00 seconds, the shot cuts to a close-up of <Subject 4> (S2), the young man in the dark-grey hoodie from Shot 1, sitting beside <Subject 3> on the sofa and holding <Subject 2> securely in his arms. <Subject 4> (S2) says in a casual young male voice with a playful tone and an easy conversational pace, <d>[English] He just likes cookies more than me.</d> He closes his mouth into an apologetic smile and strokes the dog's thick white fur.
[Shot 3] From 5.00 to 7.00 seconds, the shot cuts to a close-up of <Subject 3> (S1), the blonde woman in the light-pink shirt from Shot 1. Her annoyance softens as she looks toward the Samoyed. <Subject 3> (S1) replies in the same clear youthful voice referenced from <Audio 1> with an amused cadence, <d>[English] Well, he has good taste at least.</d> She smiles and raises the cookie in a small toast-like gesture. A classic canned audience laugh begins immediately after the line and continues through the final frame.

overall_soundscape:
Soft indoor coffee-shop room tone continues throughout the scene.

non_diegetic_music:
N/A
```

## Checklist R2V

- Minimal satu reference aktif tersedia.
- Urutan reference mengikuti manifest dan nomor token rapat.
- Semua label reference sama di seluruh section.
- `subject_definitions` menjelaskan peran dan ciri reference.
- `summary` memakai prefix task type yang sesuai.
- `retention_analysis` memakai relationship marker yang tepat.
- `style_opening` menetapkan gaya visual sebelum shot pertama.
- Semua shot memiliki timeline dan menjelaskan visual, aksi, kamera, dialog, serta suara yang relevan.
- Dialog dan lirik hanya berada di dalam `<d>` pada shot yang sesuai.
- `overall_soundscape` tidak mengulang dialog.
- `non_diegetic_music` hanya menjelaskan musik yang tidak didengar karakter.
- Tidak ada token media yang tidak tersedia.
- Tidak ada key `id_new`, `id_old`, atau `en`.
- Prompt akhir berbahasa Inggris sesuai kontrak MiniMax H3.
