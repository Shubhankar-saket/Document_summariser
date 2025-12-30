Document Summarizer via Google Drive Integration
Overview

This project is a test / evaluation application built to demonstrate integration between Google Drive, document parsing, and AI-powered summarization. The application connects to a specific Google Drive folder, downloads supported documents, extracts their content, and generates concise summaries using a local large language model.

The summarized results are displayed through a web interface and can be downloaded as a CSV report.

Project Purpose

This project was developed strictly for assessment and evaluation purposes as part of a technical assignment. It is not intended for public or production use.

Features

Google OAuth2 authentication

Restricted access to a specific Google Drive folder

Support for PDF, DOCX, and TXT documents

Text extraction from documents

AI-based summarization (5–10 sentences per document)

Web-based interface for viewing summaries

Downloadable CSV report

Local LLM inference using Ollama (llama3:latest)

Tech Stack

Backend: Flask (Python)

Authentication: Google OAuth2

Cloud API: Google Drive API

Document Parsing:

pypdf for PDF files

python-docx for DOCX files

AI Model: Ollama (local inference)

LLM: llama3:latest

Output Formats: HTML and CSV

System Workflow

User authenticates using Google OAuth2.

The application accesses a predefined Google Drive folder.

Supported documents are listed and downloaded.

Text is extracted based on document type.

Extracted content is summarized using a local LLM.

Summaries are displayed in a web interface.

Results can be exported as a CSV file.

Usage

Authenticate using the Login with Google option.

The application automatically fetches and summarizes documents.

Summaries are displayed in a table with file names and links.

Use the Download CSV option to export results.

Output Details

Each summarized document includes:

File name

Google Drive file link

AI-generated summary (5–10 sentences)

CSV export contains:

File Name

Summary

Project Access & Authorization Notice

This is a restricted-access test project.

Due to Google OAuth and Drive permission constraints:

Only explicitly authorized users can access the application.

Authentication is limited to a predefined list of email addresses.

If you wish to access or test this application:

Please send your Google email address to the project owner.

Your email will be manually added to the authorized users list in the Google Cloud Console.

Access will be granted only after approval.

Unauthorized users will not be able to authenticate or view any documents.

Notes

OAuth insecure transport is enabled only for local development.

Large documents are truncated to ensure stable summarization.

The architecture allows easy extension for chunking, RAG, or async processing.

Application Workflow

User Access & Authentication

The user opens the web application.

If not authenticated, the user is redirected to Google OAuth2 login.

Only pre-approved email addresses are allowed to authenticate.

OAuth Authorization

Google OAuth2 flow validates the user.

Access and refresh tokens are securely stored in the session.

Upon successful authentication, the user is redirected to the home page.

Google Drive Folder Access

The application connects to the Google Drive API using the authenticated credentials.

A predefined Google Drive folder (hardcoded FOLDER_ID) is accessed.

All non-trashed files in the folder are listed.

Document Filtering

Files are filtered based on supported MIME types:

PDF

DOCX

TXT

Unsupported file types are ignored.

File Download

Each supported document is downloaded from Google Drive into memory.

Files are processed one by one to ensure stability.

Text Extraction

Based on file type:

PDFs are parsed using pypdf

DOCX files are parsed using python-docx

TXT files are decoded directly

Raw text is extracted from each document.

AI Summarization

Extracted text is truncated to a safe length.

Text is sent to the local Ollama server.

The llama3:latest model generates a summary of 5–10 sentences.

Result Aggregation

For each document, the following data is stored:

File name

Google Drive file link

Generated summary

Results are cached in the session for reuse.

Web Interface Rendering

Summaries are displayed in an HTML table.

Each entry includes the document name, summary, and a clickable file link.

CSV Export

User can download all summaries as a CSV file.

CSV contains file names and their corresponding summaries.

Export uses cached session data to avoid recomputation.

Session Termination

Session data persists until browser session ends.

Re-authentication is required after session expiration.