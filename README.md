# PolyglotPDF
## Demo

[![Demo](demo.gif)](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true)
![image](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true)
[Full Video](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true)

## Overview
PolyglotPDF is an advanced PDF processing tool that employs specialized techniques for ultra-fast text, table, and formula recognition in PDF documents, typically completing processing within 1 second. It features OCR capabilities and layout-preserving translation, with full document translations usually completed within 10 seconds (speed may vary depending on the translation API provider).

## Features
- **Ultra-Fast Recognition**: Processes text, tables, and formulas in PDFs within ~1 second
- **Layout-Preserving Translation**: Maintains original document formatting while translating content
- **OCR Support**: Handles scanned documents efficiently
- **Quick Translation**: Complete PDF translation in approximately 10 seconds
- **Flexible API Integration**: Compatible with various translation service providers
- **Web-based Comparison Interface**: Side-by-side comparison of original and translated documents
- **Enhanced OCR Capabilities**: Improved accuracy in text recognition and processing

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/polyglotpdf.git
cd polyglotpdf
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Access the web interface:
Open your browser and navigate to `http://127.0.0.1:8000`

## Requirements
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

## Acknowledgments
This project leverages PyMuPDF's capabilities for efficient PDF processing and layout preservation.

## Upcoming Improvements
- PDF chat functionality
- Academic PDF search integration
- Optimization for even faster processing speeds



