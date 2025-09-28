# PolyglotPDF

[![Python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![PDF](https://img.shields.io/badge/pdf-documentation-brightgreen.svg)](https://example.com)
[![LaTeX](https://img.shields.io/badge/latex-typesetting-orange.svg)](https://www.latex-project.org/)
[![Translation](https://img.shields.io/badge/translation-supported-yellow.svg)](https://example.com)
[![Math](https://img.shields.io/badge/math-formulas-red.svg)](https://example.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24.0-blue.svg)](https://pymupdf.readthedocs.io/)

## デモ
<img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/demo.gif?raw=true" width="80%" height="40%">

### [🎬 フルビデオを見る](https://github.com/CBIhalsen/PolyglotPDF/blob/main/demo.mp4)
翻訳APIの選択肢としてLLMsが追加されました。推奨モデル：Doubao、Qwen、deepseek v3、gpt4-o-miniです。カラースペースエラーはPDFファイルの白色領域を埋めることで解決できます。古いtext to text翻訳APIは削除されました。

また、arXiv検索機能とarXiv論文のLaTeX翻訳後のレンダリングの追加を検討中です。

### ページ表示
<div style="display: flex; margin-bottom: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page1.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page2.jpeg?raw=true" width="40%" height="20%">
</div>
<div style="display: flex;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page3.png?raw=true" width="40%" height="20%" style="margin-right: 20px;">
    <img src="https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/page4.png?raw=true" width="40%" height="20%">
</div>

# 大規模言語モデルAPIの申請

## 302.AI
複数の国際主流AIモデルをサポートするAIサービス統合プラットフォーム:
- 公式サイト: [302.AI](https://302.ai)
- 登録サイト: [招待リンクで登録](https://share.302.ai/JBmCb1) (招待コード`JBmCb1`を使用して登録すると$1のボーナス)
- 対応モデル: GPT-4o、GPT-4o-mini、Claude-3.5-Sonnet、DeepSeek-V3など
- 特徴: 一つのアカウントで複数のAIモデルを利用可能、従量課金制

## Doubao & Deepseek
火山エンジンプラットフォームから申請:
- 申請先: [火山エンジン-Doubao](https://www.volcengine.com/product/doubao/)
- 対応モデル: Doubao、Deepseekシリーズモデル

## 通義千問(Qwen)
アリババクラウドプラットフォームから申請:
- 申請先: [アリババクラウド-通義千問](https://cn.aliyun.com/product/tongyi?from_alibabacloud=&utm_content=se_1019997984)
- 対応モデル: Qwen-Max、Qwen-Plusなどのシリーズモデル

## 概要
PolyglotPDFは、特殊技術を用いてPDF文書内のテキスト、表、数式を超高速で認識する先進的なPDF処理ツールです。通常1秒以内で処理を完了し、OCR機能と完全なレイアウト保持翻訳機能をサポートしています。文書全体の翻訳は通常10秒以内で完了します（翻訳APIプロバイダーによって速度は異なります）。

## 主な特徴
- **超高速認識**：約1秒でPDF内のテキスト、表、数式の処理を完了
- **レイアウト保持翻訳**：翻訳時に原文書の書式を完全に保持
- **OCRサポート**：スキャン版文書の効率的な処理
- **テキストベースPDF**：GPUは不要
- **高速翻訳**：約10秒でPDF全体の翻訳を完了
- **柔軟なAPI統合**：各種翻訳サービスプロバイダーと連携可能
- **Webベース比較インターフェース**：原文と訳文の並列比較をサポート
- **強化されたOCR機能**：より正確なテキスト認識と処理能力
- **オフライン翻訳対応**：小規模翻訳モデルの使用

## インストールとセットアップ

<details>
  <summary>標準インストール</summary>

1. リポジトリのクローン：
```bash
git clone https://github.com/CBIhalsen/Polyglotpdf.git
cd polyglotpdf
```

2. 依存パッケージのインストール：
```bash
pip install -r requirements.txt
```

3. config.json内でAPIキーを設定。alicloud翻訳APIの使用は推奨されません。

4. アプリケーションの実行：
```bash
python app.py
```

5. Webインターフェースへのアクセス：
ブラウザで `http://127.0.0.1:8000` を開く
</details>

<details>
  <summary>Docker 使用方法</summary>

## 永続化なしの簡易起動

永続化ディレクトリを設定せずにPolyglotPDFをすぐにテストしたい場合：

```bash
# まずイメージをプル
docker pull 2207397265/polyglotpdf:latest

# ボリュームをマウントせずにコンテナを実行（コンテナ削除後にデータは失われます）
docker run -d -p 12226:12226 --name polyglotpdf 2207397265/polyglotpdf:latest
```

これはPolyglotPDFを試す最速の方法ですが、コンテナ停止後はアップロードしたPDFと設定変更がすべて失われます。

## 永続化ストレージでのインストール

```bash
# 必要なディレクトリを作成
mkdir -p config fonts static/original static/target static/merged_pdf

# 設定ファイルを作成
nano config/config.json    # または任意のテキストエディタを使用
# プロジェクトの設定テンプレートをこのファイルにコピー
# APIキーなどの設定情報を入力してください

# 権限を設定
chmod -R 755 config fonts static
```

## クイックスタート

以下のコマンドでPolyglotPDF Dockerイメージをプルして実行：

```bash
# イメージをプル
docker pull 2207397265/polyglotpdf:latest

# コンテナを実行
docker run -d -p 12226:12226 --name polyglotpdf \
  -v ./config/config.json:/app/config.json \
  -v ./fonts:/app/fonts \
  -v ./static/original:/app/static/original \
  -v ./static/target:/app/static/target \
  -v ./static/merged_pdf:/app/static/merged_pdf \
  2207397265/polyglotpdf:latest
```

## アプリケーションへのアクセス

コンテナ起動後、ブラウザで開く：
```
http://localhost:12226
```

## Docker Composeの使用

`docker-compose.yml`ファイルを作成：

```yaml
version: '3'
services:
  polyglotpdf:
    image: 2207397265/polyglotpdf:latest
    ports:
      - "12226:12226"
    volumes:
      - ./config.json:/app/config.json # 設定ファイル
      - ./fonts:/app/fonts # フォントファイル
      - ./static/original:/app/static/original # 原本PDF
      - ./static/target:/app/static/target # 翻訳後PDF
      - ./static/merged_pdf:/app/static/merged_pdf # 結合PDF
    restart: unless-stopped
```

そして実行：

```bash
docker-compose up -d
```

## よく使うDockerコマンド

```bash
# コンテナを停止
docker stop polyglotpdf

# コンテナを再起動
docker restart polyglotpdf

# ログの確認
docker logs polyglotpdf
```
</details>

## 環境要件
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

## 謝辞
本プロジェクトはPyMuPDFの強力なPDF処理とレイアウト保持機能の恩恵を受けています。

## 今後の改善予定
- PDFチャット機能
- 学術PDF検索の統合
- 処理速度のさらなる向上

### 修正待ちの問題
- **問題の説明**：アプリケーション再編集時のエラー: `code=4: only Gray, RGB, and CMYK colorspaces supported`
- **現象**：テキストブロックの編集時に非対応のカラースペースが発生
- **現在の解決策**：非対応のカラースペースを含むテキストブロックをスキップ
- **解決へのアプローチ**：非対応のカラースペースを含むページ全体をOCRモードで処理
- **再現サンプル**：[非対応カラースペースのPDFサンプルを見る](https://github.com/CBIhalsen/PolyglotPDF/blob/main/static/colorspace_issue_sample.pdf)

### TODO
- □ **カスタム用語集**: カスタム用語集をサポートし、特定分野の専門的な翻訳のためのプロンプト設定
- □ **AI再配置機能**: 二段組みPDFをHTMLブログの一列リニア読書形式に変換し、モバイル端末での読書を容易にする
- □ **複数形式エクスポート**: 翻訳結果をPDF、HTML、Markdown等の形式にエクスポート可能
- □ **マルチデバイス同期**: コンピュータで翻訳完了後、スマートフォンでも閲覧可能
- □ **強化されたマージロジック**: 現バージョンのデフォルトマージロジックではフォント名検出を完全に無効にし、水平・垂直・x・y範囲の重複をすべてマージする

### フォントの最適化
現在、`main.py`の`start`関数では、デフォルトのフォント設定でテキストを挿入しています：
```python
# 現在の設定
css=f"* {{font-family:{get_font_by_language(self.target_language)};font-size:auto;color: #111111 ;font-weight:normal;}}"
```

フォント表示は以下の方法で最適化できます：

1. **デフォルトフォント設定の変更**
```python
# カスタムフォントスタイル
css=f"""* {{
    font-family: {get_font_by_language(self.target_language)};
    font-size: auto;
    color: #111111;
    font-weight: normal;
    letter-spacing: 0.5px;  # 文字間隔の調整
    line-height: 1.5;      # 行の高さの調整
}}"""
```

2. **カスタムフォントの埋め込み**
以下の手順でカスタムフォントを埋め込むことができます：
- フォントファイル（.ttf、.otfなど）をプロジェクトの`fonts`ディレクトリに配置
- CSSで`@font-face`を使用してカスタムフォントを宣言
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
本プロジェクトはAdobe Acrobat DCのPDF編集と同様の基本原理を採用し、PyMuPDFを使用してPDFテキストブロックを認識・処理します：

- **コア処理フロー**：
```python
# ページからテキストブロックを取得
blocks = page.get_text("dict")["blocks"]

# 各テキストブロックを処理
for block in blocks:
    if block.get("type") == 0:  # テキストブロック
        bbox = block["bbox"]     # テキストブロックの境界ボックスを取得
        text = ""
        font_info = None
        # テキストとフォント情報の収集
        for line in block["lines"]:
            for span in line["spans"]:
                text += span["text"] + " "
```
この方法でPDFテキストブロックを直接処理し、元のレイアウトを保持したまま、効率的なテキストの抽出と修正を実現します。

- **技術選択**：
  - PyMuPDFを使用してPDFの解析と編集を行う
  - テキスト処理に特化し、問題の複雑化を避ける
  - 数式、表、ページ再構成などの複雑なAI認識は行わない

- **複雑な処理を避ける理由**：
  - 数式、表、PDFページ再構成のAI認識には深刻なパフォーマンスのボトルネックが存在
  - 複雑なAI処理は計算コストが高額
  - 処理時間が大幅に増加（数十秒以上かかる可能性）
  - 本番環境での大規模な低コスト展開が困難
  - オンラインサービスの迅速なレスポンスに不適

- **プロジェクトの位置づけ**：
  - レイアウトを保持したPDFファイルの翻訳が主目的
  - PDFのAI支援読書に効率的な実装方法を提供
  - 最適なパフォーマンスとコスト比を追求

- **パフォーマンス**：
  - PolyglotPDF APIサービスのレスポンス時間：約1秒/ページ
  - 低計算リソース消費で、スケーラブルな展開が可能
  - コスト効率が高く、商用利用に適している
