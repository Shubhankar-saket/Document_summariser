import os
import io
import csv
import json
import requests
from flask import Flask, render_template, redirect, url_for, request, session, send_file
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pypdf
import docx

app = Flask(__name__)
app.secret_key = "interview_assignment_secret_key"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  


FOLDER_ID = "1ln7hu6m0EK9-Uuv3LbQ36S0XX6Q7yffD"
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:latest"


def extract_text(file_bytes, mime_type):
    """Extract text from PDF, DOCX, or TXT."""
    text = ""
    try:
        if mime_type == 'application/pdf':
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(
                [page.extract_text() for page in reader.pages if page.extract_text()]
            )
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        text = f"Error parsing file: {str(e)}"
    return text


def get_ollama_summary(text):
    """Summarize text using local Ollama (llama3)."""
    if not text.strip():
        return "No content found to summarize."

    prompt = (
        "Summarize the following document content in exactly 5 to 10 sentences.\n\n"
        f"{text[:15000]}"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"Ollama summarization failed: {str(e)}"


@app.route('/')
def index():
    if 'credentials' not in session:
        return render_template('index.html', summaries=None)

    creds = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=creds)

    query = f"'{FOLDER_ID}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name, mimeType, webViewLink)"
    ).execute()

    files = results.get('files', [])
    summaries = []

    for file in files:
        if any(ext in file['mimeType'] for ext in ['pdf', 'wordprocessingml', 'plain']):
            request_api = drive_service.files().get_media(fileId=file['id'])
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request_api)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            raw_text = extract_text(file_io.getvalue(), file['mimeType'])
            summary = get_ollama_summary(raw_text)

            summaries.append({
                'name': file['name'],
                'link': file['webViewLink'],
                'summary': summary
            })

    session['last_results'] = summaries
    return render_template('index.html', summaries=summaries)


@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)


@app.route('/callback')
def callback():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    session['credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    return redirect(url_for('index'))


@app.route('/download_csv')
def download_csv():
    if 'last_results' not in session or not session['last_results']:
        return "No data available to download.", 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['File Name', 'Summary'])

    for item in session['last_results']:
        writer.writerow([item['name'], item['summary']])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='document_summaries.csv'
    )


if __name__ == '__main__':
    app.run(port=5000, debug=True)
