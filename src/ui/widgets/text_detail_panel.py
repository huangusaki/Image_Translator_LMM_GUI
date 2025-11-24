from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QTextEdit,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, QEvent
from PyQt6.QtGui import QTextCursor
from core.processor import ProcessedBlock


class TextDetailPanel(QWidget):
    translated_text_changed_externally_signal = pyqtSignal(str, str)  # new_text, block_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_block_id = None
        self._programmatic_update = False
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        original_text_group = QGroupBox("原文（只可复制）")
        original_text_layout = QVBoxLayout(original_text_group)
        self.original_text_edit = QTextEdit()
        self.original_text_edit.setReadOnly(True)
        self.original_text_edit.setPlaceholderText("选中翻译的原始文本")
        original_text_layout.addWidget(self.original_text_edit)
        main_layout.addWidget(original_text_group)
        translated_text_group = QGroupBox("译文")
        translated_text_layout = QVBoxLayout(translated_text_group)
        self.translated_text_edit = QTextEdit()
        self.translated_text_edit.setPlaceholderText("选中翻译的翻译文本")
        self.translated_text_edit.installEventFilter(self)
        translated_text_layout.addWidget(self.translated_text_edit)
        main_layout.addWidget(translated_text_group)
        self.original_text_edit.setMinimumHeight(100)
        self.translated_text_edit.setMinimumHeight(100)
        self.original_text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.translated_text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        original_text_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        translated_text_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )

    def eventFilter(self, obj, event):
        if obj is self.translated_text_edit:
            if event.type() == QEvent.Type.FocusOut:
                if self._current_block_id is not None and not self._programmatic_update:
                    new_text = self.translated_text_edit.toPlainText()
                    self.translated_text_changed_externally_signal.emit(new_text, str(self._current_block_id))
        return super().eventFilter(obj, event)

    def update_texts(
        self,
        original_text: str | None,
        translated_text: str | None,
        block_id: str | int | None,
    ):
        self._programmatic_update = True
        current_displayed_original = self.original_text_edit.toPlainText()
        current_displayed_translated = self.translated_text_edit.toPlainText()
        new_original = original_text if original_text is not None else ""
        new_translated = translated_text if translated_text is not None else ""
        if current_displayed_original != new_original:
            self.original_text_edit.setPlainText(new_original)
        if current_displayed_translated != new_translated:
            old_cursor_pos = self.translated_text_edit.textCursor().position()
            self.translated_text_edit.setPlainText(new_translated)
        self._current_block_id = block_id
        self._programmatic_update = False

    def clear_texts(self):
        self._programmatic_update = True
        self._current_block_id = None
        self.original_text_edit.clear()
        self.translated_text_edit.clear()
        self._programmatic_update = False

    def get_current_translated_text(self) -> str:
        return self.translated_text_edit.toPlainText()

    def refresh_block_display(self, block: ProcessedBlock):
        if block:
            self.update_texts(block.original_text, block.translated_text, block.id)
        else:
            self.clear_texts()

    def select_block(self, block: ProcessedBlock | None):
        if block:
            self.update_texts(block.original_text, block.translated_text, block.id)
        else:
            self.clear_texts()

    def set_blocks(self, blocks: list[ProcessedBlock]):
        # This panel only shows one block at a time, so we don't need to store the list
        pass

    def clear_content(self):
        self.clear_texts()
