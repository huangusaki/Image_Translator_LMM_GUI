# Image Translator

<p align="center">
  <a href="#chinese-version">中文</a> | <a href="#english-version">English</a>
</p>

<a name="chinese-version"></a>

## 安装与运行

1.  **环境要求**: Python 3.10 或更高版本。
2.  **获取代码**: 下载并解压本项目代码。
3.  **安装依赖**:
    在项目根目录（包含 `requirements.txt` 的文件夹）下打开终端，运行：
    ```bash
    pip install -r requirements.txt
    ```
4.  **启动程序**:
    ```bash
    python src/main.py
    ```
5.  **配置说明**:
    *   首次运行需在设置菜单中配置 API。
    *   推荐使用 **Gemini** 作为 OCR 和翻译服务。
    *   **API Key 获取**: [Google AI Studio](https://aistudio.google.com/)
    *   **代理设置**: 如无法直接连接 Google 服务，请在设置中配置 HTTP 代理 (例如 `http://127.0.0.1:7890`)。

## 功能简介

*   **OCR 与翻译**: 集成 Gemini 模型，支持图片文字识别与翻译。
*   **可视化编辑**:
    *   支持选中、移动、缩放和旋转文本块。
    *   可调整字体、颜色、描边、背景色及行间距等样式。
*   **批量处理**: 支持批量导入图片进行翻译并导出结果。
*   **本地化**: 支持自定义术语表，固定特定词汇的翻译。

<details>
<summary><strong>效果展示 (点击展开)</strong></summary>

![示例图片 4](sample/4.png)
![示例图片 3](sample/3.png)
![示例图片 2](sample/2.png)
![示例图片 1](sample/1.png)
</details>

---

<a name="english-version"></a>
<details>
<summary>English Version</summary>

<br>

## Installation & Usage

1.  **Prerequisites**: Python 3.10 or higher.
2.  **Install Dependencies**:
    Run the following command in the project root directory:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run Application**:
    ```bash
    python src/main.py
    ```
4.  **Configuration**:
    *   Configure API keys in the settings menu upon first launch.
    *   **Gemini** is recommended for both OCR and translation.
    *   **Get API Key**: [Google AI Studio](https://aistudio.google.com/)
    *   **Proxy**: Configure HTTP proxy settings if required.

## Features

*   **OCR & Translation**: Uses Gemini model for text recognition and translation.
*   **Visual Editor**:
    *   Select, move, resize, and rotate text blocks.
    *   Customize font styles, colors, outlines, and spacing.
*   **Batch Processing**: Translate multiple images and export results.
*   **Customization**: Supports custom glossaries for consistent translation.

<details>
<summary><strong>Sample Images (Click to expand)</strong></summary>

![Sample Image 4](sample/4.png)
![Sample Image 3](sample/3.png)
![Sample Image 2](sample/2.png)
![Sample Image 1](sample/1.png)
</details>

</details>
