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
## 概述
PolyglotPDF 是一款先进的 PDF 处理工具，采用特殊技术实现对 PDF 文档中的文字、表格和公式的超快速识别，通常仅需 1 秒即可完成处理。它支持 OCR 功能和完美保留版面的翻译功能，整篇文档的翻译通常可在 10 秒内完成（具体速度取决于翻译 API 服务商）。

## 主要特点
- **超快识别**：在约 1 秒内完成对 PDF 中文字、表格和公式的处理
- **保留版面翻译**：翻译过程中完整保持原文档的排版格式
- **OCR 支持**：高效处理扫描版文档
- **基于文本的 PDF**：不需要GPU
- **快速翻译**：约 10 秒内完成整个 PDF 的翻译
- **灵活的 API 集成**：可对接各种翻译服务提供商
- **网页对比界面**：支持原文与译文的并排对比
- **增强的 OCR 功能**：提供更准确的文本识别和处理能力
- **支持离线翻译**：使用较小翻译模型

## 安装和设置

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/polyglotpdf.git
cd polyglotpdf
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```
3. 在config.json内配置API密钥，不建议使用alicloud翻译API.

4. 运行应用：
```bash
python app.py
```

5. 访问网页界面：
在浏览器中打开 `http://127.0.0.1:8000`

## 环境要求
- Python 3.8+
- alibabacloud-alimt20181012==1.3.0
- alibabacloud-tea-openapi==0.3.12
- alibabacloud-tea-util==0.3.13
- deepl==1.17.0
- Flask==2.0.1
- Flask-Cors==5.0.0
- langdetect==1.0.9
- Pillow==10.2.0
- PyMuPDF==1.24.0
- pytesseract==0.3.10
- requests==2.31.0
- tencentcloud-sdk-python==3.0.1300
- tiktoken==0.6.0
- Werkzeug==2.0.1

## 致谢
本项目得益于 PyMuPDF 强大的 PDF 处理和版面保持功能。

## 即将推出的改进
- PDF 聊天功能
- 学术 PDF 搜索集成
- 进一步提升处理速度

### 待修复问题
- **问题描述**：应用重编辑时发生错误: `code=4: only Gray, RGB, and CMYK colorspaces supported`
- **现象**：文本块应用编辑时遇到不支持的色彩空间
- **当前解决方案**：遇到不支持的色彩空间时跳过该文本块
- **待解决思路**：对于包含不支持色彩空间的页面，整页切换至OCR模式处理
- **复现示例**：[查看不支持色彩空间的PDF样例](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/colorspace_issue_sample.pdf)

我帮你编写字体优化相关的说明：

中文版：
### 字体优化
当前在 `main.py` 的 `start` 函数中，文本插入使用了默认字体配置：
```python
# 当前配置
css=f"* {{font-family:{get_font_by_language(self.target_language)};font-size:auto;color: #111111 ;font-weight:normal;}}"
```

你可以通过以下方式优化字体显示：

1. **修改默认字体配置**
```python
# 自定义字体样式
css=f"""* {{
    font-family: {get_font_by_language(self.target_language)};
    font-size: auto;
    color: #111111;
    font-weight: normal;
    letter-spacing: 0.5px;  # 调整字间距
    line-height: 1.5;      # 调整行高
}}"""
```

2. **嵌入自定义字体**
你可以通过以下步骤嵌入自定义字体：
- 将字体文件（如.ttf，.otf）放置在项目的 `fonts` 目录下
- 在CSS中使用 `@font-face` 声明自定义字体
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

