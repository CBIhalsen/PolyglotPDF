# PolyglotPDF
## Demo

![Demo](demo.gif)

[Full Video](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.mp4)
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
- Python 3.7+
- PyMuPDF
- FastAPI
- uvicorn
- python-multipart
- other dependencies listed in requirements.txt

## Acknowledgments
This project leverages PyMuPDF's capabilities for efficient PDF processing and layout preservation.

## Upcoming Improvements
- PDF chat functionality
- Academic PDF search integration
- Optimization for even faster processing speeds



