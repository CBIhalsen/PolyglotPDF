python包在2.2版本之前预计不会更新，2.2版本预估采取解析最底层span获取更信息的布局逻辑解决，预估解决：行内公式错误判断为公式块，错误将粗体文本进行分段bug,以及insert_html方法重复嵌入字体文件导致处理页数较大pdf时浪费计算资源极其卡顿。 目前效果，对于基于文本的pdf,polyglotpdf的解析方式依旧是最优解。 ocr和布局分析并不总是完美。（考虑处理文本上下标问题，大部分pdf文件中上标下标文本通过指定坐标和字体大小实现伪上下标，考虑替换为真正的上下标文字对应的Unicode编码，但并不完美），对于报告型表格文档，polyglotpdf效果相当完美，当然表格中的复杂矢量数学公式依旧无法正确处理）。
寻求意见的改进方法，对于复杂的颜色布局文本或者粗体参杂常规字体文本，提出以下方法，对于流内容我们可以解析为html格式如下：

    <p style="color: red; display: inline;">ABSTRACT: </p>
    <p style="display: inline;">
        The swine industry annually suffers significant economic losses caused by porcine reproductive and respiratory syndrome virus (PRRSV). Because the available commercial vaccines have limited protective efficacy against epidemic PRRSV, there is an urgent need for innovative solutions. Nanoparticle vaccines induce robust immune responses and have become a promising direction in vaccine development. In this study, we designed and produced a self-assembling nanoparticle vaccine derived from thermophilic archaeal ferritin to combat epidemic PRRSV. First, multiple T cell epitopes targeting viral structural proteins were identified by IFN-γ screening after PRRSV infection. Three different self-assembled nanoparticles with epitopes targeting viral GP3, GP4, and GP5.
    </p>

  这种解析内容只能由llms翻译，翻译结果如下：
  ```html
<p style="color: red; display: inline;">摘要：</p>
<p style="display: inline;">
    猪产业每年因猪繁殖与呼吸综合征病毒（PRRSV）造成显著的经济损失。由于现有的商业疫苗对流行性PRRSV的保护效果有限，迫切需要创新的解决方案。纳米粒子疫苗能够引发强烈的免疫反应，已成为疫苗开发的一个有前景的方向。在本研究中，我们设计并生产了一种源自嗜热古细菌铁蛋白的自组装纳米粒子疫苗，以对抗流行性PRRSV。首先，通过PRRSV感染后的IFN-γ筛选，识别出针对病毒结构蛋白的多个T细胞表位。三种不同的自组装纳米粒子携带针对病毒GP3、GP4和GP5的表位。
</p>
```
甚至包括粗体：
  ```html
<p style="color: blue; font-weight: bold; display: inline;">摘要：</p>
<p style="display: inline;">
    猪产业每年因猪繁殖与呼吸综合征病毒（PRRSV）造成显著的经济损失。由于现有的商业疫苗对流行性PRRSV的保护效果有限，迫切需要创新的解决方案。纳米粒子疫苗能够引发强烈的免疫反应，已成为疫苗开发的一个有前景的方向。在本研究中，我们设计并生产了一种源自嗜热古细菌铁蛋白的自组装纳米粒子疫苗，以对抗流行性PRRSV。首先，通过PRRSV感染后的IFN-γ筛选，识别出针对病毒结构蛋白的多个T细胞表位。三种不同的自组装纳米粒子携带针对病毒GP3、GP4和GP5的表位。
</p>
```
这种方法会无线接近于完美的处理，目前考虑将此方法作为强化功能选用

English | [简体中文](/README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JA.md) | [한국어](README_KO.md)
# PolyglotPDF

[![Python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![PDF](https://img.shields.io/badge/pdf-documentation-brightgreen.svg)](https://example.com)
[![LaTeX](https://img.shields.io/badge/latex-typesetting-orange.svg)](https://www.latex-project.org/)
[![Translation](https://img.shields.io/badge/translation-supported-yellow.svg)](https://example.com)
[![Math](https://img.shields.io/badge/math-formulas-red.svg)](https://example.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24.0-blue.svg)](https://pymupdf.readthedocs.io/)


## Demo
<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true" width="80%" height="40%">

### [🎬 Watch Full Video](https://github.com/CBIhalsen/PolyglotPDF/blob/main/demo.mp4)
 llms has been added as the translation api of choice, Doubao ,Qwen ,deepseek v3 , gpt4-o-mini are recommended. The color space error can be resolved by filling the white areas in PDF files. The old text to text translation api has been removed.

In addition, consider adding arxiv search function and rendering arxiv papers after latex translation.

### Pages show
<div style="display: flex; margin-bottom: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page1.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page2.jpeg?raw=true" width="40%" height="20%">
</div>
<div style="display: flex;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page3.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page4.png?raw=true" width="40%" height="20%">
</div>


# LLM API Application

## 302.AI
AI service aggregation platform supporting multiple international mainstream AI models:
- Official Website: [302.AI](https://302.ai)
- Registration: [Sign up with invitation link](https://share.302.ai/JBmCb1) (Use invitation code `JBmCb1` to get $1 bonus)
- Available Models: GPT-4o, GPT-4o-mini, Claude-3.7-Sonnet, DeepSeek-V3 and more
- Features: Access multiple AI models with one account, pay-per-use pricing

## Doubao & Deepseek
Apply through Volcengine platform:
- Application URL: [Volcengine-Doubao](https://www.volcengine.com/product/doubao/)
- Available Models: Doubao, Deepseek series models

## Tongyi Qwen
Apply through Alibaba Cloud platform:
- Application URL: [Alibaba Cloud-Tongyi Qwen](https://cn.aliyun.com/product/tongyi?from_alibabacloud=&utm_content=se_1019997984)
- Available Models: Qwen-Max, Qwen-Plus series models


## Overview
PolyglotPDF is an advanced PDF processing tool that employs specialized techniques for ultra-fast text, table, and formula recognition in PDF documents, typically completing processing within 1 second. It features OCR capabilities and layout-preserving translation, with full document translations usually completed within 10 seconds (speed may vary depending on the translation API provider).


## Features
- **Ultra-Fast Recognition**: Processes text, tables, and formulas in PDFs within ~1 second
- **Layout-Preserving Translation**: Maintains original document formatting while translating content
- **OCR Support**: Handles scanned documents efficiently
- **Text-based PDF**：No GPU required
- **Quick Translation**: Complete PDF translation in approximately 10 seconds
- **Flexible API Integration**: Compatible with various translation service providers
- **Web-based Comparison Interface**: Side-by-side comparison of original and translated documents
- **Enhanced OCR Capabilities**: Improved accuracy in text recognition and processing
- **Support for offline translation**: Use smaller translation model

## Installation and Usage

<details>
  <summary>Standard Installation</summary>

1. Clone the repository:
```bash
git clone https://github.com/CBIhalsen/PolyglotPDF.git
cd polyglotpdf
```

2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Configure your API key in config.json. The alicloud translation API is not recommended.

4. Run the application:
```bash
python app.py
```

5. Access the web interface:
Open your browser and navigate to `http://127.0.0.1:8000`
</details>

<details>
  <summary>Docker Installation</summary>

## Quick Start Without Persistence

If you want to quickly test PolyglotPDF without setting up persistent directories:

```bash
# Pull the image first
docker pull 2207397265/polyglotpdf:latest

# Run container without mounting volumes (data will be lost when container is removed)
docker run -d -p 12226:12226 --name polyglotpdf 2207397265/polyglotpdf:latest
```

This is the fastest way to try PolyglotPDF, but all uploaded PDFs and configuration changes will be lost when the container stops.

## Installation with Persistent Storage

```bash
# Create necessary directories
mkdir -p config fonts static/original static/target static/merged_pdf

# Create config file
nano config/config.json    # or use any text editor
# Copy configuration template from the project into this file
# Make sure to fill in your API keys and other configuration details

# Set permissions
chmod -R 755 config fonts static
```

### Quick Start

Use the following commands to pull and run the PolyglotPDF Docker image:

```bash
# Pull image
docker pull 2207397265/polyglotpdf:latest

# Run container
docker run -d -p 12226:12226 --name polyglotpdf \
  -v ./config/config.json:/app/config.json \
  -v ./fonts:/app/fonts \
  -v ./static/original:/app/static/original \
  -v ./static/target:/app/static/target \
  -v ./static/merged_pdf:/app/static/merged_pdf \
  2207397265/polyglotpdf:latest
```

### Access the Application

After the container starts, open in your browser:
```
http://localhost:12226
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  polyglotpdf:
    image: 2207397265/polyglotpdf:latest
    ports:
      - "12226:12226"
    volumes:
      - ./config.json:/app/config.json # Configuration file
      - ./fonts:/app/fonts # Font files
      - ./static/original:/app/static/original # Original PDFs
      - ./static/target:/app/static/target # Translated PDFs
      - ./static/merged_pdf:/app/static/merged_pdf # Merged PDFs
    restart: unless-stopped
```

Then run:

```bash
docker-compose up -d
```

### Common Docker Commands

```bash
# Stop container
docker stop polyglotpdf

# Restart container
docker restart polyglotpdf

# View logs
docker logs polyglotpdf
```
</details>

## Requirements
- Python 3.8+
- deepl==1.17.0
- Flask==2.0.1
- Flask-Cors==5.0.0
- langdetect==1.0.9
- Pillow==10.2.0
- PyMuPDF==1.24.0
- pytesseract==0.3.10
- requests==2.31.0
- tiktoken==0.6.0
- Werkzeug==2.0.1

## Acknowledgments
This project leverages PyMuPDF's capabilities for efficient PDF processing and layout preservation.

## Upcoming Improvements
- PDF chat functionality
- Academic PDF search integration
- Optimization for even faster processing speeds

### Known Issues
- **Issue Description**: Error during text re-editing: `code=4: only Gray, RGB, and CMYK colorspaces supported`
- **Symptom**: Unsupported color space encountered during text block editing
- **Current Workaround**: Skip text blocks with unsupported color spaces
- **Proposed Solution**: Switch to OCR mode for entire pages containing unsupported color spaces
- **Example**: [View PDF sample with unsupported color spaces](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/colorspace_issue_sample.pdf)

### TODO
- □ **Custom Terminology Database**: Support custom terminology databases with prompts for domain-specific professional translation
- □ **AI Reflow Feature**: Convert double-column PDFs to single-column HTML blog format for easier reading on mobile devices
- □ **Multi-format Export**: Export translation results to PDF, HTML, Markdown and other formats
- □ **Multi-device Synchronization**: Read translations on mobile after processing on desktop
- □ **Enhanced Merge Logic**: Improve the current merge logic by disabling font name detection and enabling horizontal, vertical, x, y range overlap merging

### Font Optimization
Current font configuration in the `start` function of `main.py`:
```python
# Current configuration
css=f"* {{font-family:{get_font_by_language(self.target_language)};font-size:auto;color: #111111 ;font-weight:normal;}}"
```

You can optimize font display through the following methods:

1. **Modify Default Font Configuration**
```python
# Custom font styles
css=f"""* {{
    font-family: {get_font_by_language(self.target_language)};
    font-size: auto;
    color: #111111;
    font-weight: normal;
    letter-spacing: 0.5px;  # Adjust letter spacing
    line-height: 1.5;      # Adjust line height
}}"""
```

2. **Embed Custom Fonts**
You can embed custom fonts by following these steps:
- Place font files (.ttf, .otf) in the project's `fonts` directory
- Use `@font-face` to declare custom fonts in CSS
```python
css=f"""
@font-face {{
    font-family: 'CustomFont';
    src: url('fonts/your-font.ttf') format('truetype');
}}
* {{
    font-family: 'CustomFont', {get_font_by_language(self.target_language)};
    font-size: auto;
    font-weight: normal;
}}
"""
```

### Basic Principles
This project follows similar basic principles as Adobe Acrobat DC's PDF editing, using PyMuPDF for text block recognition and manipulation:

- **Core Process**:
```python
# Get text blocks from the page
blocks = page.get_text("dict")["blocks"]

# Process each text block
for block in blocks:
    if block.get("type") == 0:  # text block
        bbox = block["bbox"]     # get text block boundary
        text = ""
        font_info = None
        # Collect text and font information
        for line in block["lines"]:
            for span in line["spans"]:
                text += span["text"] + " "
```
This approach directly processes PDF text blocks, maintaining the original layout while achieving efficient text extraction and modification.

- **Technical Choices**:
  - Utilizes PyMuPDF for PDF parsing and editing
  - Focuses on text processing
  - Avoids complex operations like AI formula recognition, table processing, or page restructuring

- **Why Avoid Complex Processing**:
  - AI recognition of formulas, tables, and PDF restructuring faces severe performance bottlenecks
  - Complex AI processing leads to high computational costs
  - Significantly increased processing time (potentially tens of seconds or more)
  - Difficult to deploy at scale with low costs in production environments
  - Not suitable for online services requiring quick response times

- **Project Scope**:
  - This project only serves to demonstrate the correct approach for layout-preserved PDF translation and AI-assisted PDF reading. Converting PDF files to markdown format for large language models to read, in my opinion, is not a wise approach.
  - Aims for optimal performance-to-cost ratio

- **Performance**:
  - PolyglotPDF API response time: ~1 second per page
  - Low computational resource requirements, suitable for scale deployment
  - High cost-effectiveness for commercial applications

- * Contact author:
QQ： 1421243966
email: 1421243966@qq.com

Related questions answered and discussed：

 QQ group:
 1031477425

