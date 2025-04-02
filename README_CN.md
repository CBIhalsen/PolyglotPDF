# PolyglotPDF

[![Python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![PDF](https://img.shields.io/badge/pdf-documentation-brightgreen.svg)](https://example.com)
[![LaTeX](https://img.shields.io/badge/latex-typesetting-orange.svg)](https://www.latex-project.org/)
[![Translation](https://img.shields.io/badge/translation-supported-yellow.svg)](https://example.com)
[![Math](https://img.shields.io/badge/math-formulas-red.svg)](https://example.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24.0-blue.svg)](https://pymupdf.readthedocs.io/)

## Demo 
<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true" width="80%" height="40%">

## 速度对比

<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/Figure_1.png?raw=true" width="80%" height="40%">


### [🎬 Watch Full Video](https://github.com/CBIhalsen/PolyglotPDF/blob/main/demo.mp4)
已经加入llms作为翻译api的选择，建议选择：Doubao ,Qwen ,deepseek v3 ,gpt4-o-mini。色彩空间错误可以通过填充PDF文件中的白色区域来解决。 古老text to text翻译api已删除

另外，考虑添加arxiv搜索功能及对arxiv论文进行latex翻译后渲染。

### 页面展示
<div style="display: flex; margin-bottom: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page1.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page2.jpeg?raw=true" width="40%" height="20%">
</div>
<div style="display: flex;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page3.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page4.png?raw=true" width="40%" height="20%">
</div>

# 国内大语言模型API申请

## Doubao & Deepseek
通过火山引擎平台申请:
- 申请地址: [火山引擎-豆包](https://www.volcengine.com/product/doubao/)
- 支持模型: 豆包(Doubao)、Deepseek系列模型

## 通义千问(Qwen)
通过阿里云平台申请:
- 申请地址: [阿里云-通义千问](https://cn.aliyun.com/product/tongyi?from_alibabacloud=&utm_content=se_1019997984) 
- 支持模型: Qwen-Max、Qwen-Plus等系列模型


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

### 使用方法之一是安装该库：

```bash
pip install EbookTranslator
```

基本用法：

```bash
EbookTranslator your_file.pdf
```

带参数使用：

```bash
EbookTranslator your_file.pdf -o en -t zh -b 1 -e 10 -c /path/to/config.json -d 300
```

#### 在 Python 中使用

```python
from EbookTranslator import main_function

translator = main_function(
    pdf_path="your_file.pdf",
    original_language="en",
    target_language="zh",
    bn=1,
    en=10,
    config_path="/path/to/config.json",
    DPI=300
)
translator.main()
```

## 参数说明

| 参数 | 命令行选项 | 描述 | 默认值 |
|-----------|---------------------|-------------|---------------|
| `pdf_path` | 位置参数 | PDF 文件路径 | 必填 |
| `original_language` | `-o, --original` | 源语言 | `auto` |
| `target_language` | `-t, --target` | 目标语言 | `zh` |
| `bn` | `-b, --begin` | 起始页码 | `1` |
| `en` | `-e, --end` | 结束页码 | 文档的最后一页 |
| `config_path` | `-c, --config` | 配置文件路径 | 当前工作目录下的 `config.json` |
| `DPI` | `-d, --dpi` | OCR 模式的 DPI | `72` |

#### 配置文件

配置文件是一个 JSON 文件，默认位于当前工作目录下的 `config.json`。如果不存在，程序将使用内置的默认设置。

#### 配置文件示例

```json
{
  "count": 4,
  "PPC": 20,
  "translation_services": {
    "Doubao": {
      "auth_key": "",
      "model_name": ""
    },
    "Qwen": {
      "auth_key": "",
      "model_name": "qwen-plus"
    },
    "deepl": {
      "auth_key": ""
    },
    "deepseek": {
      "auth_key": "",
      "model_name": "ep-20250218224909-gps4n"
    },
    "openai": {
      "auth_key": "",
      "model_name": "gpt-4o-mini"
    },
    "youdao": {
      "app_key": "",
      "app_secret": ""
    }
  },
  "ocr_services": {
    "tesseract": {
      "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    }
  },
  "default_services": {
    "ocr_model": false,
    "line_model": false,
    "Enable_translation": true,
    "Translation_api": "openai"
  }
}
```


#### 输出

翻译后的 PDF 文件将保存在 `output_dir` 指定的目录中（默认是当前工作目录下的 `target` 文件夹）。

## 许可

MIT

## 使用友好 UI 界面的方法

1. 克隆仓库：
```bash
git clone https://github.com/CBIhalsen/Polyglotpdf.git
cd Polyglotpdf
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
在浏览器中打开 `http://127.0.0.1:12226`

## 环境要求
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

### 基本原理
本项目采用与 Adobe Acrobat DC 编辑 PDF 类似的基本原理，基于 PyMuPDF 识别和处理 PDF 文本块：

- **核心处理流程**：
```python
# 获取页面中的文本块
blocks = page.get_text("dict")["blocks"]

# 遍历处理每个文本块
for block in blocks:
    if block.get("type") == 0:  # 文本块
        bbox = block["bbox"]     # 获取文本块边界框
        text = ""
        font_info = None
        # 收集文本和字体信息
        for line in block["lines"]:
            for span in line["spans"]:
                text += span["text"] + " "
```
这种方式直接处理 PDF 文本块，保持原有布局不变，实现高效的文本提取和修改。

- **技术选择**：
  - 使用 PyMuPDF 进行 PDF 解析和编辑
  - 专注于文本处理，避免复杂化问题
  - 不进行 AI 识别公式、表格或页面重组等复杂操作

- **为什么避免复杂处理**：
  - AI 识别公式、表格和重组 PDF 页面的方式存在严重的性能瓶颈
  - 复杂的 AI 处理导致计算成本高昂
  - 处理时间显著增加（可能需要数十秒甚至更长）
  - 难以在生产环境中大规模低成本部署
  - 不适合需要快速响应的在线服务

- **项目定位**：
  - 主要用于保留布局的 PDF 文件翻译
  - 为 AI 辅助阅读 PDF 提供高效实现方式
  - 追求最佳性能价格比

- **性能表现**：
  - PolyglotPDF API 服务响应时间：约 1 秒/页
  - 低计算资源消耗，适合规模化部署
  - 成本效益高，适合商业应用

- * Contact author:
QQ： 1421243966
email: 1421243966@qq.com

Related questions answered and discussed：

 QQ group:
 1031477425
