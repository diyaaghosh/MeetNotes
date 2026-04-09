import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# ---------------- NLTK Setup ----------------
nltk_data_path = "/opt/render/nltk_data"
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_path)


# ---------------- Lazy Model Loading ----------------
model = None

def get_model():
    global model
    if model is None:
        print("Loading SentenceTransformer model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


# ---------------- Sentence Splitting ----------------
def sentence_split(text):
    return nltk.sent_tokenize(text)


# ---------------- Remove Fillers ----------------
def remove_fillers(sentences):
    fillers = {"um", "uh", "like", "you know", "so", "actually", "basically"}
    return [s for s in sentences if not any(f in s.lower() for f in fillers)]


# ---------------- Remove Repeated Adjacent Words ----------------
def remove_same_adjacent_words(sentences):
    cleaned = []
    for s in sentences:
        words = s.split()
        cleaned.append(
            " ".join([w for i, w in enumerate(words) if i == 0 or w != words[i-1]])
        )
    return cleaned


# ---------------- Sentence Filtering ----------------
def is_valid(sentence):
    s = sentence.lower()

    if len(s.split()) < 4:
        return False

    if "?" in s:
        return False

    noise = ["can you hear", "hello", "hi", "ok", "yeah"]
    if any(n in s for n in noise):
        return False

    return True


# ---------------- Generate Embeddings ----------------
def get_embeddings(sentences):
    model = get_model()
    return model.encode(sentences)


# ---------------- MMR Summarization ----------------
def mmr_summary(sentences, embeddings, top_n=5, lambda_param=0.7):

    selected_idx = []
    centroid = np.mean(embeddings, axis=0)

    for _ in range(min(top_n, len(sentences))):

        mmr_scores = []

        for i in range(len(sentences)):
            if i in selected_idx:
                continue

            relevance = cosine_similarity([embeddings[i]], [centroid])[0][0]

            if not selected_idx:
                diversity = 0
            else:
                diversity = max(
                    cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                    for j in selected_idx
                )

            score = lambda_param * relevance - (1 - lambda_param) * diversity

            mmr_scores.append((score, i))

        best = max(mmr_scores)[1]
        selected_idx.append(best)

    return [sentences[i] for i in selected_idx]


# ---------------- Main Summarization Function ----------------
def summarize(text, top_n=5):

    sentences = sentence_split(text)
    sentences = remove_fillers(sentences)
    sentences = remove_same_adjacent_words(sentences)
    sentences = [s for s in sentences if is_valid(s)]

    if not sentences:
        return ["No meaningful content to summarize."]

    embeddings = get_embeddings(sentences)

    if len(embeddings) == 0:
        return ["Not enough data to summarize."]

    summary = mmr_summary(sentences, embeddings, top_n)

    return summary
