---
name: minimax-h3-s2v-prompt
description: Menulis prompt MiniMax H3 S2V dalam mode Ref2VA dengan satu Picture dan satu Audio aktif.
---

# MiniMax H3 S2V Prompt

Gunakan mode full-reference `Ref2VA` untuk scene S2V. Prompt disimpan langsung dalam bahasa Inggris pada `positive_prompt` dan diserialisasi menjadi enam section berikut:

```text
subject_definitions
summary
retention_analysis
detailed_description
overall_soundscape
non_diegetic_music
```

## Struktur JSON

```json
{
  "positive_prompt": {
    "subject_definitions": "...",
    "summary": "...",
    "retention_analysis": "...",
    "detailed_description": "...",
    "overall_soundscape": "...",
    "non_diegetic_music": "N/A"
  }
}
```

Jangan menambahkan `mode`, `shots`, `reference`, `negative_prompt`, wrapper bahasa, atau field baru lain ke object Ref2VA S2V.

## Reference yang aktif

Workflow S2V hanya memiliki `<Picture 1>` sebagai gambar awal dan `<Audio 1>` sebagai audio reference. Jangan memakai `<Picture 2>`, `<Picture 3>`, `<Video 1>`, atau `<Audio 2>`/`<Audio 3>`. Token semantic seperti `<Subject 1>`, `<Shot 1>`, `<d>`, `</d>`, dan speaker ID tetap boleh digunakan.

## Cara menulis field

- `subject_definitions`: identitas subjek pada `<Picture 1>` dan hubungan dengan `<Audio 1>`.
- `summary`: tujuan adegan, alur aksi, serta fungsi gambar dan audio.
- `retention_analysis`: detail visual dan karakteristik audio yang dipertahankan.
- `detailed_description`: timeline visual lengkap dari awal sampai akhir, termasuk aksi, kamera, dialog, suara, dan reference.
- `overall_soundscape`: ambience, suara fisik, suara manusia, dan penggunaan `<Audio 1>`.
- `non_diegetic_music`: musik latar atau `N/A`.

Beberapa shot untuk S2V tetap ditulis sebagai marker `[Shot N]` di dalam `detailed_description`; S2V tidak memakai array `shots[]`.

Tombol `Buat Prompt` boleh memakai LLM untuk menghasilkan object Inggris. Runtime tidak menerjemahkan prompt dan tidak membuat salinan bahasa lain.
