from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="EbookTranslator",
    version="0.3.3",
    author="Chen",
    author_email="1421243966@qq.com",
    description="The world's highest performing e-book retention layout translation library",
    long_description=long_description,  # 添加这一行
    long_description_content_type="text/markdown",
    url="https://github.com/1421243966/EbookTranslator",  # 更新为您的实际GitHub仓库
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pymupdf>=1.18.0",
        "Pillow>=8.0.0",
        "pytesseract>=0.3.0",
        "deepl>=1.17.0",
        "requests>=2.25.0",
        "Werkzeug>=2.0.0",
        "aiohttp>=3.7.4",
    ],
    entry_points={
        "console_scripts": [
            "EbookTranslator=EbookTranslator.cli:main",
        ],
    },
    include_package_data=True,
    keywords=["ebook", "translation", "pdf", "ocr", "nlp", "language"],
    project_urls={
        "Bug Reports": "https://github.com/1421243966/EbookTranslator/issues",
        "Source": "https://github.com/1421243966/EbookTranslator",
        "Documentation": "https://github.com/1421243966/EbookTranslator#readme",
    },
)
