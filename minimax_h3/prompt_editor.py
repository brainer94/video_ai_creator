"""Interactive MiniMax H3 prompt editor.

The editor is intentionally an adapter around the existing structured prompt
schema. It keeps the payload schema and runtime serializer as the source of
truth instead of introducing a second persisted prompt format.
"""

from __future__ import annotations

import copy

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from minimax_h3.minimax_h3_prompt import (
    REF2VA_SECTION_KEYS,
    ensure_i2va_frame_instructions,
    parse_ref2va_detailed_description,
    serialize_ref2va_detailed_description,
    validate_i2va_shot_timeline,
    validate_ref2va_prompt,
    validate_ref2va_reference_tokens,
    validate_ref2va_shot_timeline,
    validate_structured_prompt,
    unwrap_prompt_value,
)


REF2VA_SECTION_LABELS = {
    "subject_definitions": "Definisi Subjek",
    "summary": "Ringkasan",
    "retention_analysis": "Analisis Pemertahanan Referensi",
    "detailed_description": "Deskripsi Rinci",
    "overall_soundscape": "Suasana Suara Keseluruhan",
    "non_diegetic_music": "Musik Latar",
}


def _plain_text(value) -> str:
    return str(value or "")


def _safe_float(value, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return number if number == number else float(default)


class MiniMaxPromptEditorWidget(QWidget):
    """Interactive MiniMax H3 editor used directly inside a scene tab."""

    promptChanged = Signal(dict)
    valueApplied = Signal(dict)

    def __init__(
        self,
        value: dict | None,
        *,
        mode: str = "T2VA",
        duration: float = 5.0,
        include_last_frame: bool = False,
        reference_manifest: dict | None = None,
        scroll_enabled: bool = True,
        enable_ref2va_shot_cards: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.mode = str(mode or "T2VA").upper()
        self.duration = max(0.0, float(duration or 0.0))
        self.include_last_frame = bool(include_last_frame)
        self.reference_manifest = reference_manifest if isinstance(reference_manifest, dict) else None
        self.scroll_enabled = bool(scroll_enabled)
        self.enable_ref2va_shot_cards = bool(enable_ref2va_shot_cards)
        self._original_value = unwrap_prompt_value(value) if isinstance(value, dict) else {}
        self._shot_widgets: list[dict] = []
        self._result: dict | None = None
        self._building_editor = False
        self._editor_content: QWidget | None = None

        root_layout = QVBoxLayout(self)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        root_layout.addWidget(self.status_label)

        self.editor_scroll = None
        if self.scroll_enabled:
            self.editor_scroll = QScrollArea()
            self.editor_scroll.setWidgetResizable(True)
            self.editor_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.editor_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            root_layout.addWidget(self.editor_scroll, 1)
        self._set_editor_content()

    def value(self) -> dict | None:
        return copy.deepcopy(self._result)

    def current_value(self) -> dict:
        if self.mode == "REF2VA":
            return self._collect_ref2va_value()
        return self._collect_base_value()

    def set_prompt_value(
        self,
        value: dict | None,
        *,
        mode: str | None = None,
        duration: float | None = None,
        include_last_frame: bool | None = None,
        reference_manifest: dict | None = None,
        enable_ref2va_shot_cards: bool | None = None,
    ):
        if mode is not None:
            self.mode = str(mode or "T2VA").upper()
        if duration is not None:
            self.duration = max(0.0, float(duration or 0.0))
        if include_last_frame is not None:
            self.include_last_frame = bool(include_last_frame)
        if reference_manifest is not None or self.mode == "REF2VA":
            self.reference_manifest = (
                reference_manifest if isinstance(reference_manifest, dict) else None
            )
        if enable_ref2va_shot_cards is not None:
            self.enable_ref2va_shot_cards = bool(enable_ref2va_shot_cards)
        self._original_value = copy.deepcopy(value) if isinstance(value, dict) else {}
        self._result = None
        self._shot_widgets = []
        self._set_editor_content()

    def _set_editor_content(self):
        self._building_editor = True
        editor_content = (
            self._build_ref2va_editor()
            if self.mode == "REF2VA"
            else self._build_base_editor()
        )
        editor_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        editor_content.setMinimumWidth(0)
        if self.editor_scroll is not None:
            previous = self.editor_scroll.takeWidget()
            if previous is not None:
                previous.deleteLater()
            self.editor_scroll.setWidget(editor_content)
        else:
            if self._editor_content is not None:
                self.layout().removeWidget(self._editor_content)
                self._editor_content.deleteLater()
            self._editor_content = editor_content
            self.layout().addWidget(editor_content, 1)
        self._building_editor = False

    def _connect_live_change(self, widget):
        signal = getattr(widget, "textChanged", None)
        if signal is None:
            signal = getattr(widget, "valueChanged", None)
        if signal is not None:
            signal.connect(self._emit_live_change)

    def _emit_live_change(self, *_args):
        if self._building_editor:
            return
        self.promptChanged.emit(copy.deepcopy(self.current_value()))

    def _build_base_editor(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        if self.mode == "I2VA":
            if self.include_last_frame:
                message = (
                    "I2VA dengan frame awal dan frame akhir aktif. "
                    "Editor akan mempertahankan Picture 1 di awal dan Picture 2 di akhir."
                )
            else:
                message = (
                    "I2VA dimulai dari Picture 1 pada 0,00 detik. "
                    "Kalimat teknis frame awal dibuat otomatis saat diterapkan."
                )
            self.status_label.setText(message)
        else:
            self.status_label.setText(
                "Susun linimasa melalui kartu bidikan. Kolom bantuan akan dikompilasi ke "
                "struktur shots yang sudah dipakai MiniMax H3."
            )

        toolbar = QHBoxLayout()
        add_button = QPushButton("Tambah")
        add_button.setToolTip("Tambah bidikan")
        add_button.clicked.connect(lambda: self._add_shot())
        toolbar.addWidget(add_button)
        normalize_button = QToolButton()
        normalize_button.setText("Akhir = durasi")
        normalize_button.setToolTip("Atur waktu selesai bidikan terakhir ke durasi acuan")
        normalize_button.setFixedWidth(120)
        normalize_button.clicked.connect(self._align_last_shot_end)
        toolbar.addWidget(normalize_button)
        toolbar.addStretch(1)
        toolbar.addWidget(QLabel(f"Durasi: {self.duration:.2f} dtk"))
        layout.addLayout(toolbar)

        shots_container = QWidget()
        self.shots_layout = QVBoxLayout(shots_container)
        self.shots_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(shots_container)

        audio_box = QGroupBox("Suara Keseluruhan")
        audio_form = QFormLayout(audio_box)
        self.overall_soundscape_input = QPlainTextEdit(
            _plain_text(self._original_value.get("overall_soundscape"))
        )
        self.overall_soundscape_input.setPlaceholderText(
            "Suasana lingkungan, suara aksi fisik, dan suara manusia non-verbal selama video."
        )
        self.overall_soundscape_input.setFixedHeight(78)
        self.non_diegetic_music_input = QPlainTextEdit(
            _plain_text(self._original_value.get("non_diegetic_music"))
        )
        self.non_diegetic_music_input.setPlaceholderText(
            "Musik latar yang hanya didengar penonton, atau N/A."
        )
        self.non_diegetic_music_input.setFixedHeight(78)
        self._connect_live_change(self.overall_soundscape_input)
        self._connect_live_change(self.non_diegetic_music_input)
        audio_form.addRow("Suasana Suara Keseluruhan", self.overall_soundscape_input)
        audio_form.addRow("Musik Latar", self.non_diegetic_music_input)
        layout.addWidget(audio_box)

        shots = self._original_value.get("shots")
        if not isinstance(shots, list) or not shots:
            shots = [{
                "shot_id": "Shot 1",
                "start": 0.0,
                "end": self.duration or 5.0,
                "visual": "",
                "action": "",
                "camera": "",
                "dialogue": "",
                "diegetic_sound": "",
            }]
        for shot in shots:
            self._add_shot(shot if isinstance(shot, dict) else {})
        return container

    def _build_ref2va_editor(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        status = (
            "Ref2VA memakai enam bagian tetap. Gunakan scrollbar di dalam editor untuk "
            "melihat semua bagian. Semua bagian ditulis dalam bahasa Inggris; dialog, "
            "lirik, dan teks yang terlihat tetap memakai bahasa aslinya."
        )

        manifest_box = QGroupBox("Daftar Referensi Aktif")
        manifest_layout = QVBoxLayout(manifest_box)
        labels = []
        manifest = self.reference_manifest or {}
        for index, _name in enumerate(manifest.get("images", []) or [], start=1):
            labels.append(f"<Picture {index}>")
        for index, _name in enumerate(manifest.get("audios", []) or [], start=1):
            labels.append(f"<Audio {index}>")
        if manifest.get("video"):
            labels.append("<Video 1>")
        manifest_layout.addWidget(QLabel(
            "Label referensi mengikuti urutan posisi alur kerja, bukan urutan abjad nama file: "
            + (", ".join(labels) if labels else "belum ada referensi")
        ))
        layout.addWidget(manifest_box)

        section_container = QWidget()
        section_layout = QVBoxLayout(section_container)
        self._ref2va_inputs: dict[str, QPlainTextEdit] = {}
        heights = {
            "subject_definitions": 140,
            "summary": 100,
            "retention_analysis": 150,
            "detailed_description": 330,
            "overall_soundscape": 100,
            "non_diegetic_music": 100,
        }
        hints = {
            "subject_definitions": "Satu baris untuk setiap Subject, Picture, Video, atau Audio yang perlu dilacak.",
            "summary": "Awalan jenis tugas, misalnya [reference generation + audio reference].",
            "retention_analysis": "Satu baris untuk setiap label dengan penanda hubungan referensi/copy yang sesuai.",
            "detailed_description": "Pembuka gaya visual lalu uraian [Shot N] dalam urutan pemutaran.",
            "overall_soundscape": "Suasana lingkungan dan suara fisik sepanjang video.",
            "non_diegetic_music": "Musik yang hanya didengar penonton, atau N/A.",
        }
        for key in REF2VA_SECTION_KEYS:
            box = QGroupBox(REF2VA_SECTION_LABELS.get(key, key))
            box_layout = QVBoxLayout(box)
            box_layout.addWidget(QLabel(hints[key]))
            if key == "detailed_description" and self.enable_ref2va_shot_cards:
                box_layout.addWidget(QLabel("Pembuka gaya visual (ditulis sebelum Shot 1)."))
                self.ref2va_style_input = QPlainTextEdit()
                self.ref2va_style_input.setPlainText("")
                self.ref2va_style_input.setFixedHeight(72)
                self._connect_live_change(self.ref2va_style_input)
                box_layout.addWidget(self.ref2va_style_input)

                toolbar = QHBoxLayout()
                add_button = QPushButton("Tambah Bidikan")
                add_button.setToolTip("Tambah bidikan ke timeline Ref2VA")
                add_button.clicked.connect(lambda: self._add_shot())
                toolbar.addWidget(add_button)
                normalize_button = QToolButton()
                normalize_button.setText("Akhir = durasi")
                normalize_button.setToolTip("Atur waktu selesai bidikan terakhir ke durasi acuan")
                normalize_button.setFixedWidth(120)
                normalize_button.clicked.connect(self._align_last_shot_end)
                toolbar.addWidget(normalize_button)
                toolbar.addStretch(1)
                toolbar.addWidget(QLabel(f"Durasi: {self.duration:.2f} dtk"))
                box_layout.addLayout(toolbar)

                shots_container = QWidget()
                self.shots_layout = QVBoxLayout(shots_container)
                self.shots_layout.setAlignment(Qt.AlignTop)
                box_layout.addWidget(shots_container)

                if isinstance(self._original_value.get("shots"), list):
                    parsed = {
                        "style_opening": self._original_value.get("style_opening", ""),
                        "shots": self._original_value.get("shots", []),
                        "has_markers": True,
                    }
                else:
                    parsed = parse_ref2va_detailed_description(
                        self._original_value.get(key), self.duration
                    )
                self.ref2va_style_input.setPlainText(parsed.get("style_opening", ""))
                for shot in parsed.get("shots", []) or []:
                    self._add_shot(shot if isinstance(shot, dict) else {})
                if self._original_value.get(key) and not parsed.get("has_markers"):
                    status += (
                        " Prompt R2V lama tidak memiliki marker [Shot N]; isinya dipertahankan "
                        "sebagai satu bidikan dan akan diberi marker saat disimpan."
                    )
            else:
                editor = QPlainTextEdit(_plain_text(self._original_value.get(key)))
                editor.setMinimumHeight(heights[key])
                self._connect_live_change(editor)
                box_layout.addWidget(editor)
                self._ref2va_inputs[key] = editor
            section_layout.addWidget(box)
        section_layout.addStretch(1)
        layout.addWidget(section_container)
        self.status_label.setText(status)
        return container

    def _add_shot(self, shot: dict | None = None):
        shot = copy.deepcopy(shot) if isinstance(shot, dict) else {}
        index = len(self._shot_widgets) + 1
        box = QGroupBox(f"Bidikan {index}")
        box_layout = QVBoxLayout(box)

        top_row = QHBoxLayout()
        start_input = QDoubleSpinBox()
        start_input.setRange(0.0, 9999.0)
        start_input.setDecimals(3)
        start_input.setSingleStep(0.5)
        start_input.setValue(_safe_float(shot.get("start", 0.0), 0.0))
        start_input.setFixedWidth(96)
        end_input = QDoubleSpinBox()
        end_input.setRange(0.0, 9999.0)
        end_input.setDecimals(3)
        end_input.setSingleStep(0.5)
        end_input.setValue(_safe_float(shot.get("end", self.duration or 5.0), self.duration or 5.0))
        end_input.setFixedWidth(96)
        self._connect_live_change(start_input)
        self._connect_live_change(end_input)
        top_row.addWidget(QLabel("Mulai"))
        top_row.addWidget(start_input)
        top_row.addWidget(QLabel("Selesai"))
        top_row.addWidget(end_input)
        top_row.addStretch(1)
        remove_button = QToolButton()
        remove_button.setText("Hapus")
        remove_button.setToolTip("Hapus bidikan ini")
        remove_button.clicked.connect(lambda: self._remove_shot(box))
        top_row.addWidget(remove_button)
        box_layout.addLayout(top_row)

        form = QFormLayout()
        visual_input = QPlainTextEdit(_plain_text(shot.get("visual")))
        visual_input.setPlaceholderText(
            "Gaya, komposisi, subjek, pakaian, posisi, lingkungan, pencahayaan, properti, dan teks terlihat."
        )
        visual_input.setFixedHeight(100)
        action_input = QPlainTextEdit(_plain_text(shot.get("action")))
        action_input.setPlaceholderText("Aksi, reaksi, perubahan pose, dan perubahan keadaan objek.")
        action_input.setFixedHeight(76)
        camera_input = QPlainTextEdit(_plain_text(shot.get("camera")))
        camera_input.setPlaceholderText("Pembingkaian, posisi kamera, gerakan, amplitudo, dan kecepatan.")
        camera_input.setFixedHeight(68)
        dialogue_input = QPlainTextEdit(_plain_text(shot.get("dialogue")))
        dialogue_input.setPlaceholderText(
            "Contoh: Wanita (S1) berkata: <d>[Indonesia] ...</d>"
        )
        dialogue_input.setFixedHeight(68)
        sound_input = QPlainTextEdit(_plain_text(shot.get("diegetic_sound")))
        sound_input.setPlaceholderText("Suara yang benar-benar terjadi di dalam adegan.")
        sound_input.setFixedHeight(68)
        for input_widget in (
            visual_input,
            action_input,
            camera_input,
            dialogue_input,
            sound_input,
        ):
            self._connect_live_change(input_widget)
        form.addRow("Gambaran Visual", visual_input)
        form.addRow("Aksi", action_input)
        form.addRow("Kamera", camera_input)
        form.addRow("Dialog / Lirik", dialogue_input)
        form.addRow("Suara dalam Adegan", sound_input)
        box_layout.addLayout(form)

        self.shots_layout.addWidget(box)
        self._shot_widgets.append({
            "box": box,
            "original": shot,
            "start": start_input,
            "end": end_input,
            "visual": visual_input,
            "action": action_input,
            "camera": camera_input,
            "dialogue": dialogue_input,
            "diegetic_sound": sound_input,
        })
        self._renumber_shots()
        if not self._building_editor:
            self._emit_live_change()

    def _remove_shot(self, box: QWidget):
        if len(self._shot_widgets) <= 1:
            QMessageBox.information(self, "Bidikan wajib", "Minimal harus ada satu bidikan.")
            return
        for index, item in enumerate(self._shot_widgets):
            if item["box"] is box:
                self._shot_widgets.pop(index)
                box.deleteLater()
                break
        self._renumber_shots()
        self._emit_live_change()

    def _renumber_shots(self):
        for index, item in enumerate(self._shot_widgets, start=1):
            item["box"].setTitle(f"Bidikan {index}")

    def _align_last_shot_end(self):
        if self._shot_widgets:
            self._shot_widgets[-1]["end"].setValue(self.duration)

    def _collect_base_value(self) -> dict:
        result = copy.deepcopy(self._original_value)
        result["mode"] = self.mode
        result["shots"] = []
        for index, item in enumerate(self._shot_widgets, start=1):
            shot = copy.deepcopy(item["original"])
            shot.update({
                "shot_id": f"Shot {index}",
                "start": float(item["start"].value()),
                "end": float(item["end"].value()),
                "visual": item["visual"].toPlainText().strip(),
                "action": item["action"].toPlainText().strip(),
                "camera": item["camera"].toPlainText().strip(),
                "dialogue": item["dialogue"].toPlainText().strip(),
                "diegetic_sound": item["diegetic_sound"].toPlainText().strip(),
            })
            result["shots"].append(shot)
        result["overall_soundscape"] = self.overall_soundscape_input.toPlainText().strip()
        result["non_diegetic_music"] = self.non_diegetic_music_input.toPlainText().strip()
        if self.mode == "I2VA":
            result["reference"] = {
                "picture": "Picture 1",
                "source": "[Shot 1]",
                "time": 0.0,
                "instruction": "fully referenced",
            }
            result = ensure_i2va_frame_instructions(
                result,
                self.duration,
                include_last_frame=self.include_last_frame,
            )
        return result

    def _collect_shot_cards(self) -> list[dict]:
        shots = []
        for index, item in enumerate(self._shot_widgets, start=1):
            shot = copy.deepcopy(item["original"])
            shot.update({
                "shot_id": f"Shot {index}",
                "start": float(item["start"].value()),
                "end": float(item["end"].value()),
                "visual": item["visual"].toPlainText().strip(),
                "action": item["action"].toPlainText().strip(),
                "camera": item["camera"].toPlainText().strip(),
                "dialogue": item["dialogue"].toPlainText().strip(),
                "diegetic_sound": item["diegetic_sound"].toPlainText().strip(),
            })
            shots.append(shot)
        return shots

    def _collect_ref2va_value(self) -> dict:
        result = copy.deepcopy(self._original_value)
        for key, editor in self._ref2va_inputs.items():
            result[key] = editor.toPlainText().strip()
        if self.enable_ref2va_shot_cards:
            result["mode"] = "R2VA"
            result["style_opening"] = self.ref2va_style_input.toPlainText().strip()
            result["shots"] = self._collect_shot_cards()
            result.pop("detailed_description", None)
        return result

    def apply(self) -> bool:
        if self.mode == "REF2VA":
            result = self._collect_ref2va_value()
            errors = []
            if self.enable_ref2va_shot_cards:
                errors.extend(self._validate_ref2va_shot_cards())
                errors.extend(validate_ref2va_shot_timeline(
                    serialize_ref2va_detailed_description(
                        result.get("style_opening", ""), result.get("shots", [])
                    ),
                    self.duration,
                ))
            errors.extend(validate_ref2va_prompt(result))
            if not errors:
                errors = self._validate_ref2va_references(result)
        else:
            result = self._collect_base_value()
            errors = validate_structured_prompt(result, expected_mode=self.mode)
            if self.mode == "I2VA":
                errors.extend(validate_i2va_shot_timeline(result, self.duration))
        if errors:
            QMessageBox.warning(
                self,
                "Prompt belum valid",
                "Periksa bagian berikut:\n\n- " + "\n- ".join(dict.fromkeys(errors[:10])),
            )
            return False
        self._result = result
        self.promptChanged.emit(copy.deepcopy(result))
        self.valueApplied.emit(copy.deepcopy(result))
        return True

    def _validate_ref2va_shot_cards(self) -> list[str]:
        errors = []
        for index, item in enumerate(self._shot_widgets, start=1):
            fields = (
                item["visual"].toPlainText(),
                item["action"].toPlainText(),
                item["camera"].toPlainText(),
                item["dialogue"].toPlainText(),
                item["diegetic_sound"].toPlainText(),
            )
            if not any(str(value or "").strip() for value in fields):
                errors.append(f"Bidikan {index} harus memiliki isi.")
            if float(item["end"].value()) <= float(item["start"].value()):
                errors.append(f"Waktu selesai Bidikan {index} harus lebih besar dari waktu mulai.")
            if index > 1 and float(item["start"].value()) <= float(self._shot_widgets[index - 2]["start"].value()):
                errors.append(f"Waktu mulai Bidikan {index} harus lebih besar dari bidikan sebelumnya.")
        if self._shot_widgets and abs(float(self._shot_widgets[0]["start"].value())) > 0.0001:
            errors.append("Bidikan 1 Ref2VA harus dimulai pada 0,00 detik.")
        return errors

    def _accept(self):
        return self.apply()

    def _validate_ref2va_references(self, value: dict) -> list[str]:
        if self.reference_manifest is None:
            return []
        images = self.reference_manifest.get("images", []) or []
        audios = self.reference_manifest.get("audios", []) or []
        has_video = bool(self.reference_manifest.get("video"))
        return validate_ref2va_reference_tokens(
            value,
            image_count=len(images),
            audio_count=len(audios),
            has_video=has_video,
        )


class MiniMaxPromptEditorDialog(QDialog):
    """Compatibility wrapper for callers that still want a modal editor."""

    def __init__(self, value: dict | None, *, parent=None, **editor_options):
        super().__init__(parent)
        mode = str(editor_options.get("mode", "T2VA") or "T2VA").upper()
        self.setWindowTitle(f"Editor Prompt MiniMax H3 — {mode}")
        self.setModal(True)
        self.resize(980, 760)

        layout = QVBoxLayout(self)
        self.editor = MiniMaxPromptEditorWidget(
            value,
            parent=self,
            **editor_options,
        )
        layout.addWidget(self.editor, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Terapkan")
        button_box.button(QDialogButtonBox.Cancel).setText("Batal")
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def value(self) -> dict | None:
        return self.editor.value()

    def _accept(self):
        if self.editor.apply():
            self.accept()
