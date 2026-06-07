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
│   │       ├── hybrid_summarizer.py   # BERT embeddings + MMR
│   │       ├── extractor.py           # Converts summary sentences to bullets
│   │       ├── pdf_service.py         # PDF generation with fpdf
│   │       └── summarizer.py          # TF-IDF summarizer (unused in main flow)
│   ├── requirements.txt
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

## How the Summarization Works

The main pipeline is in `hybrid_summarizer.py`.

**1. Sentence splitting and cleaning**

The transcript is tokenized into sentences with NLTK. Filler words (`um`, `uh`, `like`, etc.) and noise phrases (`can you hear`, `hello`, etc.) are filtered out. Sentences under 4 words or containing questions are also dropped.

**2. Sentence embeddings**

The cleaned sentences are encoded with `sentence-transformers/all-MiniLM-L6-v2`, a lightweight BERT-based model that maps each sentence to a 384-dimensional vector.

**3. MMR selection**

Maximal Marginal Relevance (MMR) selects the top N sentences by balancing two things: relevance to the centroid of all sentence embeddings, and diversity from already-selected sentences. The tradeoff is controlled by `lambda_param` (default 0.7, skewing toward relevance). This avoids picking multiple sentences that say the same thing.

**4. Bullet extraction**

`extractor.py` takes the selected summary sentences and prepends a bullet marker to each. No additional NLP happens here.

**5. PDF generation**

`pdf_service.py` uses `fpdf` to produce a two-section PDF: Summary (paragraph form) and Key Points (bullet list). The bullet marker is converted from `*` to `-` since fpdf does not handle the unicode dot character.
---
<h2>Summarizer Model Architecture</h2>

<p align="center">
  <img src="assets/summarizer_model.png" alt="Summarizer Model" width="800">
</p>
---

## Known Issues

- The extension must be reloaded from `chrome://extensions` after any change to `script.js` or `manifest.json`.
- `summarizer.py` (TF-IDF approach) is present but not connected to any route. It was the earlier implementation.
- The PDF is written to `backend/output.pdf` on disk before being served. Concurrent requests would overwrite it.
