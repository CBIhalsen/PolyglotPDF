# PolyglotPDF

[![Python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![PDF](https://img.shields.io/badge/pdf-documentation-brightgreen.svg)](https://example.com)
[![LaTeX](https://img.shields.io/badge/latex-typesetting-orange.svg)](https://www.latex-project.org/)
[![Translation](https://img.shields.io/badge/translation-supported-yellow.svg)](https://example.com)
[![Math](https://img.shields.io/badge/math-formulas-red.svg)](https://example.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24.0-blue.svg)](https://pymupdf.readthedocs.io/)

## 데모
<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true" width="80%" height="40%">

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

# 대규모 언어 모델 API 신청

## 302.AI
여러 국제 주류 AI 모델을 지원하는 AI 서비스 통합 플랫폼:
- 공식 웹사이트: [302.AI](https://302.ai)
- 가입하기: [초대 링크로 가입](https://share.302.ai/JBmCb1) (초대 코드 `JBmCb1` 사용 시 $1 보너스)
- 지원 모델: GPT-4o, GPT-4o-mini, Claude-3.5-Sonnet, DeepSeek-V3 등
- 특징: 하나의 계정으로 여러 AI 모델 사용 가능, 사용량 기반 과금

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

<details>
  <summary>표준 설치</summary>

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
</details>

<details>
  <summary>Docker 사용 방법</summary>

## 비지속성 빠른 시작

영구 디렉토리 설정 없이 PolyglotPDF를 빠르게 테스트하려면:

```bash
# 먼저 이미지 가져오기
docker pull 2207397265/polyglotpdf:latest

# 볼륨 마운트 없이 컨테이너 실행(컨테이너 삭제 시 데이터 손실)
docker run -d -p 12226:12226 --name polyglotpdf 2207397265/polyglotpdf:latest
```

이것은 PolyglotPDF를 시도하는 가장 빠른 방법이지만, 컨테이너가 중지되면 업로드된 모든 PDF와 구성 변경 사항이 손실됩니다.

## 영구 저장소 설치

```bash
# 필요한 디렉토리 생성
mkdir -p config fonts static/original static/target static/merged_pdf

# 설정 파일 생성
nano config/config.json    # 또는 원하는 텍스트 편집기 사용
# 프로젝트의 설정 템플릿을 이 파일에 복사
# API 키 등의 설정 정보를 입력하세요

# 권한 설정
chmod -R 755 config fonts static
```

## 빠른 시작

다음 명령을 사용하여 PolyglotPDF Docker 이미지를 가져와 실행:

```bash
# 이미지 가져오기
docker pull 2207397265/polyglotpdf:latest

# 컨테이너 실행
docker run -d -p 12226:12226 --name polyglotpdf \
  -v ./config/config.json:/app/config.json \
  -v ./fonts:/app/fonts \
  -v ./static/original:/app/static/original \
  -v ./static/target:/app/static/target \
  -v ./static/merged_pdf:/app/static/merged_pdf \
  2207397265/polyglotpdf:latest
```

## 애플리케이션 접속

컨테이너가 시작된 후, 브라우저에서 열기:
```
http://localhost:12226
```

## Docker Compose 사용

`docker-compose.yml` 파일 생성:

```yaml
version: '3'
services:
  polyglotpdf:
    image: 2207397265/polyglotpdf:latest
    ports:
      - "12226:12226"
    volumes:
      - ./config.json:/app/config.json # 설정 파일
      - ./fonts:/app/fonts # 폰트 파일
      - ./static/original:/app/static/original # 원본 PDF
      - ./static/target:/app/static/target # 번역된 PDF
      - ./static/merged_pdf:/app/static/merged_pdf # 병합된 PDF
    restart: unless-stopped
```

그리고 실행:

```bash
docker-compose up -d
```

## 자주 사용하는 Docker 명령어

```bash
# 컨테이너 중지
docker stop polyglotpdf

# 컨테이너 재시작
docker restart polyglotpdf

# 로그 확인
docker logs polyglotpdf
```
</details>

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

### TODO
- □ **사용자 정의 용어집**: 사용자 정의 용어집을 지원하고, 특정 분야의 전문적인 번역을 위한 프롬프트 설정
- □ **AI 재배치 기능**: 두 칸 PDF를 HTML 블로그의 한 줄 선형 읽기 형식으로 변환하여 모바일 장치에서 읽기 편하게 함
- □ **다중 형식 내보내기**: 번역 결과를 PDF, HTML, Markdown 등 다양한 형식으로 내보내기
- □ **다중 기기 동기화**: 컴퓨터에서 번역 완료한 후 모바일에서도 볼 수 있음
- □ **향상된 병합 로직**: 현재 버전의 기본 병합 로직에서 글꼴 이름 감지를 모두 비활성화하고, 가로, 세로, x, y 범위 중복이 모두 병합되도록 함

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
