# Scene minimax-h3_i2v-panjang

Scene ini mengatur MiniMax H3 I2V berantai dengan maksimal empat stage. Setiap stage aktif wajib memiliki first frame dan last frame.

## Aturan scene

- Scene memakai workflow MiniMax H3 I2VA pada setiap stage.
- `continuations` bernilai `0` sampai `3`; stage aktif adalah `continuations + 1`.
- `run_start_stage` menentukan stage pertama pada partial run.
- Setiap stage aktif wajib memilih `first` dan `last` pada `stage_references`; `source: "none"` atau referensi kosong tidak valid.
- Stage 1 tidak boleh memakai `stage_last` karena belum ada stage sebelumnya.
- Frame pertama dan terakhir dikirim ke ComfyUI dalam urutan tersebut.
- Prompt setiap stage mendeskripsikan transisi kontinu dari first frame menuju last frame.
- FPS workflow `24`; durasi scene `0.0) sampai `15.0) detik dengan maksimal empat angka desimal.

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
      "first": {"source": "scene", "name": "awal.png"},
      "last": {"source": "scene", "name": "akhir.png"}
    }
  ]
}
```

Setiap item `prompts[]` adalah object I2VA langsung dengan schema yang sama seperti `minimax_h3_i2v_prompt.json`. `prompts` dan `stage_references` selalu berisi empat item pada file runtime; validasi hanya memblokir stage aktif yang belum memiliki dua frame.

## Checklist

- File JSON tersedia dan valid.
- Stage aktif memiliki first frame dan last frame.
- Setiap prompt stage aktif berupa object I2VA langsung dengan `reference`, `shots[]`, dan audio global.
- Referensi lokal benar-benar ada di folder scene.
- Referensi `stage_last` menunjuk stage sebelumnya yang valid.
- Tidak ada wrapper bahasa, `source: "none"`, atau `negative_prompt`.
