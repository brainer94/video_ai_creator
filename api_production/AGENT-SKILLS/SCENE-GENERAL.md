# Petunjuk Buat Prompt untuk scene

Gunakan informasi yang tersedia dalam request `Buat Prompt`:

- `Context` memuat `Scene title`, `Scene type`, target prompt, mode aktif, ukuran, durasi, dan reference yang tersedia.
- `Prompt`, jika disertakan, berisi prompt awal yang perlu dikembangkan.
- `ADDITIONAL INSTRUCTION FROM UI`, jika disertakan, berisi instruksi pengguna untuk target aktif.
- Manifest reference terurut dan gambar terlampir menentukan sumber serta urutan reference yang boleh digunakan.

## Aturan penyusunan

- Susun hanya prompt untuk target dan stage aktif.
- Ikuti schema dan mode aktif. Untuk MiniMax H3, hasilkan object JSON prompt langsung dalam bahasa Inggris; jangan mengembalikan wrapper bahasa.
- Gunakan durasi dari konteks tanpa membulatkan nilai desimal.
- Pertahankan token dan urutan reference aktif. Contoh dokumen tidak menambah reference yang tersedia.
- Pertahankan parameter teknis seperti ukuran dan LoRA; perubahan kreatif hanya diterapkan pada isi prompt.
- LLM hanya membuat prompt saat tombol `Buat Prompt` dipakai. Runtime aplikasi tidak menerjemahkan prompt.
