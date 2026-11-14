---
name: h3-prompt-writing
description: Write MiniMax H3 video generation prompts for T2VA, I2VA, FL2VA, L2VA, and Ref2VA. Use when rewriting multimodal requests into H3 prompt structures, composing integrated_multimodal_description, overall_soundscape, and non_diegetic_music, aligning keyframes, or defining reference labels for images, videos, and audio.
---

# H3 Prompt Writing

Portable to any agent that can read local files; no external API calls, MiniMax Hub tools, or proprietary runtime are required. The optional `agents/openai.yaml` only provides UI metadata.

## Workflow

1. Identify the input mode: T2VA, I2VA, FL2VA, L2VA, or full-reference Ref2VA.
2. For base text/keyframe modes, read `references/base-en.txt` and follow its final prompt structure.
3. For full-reference mode, read `references/ref-en.txt` and follow its six-section rewrite format.
4. Preserve the exact field names, section order, labels, and timing notation from the selected guide.
5. For runtime JSON, write the prompt value directly in English. Do not invent language wrappers or translation metadata.

## Base Modes

- T2VA: build the full audiovisual timeline from text.
- I2VA: start from the first frame and develop forward from it.
- FL2VA: describe the continuous path between the first and last frames.
- L2VA: infer a plausible opening and converge to the supplied last frame.

Use `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in the order shown in `references/base-en.txt`.

For T2VA, I2VA, and R2V authoring, use the shared `shots[]` item shape: `shot_id`, numeric `start`/`end`, `visual`, `action`, `camera`, `dialogue`, and `diegetic_sound`. R2V authoring uses the same `shots[]` shape and compiles it to Ref2VA `detailed_description` for runtime. `minimax-h3_r2v-panjang` keeps four R2V prompt objects in `prompts[]`; its runtime allows an optional Process 1 initial image after the global Picture references and adds the previous process last frame in that same position for processes 2–4.

## Full-Reference Mode

Ref2VA runtime rewrites use `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order. For R2V authoring, store `style_opening` and the shared `shots[]` cards instead; the application compiles them into runtime `detailed_description`. Reference labels stay consistent across all sections.

Read `references/ref-en.txt` for label rules, retention analysis, and complete examples.

## Output Rules

- Write rewrite sections in English; preserve dialogue, lyrics, and visible scene text in their original language.
- Describe each shot by composition, subjects, environment, actions, camera, sound, and the exact point where referenced content appears.
- Avoid plot summaries, unresolved reference labels, and timing that does not match the requested duration.
