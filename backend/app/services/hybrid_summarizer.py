import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# -----------------------------
# NLTK setup (safe for Render)
# -----------------------------
nltk_data_path = "/opt/render/nltk_data"
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_path)

# -----------------------------
# Load model ONCE (critical fix)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# Text processing
# -----------------------------
def sentence_split(text):
    return nltk.sent_tokenize(text)


def remove_fillers(sentences):
    fillers = {"um", "uh", "like", "you know", "so", "actually", "basically"}
    return [s for s in sentences if not any(f in s.lower() for f in fillers)]


def is_valid(sentence):
    s = sentence.lower()
    if len(s.split()) < 4:
        return False
    if "?" in s:
        return False

    noise = ["can you hear", "hello", "hi", "ok", "yeah"]
    return not any(n in s for n in noise)


# -----------------------------
# SAFE summarization (NO MMR)
# -----------------------------
def summarize(text, top_n=3):
    sentences = sentence_split(text)
    sentences = remove_fillers(sentences)
    sentences = [s for s in sentences if is_valid(s)]

    # HARD LIMIT (critical for Render stability)
    sentences = sentences[:10]

    if not sentences:
        return ["No meaningful content to summarize."]

    # embeddings (fast + stable now)
    embeddings = model.encode(sentences, show_progress_bar=False)

    # centroid scoring (simple, replaces MMR)
    centroid = np.mean(embeddings, axis=0).reshape(1, -1)

    scores = cosine_similarity(embeddings, centroid).flatten()

    ranked_idx = np.argsort(scores)[::-1][:top_n]

    summary = [sentences[i] for i in ranked_idx]

    return summary
