# PolyglotPDF README

## Overview

PolyglotPDF is a multilingual PDF processing tool designed to facilitate both online and offline translations while preserving the original layout. It excels in converting scanned PDF documents through OCR, surpassing the speed of traditional tools like ocrmypdf. This tool is equipped with a Web UI for direct comparison with the original PDFs and enhances user interaction through a PDF chat functionality. Additionally, it integrates academic PDF search capabilities via the Semantic Scholar API, making it a comprehensive solution for handling diverse PDF-related tasks.

## Acknowledgments

This project owes its successful implementation to the powerful features of PyMuPDF, which have been instrumental in achieving layout-preserving translations and swift OCR conversions for scanned PDFs.

## Features

- **Layout-Preserving Translation**: Offers both online and offline translation services that maintain the original document layout.
- **Fast OCR Conversion**: Utilizes Tesseract for OCR conversions, significantly outpacing ocrmypdf in speed. Online translations are powered by DeepL's API, typically processing a document in under 12 seconds. However, it's worth noting that the current OCR implementation struggles with accurately recognizing content within tables.
- **Web UI**: A user-friendly interface for comparing translations with the original PDFs is in development.
- **PDF Chat Functionality**: An upcoming feature that will allow users to interact with PDF documents in a novel way.
- **Academic PDF Search**: Leveraging the Semantic Scholar API, this feature will enable efficient searching of academic PDFs.

## Upcoming Improvements

- **OCR Enhancement**: Plans are underway to transition to PaddleOCR for improved accuracy, especially in recognizing table content within PDFs.
- **Discontinuation of Text Recognition in Images**: Future versions will no longer focus on recognizing text within images in PDFs.
- **Web UI Completion**: The development of the Web UI interface is ongoing, aiming to provide an intuitive and interactive experience for users.
- **PDF Chat Functionality**: The implementation of a chat feature within PDFs is anticipated, fostering a more engaging way to interact with documents.
- **Academic PDF Search**: Integration of a more robust search feature for academic PDFs is in progress, intending to streamline the research process.

PolyglotPDF is committed to continuous improvement and eagerly anticipates delivering these enhancements to further aid users in their PDF processing tasks.
