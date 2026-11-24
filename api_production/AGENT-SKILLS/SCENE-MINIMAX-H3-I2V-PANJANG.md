# Scene minimax-h3_i2v-panjang

Scene ini mengatur MiniMax H3 I2V berantai dengan maksimal empat stage. Setiap stage memiliki pilihan frame awal dan frame akhir yang bersifat opsional.

## Aturan scene

- Scene memakai workflow MiniMax H3 I2VA pada setiap stage.
- `continuations` bernilai `0` sampai `3`; stage aktif adalah `continuations + 1`.
- `run_start_stage` menentukan stage pertama pada partial run.
- `stage_references` memakai dropdown `first` dan `last` dengan pilihan `(Tanpa Gambar)` atau aset gambar scene.
- Jika `first.source` Proses 1 adalah `none`, runtime memakai gambar terbaru di root scene sebagai frame awal.
- Jika `first.source` Proses 2–4 adalah `none`, runtime otomatis memakai frame terakhir proses sebelumnya.
- Jika `last.source` adalah `none`, runtime tidak mengirim frame akhir dan proses tidak memiliki target gambar akhir.
- Jika tersedia, frame awal dikirim lebih dahulu lalu frame akhir ke ComfyUI.
- Prompt setiap stage mendeskripsikan alur visual berdasarkan frame yang tersedia; instruksi temporal ditambahkan runtime.
- FPS workflow `24`; durasi scene `0.0` sampai `15.0` detik dengan maksimal empat angka desimal.

## Pembuatan prompt melalui UI

Tombol `Buat Prompt` pada salah satu stage I2V-Panjang menghasilkan prompt untuk seluruh stage aktif, mulai dari Proses 1 sampai Proses N (`N = continuations + 1`).

- Jika hanya satu instruksi pengguna yang diisi, instruksi tersebut dipakai sebagai arahan global untuk semua stage aktif.
- Jika instruksi beberapa stage diisi, setiap stage memakai instruksinya sendiri.
- Setiap stage dikirim ke LLM sebagai request terpisah. Gambar yang tersedia dapat dilampirkan sebagai konteks visual.
- Request tidak wajib memiliki dua lampiran: frame kosong tetap dipahami sebagai aturan runtime dan tidak menghambat penyusunan prompt.
- Request diproses berurutan; hasil prompt stage sebelumnya diberikan sebagai konteks kesinambungan untuk stage berikutnya.
- Hasil batch hanya disimpan setelah semua stage aktif berhasil divalidasi. Struktur JSON tetap memakai empat slot `prompts[]`.

Aturan prompt I2V-Panjang tetap memakai kontrak I2VA. Jika frame akhir dipilih, prompt perlu menjelaskan jalur visual konkret menuju kondisi gambar tersebut. Jika frame akhir tidak dipilih, prompt cukup menjelaskan alur visual yang diinginkan. Instruksi frame tidak disimpan pada prompt authoring dan ditambahkan hanya saat runtime.

Serializer runtime tetap memakai kontrak I2VA untuk setiap stage. Frame awal dan frame akhir dikirim melalui input gambar workflow; prompt tidak diberi header `How the reference pictures align with the target video`.

- prompt tetap memiliki anchor I2VA `<Picture 1>` pada awal video;
- jika frame akhir dipilih, kalimat target frame dibuat pada shot terakhir menggunakan durasi yang dipilih pengguna, misalnya `10.00` detik;
- field `reference` dan kalimat target frame hanya dibuat pada salinan payload runtime;
- penyesuaian jumlah frame internal ComfyUI tidak mengubah angka durasi yang ditulis pada prompt.

JSON authoring tetap memakai `mode: "I2VA"` dan tidak menyimpan instruksi frame, sehingga editor pengguna tetap berisi deskripsi kreatif dan shot saja.

## Struktur prompt

Root file `minimax_h3_i2v_panjang_prompt.json` tetap mempertahankan metadata dan empat slot prompt:

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
      "first": {"source": "none", "name": ""},
      "last": {"source": "scene", "name": "akhir.png"}
    }
  ]
}
```

Setiap item `prompts[]` adalah object I2VA langsung dengan schema yang sama seperti `minimax_h3_i2v_prompt.json`. `prompts` dan `stage_references` selalu berisi empat item pada file runtime. Bentuk JSON tidak berubah; nilai `source: "none"` ditafsirkan runtime sesuai nomor proses.

## Checklist

- File JSON tersedia dan valid.
- Stage aktif memiliki prompt yang valid.
- Pilihan frame awal dan frame akhir boleh `(Tanpa Gambar)`; frame awal proses lanjutan akan memakai frame carry otomatis.
- Setiap prompt stage aktif berupa object I2VA langsung dengan prompt kreatif, `shots[]`, dan audio global; `reference` serta instruksi first/last frame dibuat runtime.
- Referensi lokal benar-benar ada di folder scene.
- Referensi `stage_last` dari JSON lama tetap dapat dibaca sebagai kompatibilitas.
- Tidak ada wrapper bahasa, atau `negative_prompt`.
