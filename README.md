# Salesforce TIFF to PDF Uploader

This Python application provides a GUI for uploading TIFF files from Salesforce to PDF format. The application handles Salesforce authentication securely, processes TIFF files by converting them into PDFs, and uploads the converted PDFs back to Salesforce.

## Features

- **Secure Salesforce Authentication**: Credentials are encrypted and stored securely.
- **Download TIFF Files**: Downloads TIFF files created today from Salesforce.
- **Convert TIFF to PDF**: Converts downloaded TIFF files into PDF format.
- **Upload PDF to Salesforce**: Uploads the converted PDFs back to Salesforce as `ContentVersion` records.
- **Automatic File Management**: Automatically deletes the TIFF and PDF files after processing and uploading.

## Installation

### Prerequisites

- Python 3.x
- [pip](https://pip.pypa.io/en/stable/installation/)

### Step 1: Clone the Repository

git clone https://github.com/REsron/TifftoPDFSFPython/salesforce-tiff-to-pdf-uploader.git
cd salesforce-tiff-to-pdf-uploader

### Step 2 : Install Dependencies

pip install -r requirements.txt

Step 3: Run the Application

python salesforce_tiff_to_pdf_uploader.py

