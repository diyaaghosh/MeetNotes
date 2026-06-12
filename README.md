# MeetNotes

A Chrome extension that transcribes speech in real time during a meeting, then generates a summary and key points using NLP on a local FastAPI backend. Notes can be exported as a PDF.

---

## Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS config
│   │   ├── routes/api.py        # POST /process-text, POST /generate-pdf
│   │   └── services/
│   │       ├── hybrid_summarizer.py  
│   │       ├── extractor.py        
│   │       ├── pdf_service.py         # PDF generation with fpdf
│   │       └── summarizer.py        
│   ├── requirements.txt
|   |
|   ├──runtime.txt
│   └── run.py
└── extension/
    ├── index.html
    ├── manifest.json
    ├── script.js
    └── styles.css
```

---

## Running Locally

**Requirements:** Python 3.10+, Google Chrome

### 1. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The server starts at `http://127.0.0.1:8000`. On first run, it downloads the `all-MiniLM-L6-v2` sentence transformer model and NLTK punkt tokenizer data. This takes a minute.

### 2. Load the extension

1. Go to `chrome://extensions`
2. Enable Developer mode (toggle, top right)
3. Click "Load unpacked"
4. Select the `extension/` folder

Click the extension icon in the Chrome toolbar to open it.

---

## API Routes

Both routes are on the FastAPI server at `http://127.0.0.1:8000`.

**POST /process-text**

Accepts raw transcript text, returns summary sentences and bullet points.

```json
// request
{ "text": "full transcript string" }

// response
{
  "summary": ["sentence 1", "sentence 2", ...],
  "bullets": ["- sentence 1", "- sentence 2", ...]
}
```

**POST /generate-pdf**

Accepts summary and bullets, writes a PDF to disk, returns it as a file download.

```json
// request
{
  "summary": ["sentence 1", ...],
  "bullets": ["- sentence 1", ...]
}
```

Returns `notes.pdf` as a file response.

---

