# PolyglotPDF

[![Python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![PDF](https://img.shields.io/badge/pdf-documentation-brightgreen.svg)](https://example.com)
[![LaTeX](https://img.shields.io/badge/latex-typesetting-orange.svg)](https://www.latex-project.org/)
[![Translation](https://img.shields.io/badge/translation-supported-yellow.svg)](https://example.com)
[![Math](https://img.shields.io/badge/math-formulas-red.svg)](https://example.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24.0-blue.svg)](https://pymupdf.readthedocs.io/)

## 데모
<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true" width="80%" height="40%">

## 속도 비교

<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/Figure_1.png?raw=true" width="80%" height="40%">

### [🎬 전체 영상 보기](https://github.com/CBIhalsen/PolyglotPDF/blob/main/demo.mp4)
번역 API 선택지로 LLMs가 추가되었습니다. 권장 모델: Doubao, Qwen, deepseek v3, gpt4-o-mini입니다. 색상 공간 오류는 PDF 파일의 흰색 영역을 채우는 것으로 해결할 수 있습니다. 기존 text to text 번역 API는 삭제되었습니다.

또한, arXiv 검색 기능과 arXiv 논문의 LaTeX 번역 후 렌더링 추가를 고려 중입니다.

### 페이지 표시
<div style="display: flex; margin-bottom: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page1.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page2.jpeg?raw=true" width="40%" height="20%">
</div>
<div style="display: flex;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page3.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page4.png?raw=true" width="40%" height="20%">
</div>

# 중국 대규모 언어 모델 API 신청

## Doubao & Deepseek
화산 엔진 플랫폼을 통한 신청:
- 신청 주소: [화산 엔진-Doubao](https://www.volcengine.com/product/doubao/)
- 지원 모델: Doubao, Deepseek 시리즈 모델

## 통의천문(Qwen)
알리바바 클라우드 플랫폼을 통한 신청:
- 신청 주소: [알리바바 클라우드-통의천문](https://cn.aliyun.com/product/tongyi?from_alibabacloud=&utm_content=se_1019997984)
- 지원 모델: Qwen-Max, Qwen-Plus 등 시리즈 모델

## 개요
PolyglotPDF는 특수 기술을 사용하여 PDF 문서 내의 텍스트, 표, 수식을 초고속으로 인식하는 선진적인 PDF 처리 도구입니다. 보통 1초 이내에 처리를 완료하며, OCR 기능과 완벽한 레이아웃 유지 번역 기능을 지원합니다. 문서 전체의 번역은 보통 10초 이내에 완료됩니다(번역 API 제공업체에 따라 속도가 다릅니다).

## 주요 특징
- **초고속 인식**: 약 1초 내에 PDF 내의 텍스트, 표, 수식 처리 완료
- **레이아웃 유지 번역**: 번역 시 원문서의 서식을 완벽하게 유지
- **OCR 지원**: 스캔 버전 문서의 효율적인 처리
- **텍스트 기반 PDF**: GPU 불필요
- **고속 번역**: 약 10초 내에 PDF 전체 번역 완료
- **유연한 API 통합**: 각종 번역 서비스 제공업체와 연동 가능
- **웹 기반 비교 인터페이스**: 원문과 번역문의 병렬 비교 지원
- **강화된 OCR 기능**: 더 정확한 텍스트 인식과 처리 능력
- **오프라인 번역 지원**: 소규모 번역 모델 사용

## 설치 및 설정

### 사용 방법 중 하나는 라이브러리를 설치하는 것입니다:

```bash
pip install EbookTranslator
```

기본 사용법:

```bash
EbookTranslator your_file.pdf
```

매개변수를 사용한 예제:

```bash
EbookTranslator your_file.pdf -o en -t zh -b 1 -e 10 -c /path/to/config.json -d 300
```

#### Python 코드에서 사용

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

## 매개변수 설명

| 매개변수 | 명령줄 옵션 | 설명 | 기본값 |
|-----------|---------------------|-------------|---------------|
| `pdf_path` | 위치 인수 | PDF 파일 경로 | 필수 |
| `original_language` | `-o, --original` | 원본 언어 | `auto` |
| `target_language` | `-t, --target` | 대상 언어 | `zh` |
| `bn` | `-b, --begin` | 시작 페이지 번호 | `1` |
| `en` | `-e, --end` | 종료 페이지 번호 | 문서의 마지막 페이지 |
| `config_path` | `-c, --config` | 구성 파일 경로 | 현재 작업 디렉토리의 `config.json` |
| `DPI` | `-d, --dpi` | OCR 모드의 DPI | `72` |

#### 구성 파일

구성 파일은 JSON 형식으로, 기본적으로 현재 작업 디렉토리의 `config.json`에 저장됩니다. 파일이 없으면 프로그램은 내장된 기본 설정을 사용합니다.

#### 구성 파일 예제

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


#### 출력

번역된 PDF 파일은 `output_dir`에 지정된 디렉토리에 저장됩니다 (기본값은 현재 작업 디렉토리의 `target` 폴더).

## 라이선스

MIT

## 친화적인 UI 인터페이스 사용 방법

1. 저장소 클론:
```bash
git clone https://github.com/CBIhalsen/Polyglotpdf.git
cd polyglotpdf
```

2. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

3. config.json에서 API 키 설정. alicloud 번역 API 사용은 권장되지 않습니다.

4. 애플리케이션 실행:
```bash
python app.py
```

5. 웹 인터페이스 접속:
브라우저에서 `http://127.0.0.1:8000` 열기

## 환경 요구사항
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

## 감사의 말
본 프로젝트는 PyMuPDF의 강력한 PDF 처리와 레이아웃 유지 기능의 혜택을 받았습니다.

## 향후 개선 예정
- PDF 채팅 기능
- 학술 PDF 검색 통합
- 처리 속도 추가 향상

### 수정 대기 중인 문제
- **문제 설명**: 애플리케이션 재편집 시 오류: `code=4: only Gray, RGB, and CMYK colorspaces supported`
- **현상**: 텍스트 블록 편집 시 지원되지 않는 색상 공간 발생
- **현재 해결책**: 지원되지 않는 색상 공간을 포함한 텍스트 블록 건너뛰기
- **해결 접근 방식**: 지원되지 않는 색상 공간을 포함한 페이지 전체를 OCR 모드로 처리
- **재현 샘플**: [지원되지 않는 색상 공간의 PDF 샘플 보기](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/colorspace_issue_sample.pdf)

### 폰트 최적화
현재 `main.py`의 `start` 함수에서는 기본 폰트 설정으로 텍스트를 삽입합니다:
```python
# 현재 설정
css=f"* {{font-family:{get_font_by_language(self.target_language)};font-size:auto;color: #111111 ;font-weight:normal;}}"
```

폰트 표시는 다음 방법으로 최적화할 수 있습니다:

1. **기본 폰트 설정 변경**
```python
# 사용자 정의 폰트 스타일
css=f"""* {{
    font-family: {get_font_by_language(self.target_language)};
    font-size: auto;
    color: #111111;
    font-weight: normal;
    letter-spacing: 0.5px;  # 자간 조정
    line-height: 1.5;      # 행간 조정
}}"""
```

2. **사용자 정의 폰트 임베딩**
다음 단계로 사용자 정의 폰트를 임베딩할 수 있습니다:
- 폰트 파일(.ttf, .otf 등)을 프로젝트의 `fonts` 디렉토리에 배치
- CSS에서 `@font-face`를 사용하여 사용자 정의 폰트 선언
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

### 기본 원리
본 프로젝트는 Adobe Acrobat DC의 PDF 편집과 유사한 기본 원리를 채택하고, PyMuPDF를 사용하여 PDF 텍스트 블록을 인식하고 처리합니다:

- **핵심 처리 흐름**:
```python
# 페이지에서 텍스트 블록 가져오기
blocks = page.get_text("dict")["blocks"]

# 각 텍스트 블록 처리
for block in blocks:
    if block.get("type") == 0:  # 텍스트 블록
        bbox = block["bbox"]     # 텍스트 블록의 경계 상자 가져오기
        text = ""
        font_info = None
        # 텍스트와 폰트 정보 수집
        for line in block["lines"]:
            for span in line["spans"]:
                text += span["text"] + " "
```
이 방법으로 PDF 텍스트 블록을 직접 처리하여 원래 레이아웃을 유지한 채 효율적인 텍스트 추출과 수정을 실현합니다.

- **기술 선택**:
  - PyMuPDF를 사용하여 PDF 분석과 편집 수행
  - 텍스트 처리에 특화하여 문제의 복잡화 방지
  - 수식, 표, 페이지 재구성 등의 복잡한 AI 인식은 수행하지 않음

- **복잡한 처리를 피하는 이유**:
  - 수식, 표, PDF 페이지 재구성의 AI 인식에는 심각한 성능 병목 현상 존재
  - 복잡한 AI 처리는 계산 비용이 높음
  - 처리 시간이 크게 증가(수십 초 이상 소요 가능)
  - 프로덕션 환경에서의 대규모 저비용 배포가 어려움
  - 온라인 서비스의 신속한 응답에 부적합

- **프로젝트 위치**:
  - 레이아웃을 유지한 PDF 파일의 번역이 주목적
  - PDF의 AI 지원 읽기에 효율적인 구현 방법 제공
  - 최적의 성능과 비용 비율 추구

- **성능**:
  - PolyglotPDF API 서비스의 응답 시간: 약 1초/페이지
  - 낮은 계산 리소스 소비로 확장 가능한 배포 가능
  - 비용 효율이 높아 상업적 사용에 적합