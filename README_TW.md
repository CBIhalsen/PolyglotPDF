# PolyglotPDF

[![Python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![PDF](https://img.shields.io/badge/pdf-documentation-brightgreen.svg)](https://example.com)
[![LaTeX](https://img.shields.io/badge/latex-typesetting-orange.svg)](https://www.latex-project.org/)
[![Translation](https://img.shields.io/badge/translation-supported-yellow.svg)](https://example.com)
[![Math](https://img.shields.io/badge/math-formulas-red.svg)](https://example.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24.0-blue.svg)](https://pymupdf.readthedocs.io/)

## 演示
<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true" width="80%" height="40%">

## 速度對比

<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/Figure_1.png?raw=true" width="80%" height="40%">

### [🎬 觀看完整影片](https://github.com/CBIhalsen/PolyglotPDF/blob/main/demo.mp4)
翻譯API選項已新增LLMs。推薦模型：Doubao、Qwen、deepseek v3、gpt4-o-mini。色彩空間錯誤可透過填充PDF檔案的白色區域來解決。舊有的text to text翻譯API已被移除。

此外，我們正在考慮新增arXiv搜尋功能和arXiv論文的LaTeX翻譯後渲染功能。

### 頁面展示
<div style="display: flex; margin-bottom: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page1.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page2.jpeg?raw=true" width="40%" height="20%">
</div>
<div style="display: flex;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page3.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page4.png?raw=true" width="40%" height="20%">
</div>

# 中國大型語言模型API申請

## Doubao & Deepseek
從火山引擎平台申請：
- 申請地址：[火山引擎-Doubao](https://www.volcengine.com/product/doubao/)
- 支援模型：Doubao、Deepseek系列模型

## 通義千問(Qwen)
從阿里雲平台申請：
- 申請地址：[阿里雲-通義千問](https://cn.aliyun.com/product/tongyi?from_alibabacloud=&utm_content=se_1019997984)
- 支援模型：Qwen-Max、Qwen-Plus等系列模型

## 概述
PolyglotPDF是一款使用特殊技術，能夠超高速識別PDF文件中文字、表格、數學公式的先進PDF處理工具。通常能在1秒內完成處理，並支援OCR功能和完整的版面保持翻譯功能。整份文件的翻譯通常能在10秒內完成（速度依翻譯API提供商而異）。

## 主要特點
- **超高速識別**：約1秒內完成PDF中文字、表格、數學公式的處理
- **版面保持翻譯**：翻譯時完整保持原文件的格式
- **OCR支援**：高效處理掃描版文件
- **文字基礎PDF**：無需GPU
- **快速翻譯**：約10秒完成PDF整體翻譯
- **靈活API整合**：可與各種翻譯服務提供商連接
- **網頁基礎比較介面**：支援原文與譯文並列比較
- **強化OCR功能**：更準確的文字識別和處理能力
- **離線翻譯支援**：使用小型翻譯模型

## 安裝與設定

### 使用方法之一是安裝該庫：

```bash
pip install EbookTranslator
```

基本用法：

```bash
EbookTranslator your_file.pdf
```

帶參數使用：

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

## 參數說明

| 參數 | 命令行選項 | 描述 | 默認值 |
|-----------|---------------------|-------------|---------------|
| `pdf_path` | 位置參數 | PDF 文件路徑 | 必填 |
| `original_language` | `-o, --original` | 源語言 | `auto` |
| `target_language` | `-t, --target` | 目標語言 | `zh` |
| `bn` | `-b, --begin` | 起始頁碼 | `1` |
| `en` | `-e, --end` | 結束頁碼 | 文檔的最後一頁 |
| `config_path` | `-c, --config` | 配置文件路徑 | 當前工作目錄下的 `config.json` |
| `DPI` | `-d, --dpi` | OCR 模式的 DPI | `72` |

#### 配置文件

配置文件是一個 JSON 文件，默認位於當前工作目錄下的 `config.json`。如果不存在，程序將使用內置的默認設置。

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

#### 配置選項

- `translation_service`: 翻譯服務提供商（例如 "google", "deepl", "baidu"）
- `api_key`: 翻譯 API 密鑰（如果需要）
- `translation_mode`: 翻譯模式，"online" 或 "offline"
- `ocr_enabled`: 是否啟用 OCR 識別
- `tesseract_path`: Tesseract OCR 引擎路徑（如果未添加到系統 PATH）
- `output_dir`: 輸出目錄
- `language_codes`: 語言代碼映射
- `font_mapping`: 不同語言對應的字體

#### 輸出

翻譯後的 PDF 文件將保存在 `output_dir` 指定的目錄中（默認是當前工作目錄下的 `target` 文件夾）。

## 許可

MIT

## 使用友好 UI 介面的方法

1. 複製儲存庫：
```bash
git clone https://github.com/CBIhalsen/Polyglotpdf.git
cd Polyglotpdf
```

2. 安裝相依套件：
```bash
pip install -r requirements.txt
```

3. 在config.json中設定API金鑰。不建議使用alicloud翻譯API。

4. 執行應用程式：
```bash
python app.py
```

5. 存取網頁介面：
在瀏覽器中開啟 `http://127.0.0.1:8000`

## 環境需求
- Python 3.8+
- deepl==1.17.0
- Flask==2.0.1
- Flask-Cors==5.0.0
- langdetect==1.0.9
- Pillow==10.2.0
- PyMuPDF==1.24.0
- pytesseract==0.3.10
- requests==2.31.0
- Werkzeug==2.0.1

## 致謝
本專案受益於PyMuPDF強大的PDF處理和版面保持功能。

## 未來改進計劃
- PDF聊天功能
- 學術PDF搜尋整合
- 進一步提升處理速度

### 待修正問題
- **問題描述**：應用程式重新編輯時的錯誤：`code=4: only Gray, RGB, and CMYK colorspaces supported`
- **現象**：編輯文字區塊時出現不支援的色彩空間
- **目前解決方案**：跳過包含不支援色彩空間的文字區塊
- **解決方向**：使用OCR模式處理包含不支援色彩空間的整個頁面
- **重現範例**：[查看不支援色彩空間的PDF範例](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/colorspace_issue_sample.pdf)

### 字型最佳化
目前在`main.py`的`start`函數中，使用預設字型設定插入文字：
```python
# 目前設定
css=f"* {{font-family:{get_font_by_language(self.target_language)};font-size:auto;color: #111111 ;font-weight:normal;}}"
```

字型顯示可透過以下方式最佳化：

1. **修改預設字型設定**
```python
# 自訂字型樣式
css=f"""* {{
    font-family: {get_font_by_language(self.target_language)};
    font-size: auto;
    color: #111111;
    font-weight: normal;
    letter-spacing: 0.5px;  # 調整字距
    line-height: 1.5;      # 調整行高
}}"""
```

2. **嵌入自訂字型**
可透過以下步驟嵌入自訂字型：
- 將字型檔案（.ttf、.otf等）放置在專案的`fonts`目錄中
- 在CSS中使用`@font-face`宣告自訂字型
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
本專案採用與Adobe Acrobat DC的PDF編輯類似的基本原理，使用PyMuPDF識別和處理PDF文字區塊：

- **核心處理流程**：
```python
# 從頁面取得文字區塊
blocks = page.get_text("dict")["blocks"]

# 處理每個文字區塊
for block in blocks:
    if block.get("type") == 0:  # 文字區塊
        bbox = block["bbox"]     # 取得文字區塊的邊界框
        text = ""
        font_info = None
        # 收集文字和字型資訊
        for line in block["lines"]:
            for span in line["spans"]:
                text += span["text"] + " "
```
這種方式直接處理PDF文字區塊，在保持原始版面的同時，實現高效的文字擷取和修改。

- **技術選擇**：
  - 使用PyMuPDF進行PDF解析和編輯
  - 專注於文字處理，避免問題複雜化
  - 不進行複雜的AI識別，如數學公式、表格、頁面重構

- **避免複雜處理的原因**：
  - 數學公式、表格、PDF頁面重構的AI識別存在嚴重的效能瓶頸
  - 複雜的AI處理計算成本高昂
  - 處理時間大幅增加（可能需要數十秒以上）
  - 難以在生產環境中進行大規模低成本部署
  - 不適合線上服務的快速回應

- **專案定位**：
  - 主要目的是保持版面的PDF檔案翻譯
  - 提供PDF AI輔助閱讀的高效實現方式
  - 追求最佳效能和成本比

- **效能表現**：
  - PolyglotPDF API服務回應時間：約1秒/頁
  - 低計算資源消耗，可擴展部署
  - 成本效益高，適合商業使用
