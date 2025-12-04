"""
Prompt 设置对话框
允许用户自定义 OCR 和翻译使用的 Prompt 模板。
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QMessageBox,
    QSplitter,
    QWidget,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

DEFAULT_PROMPT_TEMPLATE = """<system_role>
你是一位精通计算机视觉（Computer Vision）、OCR（光学字符识别）和多语言翻译的专家级AI助手。
你的核心能力是**像素级精度的文本定位**和**地道的语境翻译**。
你的任务是分析图像，精确定位{source_language}文本，提取内容，并将其翻译成{target_language}。
</system_role>
<instructions>
    <step index="1">
        <description>图像类型分析</description>
        <action>判断图像主要属于以下哪种类型：</action>
        <options>
            <option value="a">漫画/卡通页面（特点是分格、对话气泡、风格化的艺术）。</option>
            <option value="b">普通图像（例如，照片、文档、带有信息文本的插图、海报、应用程序截图）。</option>
        </options>
    </step>
    <step index="2">
        <description>{source_language}文本块识别与提取</description>
        <condition type="image_type_a" description="漫画/卡通页面">
            <rule>优先处理对话气泡、对话框和思想泡泡内的{source_language}文本。</rule>
            <rule>如果视觉上突出且是叙事的一部分，则提取清晰可辨的{source_language}拟声词。</rule>
            <rule>提取独特的叙事框中的{source_language}文本。</rule>
            <rule>提取不在气泡/框中但清晰属于故事叙述部分的重要、较长的{source_language}对话/叙述段落。</rule>
            <rule>通常，忽略复杂背景、微小辅助细节或装饰性元素中的{source_language}文本，除非它们是关键的叙事/拟声词。</rule>
        </condition>
        <condition type="image_type_b" description="普通图像">
            <rule>识别所有包含重要{source_language}文本的独立视觉文本块。</rule>
            <rule>忽略非常小、不清晰或孤立的、不传达重要意义的{source_language}文本片段。</rule>
        </condition>
    </step>
    <step index="3">
        <description>处理每一个识别出的{source_language}文本块</description>
        <requirements>
            <field name="original_text">
                <instruction>提取完整、准确的{source_language}文本。</instruction>
            </field>
            <field name="orientation">
                <instruction>判断其主要方向："horizontal" (水平), "vertical_ltr" (从左到右垂直), 或 "vertical_rtl" (从右到左垂直)。</instruction>
            </field>
            <field name="bounding_box">
                <importance>EXTREME</importance>
                <goal>提供一个**紧贴文本像素**的边界框。</goal>
                <format>[y_min, x_min, y_max, x_max]</format>
                <coordinate_system>0到1000之间的整数归一化坐标。(0,0)是左上角，(1000,1000)是右下角。</coordinate_system>
                <strict_constraints>
                    <constraint>1. **紧凑性 (Tightness)**: 边界框必须紧紧包裹文字本身。**严禁**包含文字周围的空白区域。</constraint>
                    <constraint>2. **排除干扰**: 严禁包含对话气泡的边框、尾巴、背景图案或邻近的物体。</constraint>
                    <constraint>3. **完整性**: 必须包含文本块中的所有字符，不能切断字符。</constraint>
                    <constraint>4. **逻辑性**: y_min < y_max 且 x_min < x_max。</constraint>
                </strict_constraints>
                <thinking_process>
                    在确定坐标时，请想象你在文本的上下左右边缘画了四条线，这四条线必须触碰到最外层字符的像素边缘。
                </thinking_process>
            </field>
            <field name="font_size_category">
                <options>very_small, small, medium, large, very_large</options>
                <criteria>根据其在图像中相对于其他文本的视觉大小。</criteria>
            </field>
            <field name="translated_text">
                <action>将提取的{source_language}文本翻译成流畅自然的{target_language}。</action>
                <context>注意视觉上下文（场景、角色表情）和对话流程/氛围，确保翻译准确反映原文的语调、情绪和细微差别。</context>
            </field>
        </requirements>
    </step>
    {glossary_section}
    <step index="4">
        <description>输出格式</description>
        <format>JSON</format>
        <structure>
            一个JSON对象列表。每个对象包含以下键：
            - "original_text": string
            - "translated_text": string
            - "orientation": string
            - "bounding_box": [int, int, int, int]
            - "font_size_category": string
        </structure>
        <example>
            [
                {{
                    "original_text": "何だ！？",
                    "translated_text": "What is it!?",
                    "orientation": "vertical_rtl",
                    "bounding_box": [100, 200, 300, 400],
                    "font_size_category": "medium"
                }}
            ]
        </example>
    </step>
    <step index="5">
        <description>异常处理</description>
        <rule>如果在图像中未找到符合条件的{source_language}文本块，则返回一个空的JSON列表：[]。</rule>
    </step>
    <step index="6">
        <description>输出约束</description>
        <rule>输出必须仅为原始JSON字符串。</rule>
        <rule>不要包含任何解释性文本、注释或markdown格式（如 ```json ... ```）。</rule>
    </step>
</instructions>
"""


class PromptSettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prompt 模板设置")
        self.config_manager = config_manager
        self.setMinimumSize(800, 600)
        self._init_ui()
        self._load_settings()
        self._connect_signals()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        info_label = QLabel(
            "自定义 Prompt 模板用于控制 LLM 如何进行 OCR 识别和翻译。\n"
            "可用变量: {source_language}, {target_language}, {glossary_section}"
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        self.use_custom_checkbox = QCheckBox("启用自定义 Prompt 模板")
        main_layout.addWidget(self.use_custom_checkbox)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        default_label = QLabel("默认模板（只读参考）:")
        left_layout.addWidget(default_label)
        self.default_prompt_edit = QTextEdit()
        self.default_prompt_edit.setReadOnly(True)
        self.default_prompt_edit.setPlainText(DEFAULT_PROMPT_TEMPLATE)
        self.default_prompt_edit.setFont(QFont("Consolas", 9))
        self.default_prompt_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
            }
        """
        )
        left_layout.addWidget(self.default_prompt_edit)
        splitter.addWidget(left_widget)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        custom_label = QLabel("自定义模板:")
        right_layout.addWidget(custom_label)
        self.custom_prompt_edit = QTextEdit()
        self.custom_prompt_edit.setPlaceholderText(
            "在此输入自定义 Prompt 模板...\n\n"
            "可用变量:\n"
            "  {source_language} - 源语言\n"
            "  {target_language} - 目标语言\n"
            "  {glossary_section} - 术语表内容"
        )
        self.custom_prompt_edit.setFont(QFont("Consolas", 9))
        self.custom_prompt_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
            }
        """
        )
        right_layout.addWidget(self.custom_prompt_edit)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter, 1)
        button_layout = QHBoxLayout()
        self.copy_default_button = QPushButton("复制默认模板到自定义")
        self.copy_default_button.setToolTip("将默认模板复制到自定义编辑区，便于修改")
        button_layout.addWidget(self.copy_default_button)
        self.reset_button = QPushButton("清空自定义模板")
        button_layout.addWidget(self.reset_button)
        button_layout.addSpacerItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def _load_settings(self):
        use_custom = self.config_manager.getboolean(
            "Prompt", "use_custom_prompt", fallback=False
        )
        self.use_custom_checkbox.setChecked(use_custom)
        custom_template = self.config_manager.get(
            "Prompt", "custom_prompt_template", fallback=""
        )
        self.custom_prompt_edit.setPlainText(custom_template)
        self._toggle_custom_edit(use_custom)

    def _save_settings(self):
        self.config_manager.set(
            "Prompt", "use_custom_prompt", str(self.use_custom_checkbox.isChecked())
        )
        self.config_manager.set(
            "Prompt", "custom_prompt_template", self.custom_prompt_edit.toPlainText()
        )
        self.config_manager.save()

    def _connect_signals(self):
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.copy_default_button.clicked.connect(self._copy_default)
        self.reset_button.clicked.connect(self._reset_custom)
        self.use_custom_checkbox.stateChanged.connect(self._on_checkbox_changed)

    def _toggle_custom_edit(self, enabled: bool):
        self.custom_prompt_edit.setEnabled(enabled)
        if not enabled:
            self.custom_prompt_edit.setStyleSheet(
                """
                QTextEdit {
                    background-color: #1a1a1a;
                    color: #888888;
                    border: 1px solid #333333;
                    border-radius: 4px;
                }
            """
            )
        else:
            self.custom_prompt_edit.setStyleSheet(
                """
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #444444;
                    border-radius: 4px;
                }
            """
            )

    def _on_checkbox_changed(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self._toggle_custom_edit(is_checked)

    def _copy_default(self):
        self.custom_prompt_edit.setPlainText(DEFAULT_PROMPT_TEMPLATE)
        if not self.use_custom_checkbox.isChecked():
            self.use_custom_checkbox.setChecked(True)

    def _reset_custom(self):
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空自定义模板吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.custom_prompt_edit.clear()

    def _on_save(self):
        if self.use_custom_checkbox.isChecked():
            template = self.custom_prompt_edit.toPlainText().strip()
            if not template:
                QMessageBox.warning(
                    self,
                    "警告",
                    "启用了自定义模板但内容为空，请填写模板内容或取消勾选。",
                )
                return
            if (
                "bounding_box" not in template.lower()
                or "translated_text" not in template.lower()
            ):
                reply = QMessageBox.warning(
                    self,
                    "警告",
                    "自定义模板中似乎缺少 'bounding_box' 或 'translated_text' 关键字。\n"
                    "这可能导致翻译结果无法正确解析。\n\n是否仍要保存？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        self._save_settings()
        self.accept()


if __name__ == "__main__":

    class DummyCM:
        def __init__(self):
            self.data = {}

        def get(self, s, o, fallback=None):
            return self.data.get(s, {}).get(o, fallback)

        def getboolean(self, s, o, fallback=False):
            val = self.get(s, o, None)
            if val is None:
                return fallback
            return str(val).lower() in ("true", "1", "yes")

        def set(self, s, o, v):
            self.data.setdefault(s, {})[o] = str(v)

        def save(self):
            print(f"Saved: {self.data}")

    app = QApplication(sys.argv)
    dialog = PromptSettingsDialog(DummyCM())
    dialog.show()
    sys.exit(app.exec())
