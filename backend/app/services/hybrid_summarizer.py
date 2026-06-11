import nltk
import os

nltk_data_path = "/opt/render/nltk_data"
os.makedirs(nltk_data_path, exist_ok=True)

nltk.data.path.append(nltk_data_path)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_path)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", download_dir=nltk_data_path)

def preprocess_sentences(sentences):
    fillers = {
        "um", "uh", "like", "you know",
        "actually", "basically", "okay", "ok"
    }

    cleaned = []

    for sentence in sentences:
        s = sentence.strip()

        if len(s.split()) < 5:
            continue

        lower = s.lower()

        if any(f in lower for f in fillers):
            continue

        cleaned.append(s)

    return cleaned


def rank_sentences(sentences):

    tfidf = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = tfidf.fit_transform(sentences)

    similarity_matrix = cosine_similarity(matrix)

    np.fill_diagonal(similarity_matrix, 0)

    graph = nx.from_numpy_array(similarity_matrix)

    scores = nx.pagerank(graph)

    return scores


def summarize(text, top_n=5):

    sentences = sent_tokenize(text)

    sentences = preprocess_sentences(sentences)

    if not sentences:
        return ["No meaningful content found."]

    if len(sentences) <= top_n:
        return sentences

    scores = rank_sentences(sentences)

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    selected_indices = sorted(
        [idx for idx, _ in ranked[:top_n]]
    )

    summary = [
        sentences[i]
        for i in selected_indices
    ]

    return summary


def extract_key_points(summary):

    key_points = []

    action_words = {
        "will",
        "should",
        "must",
        "need",
        "required",
        "deadline",
        "task",
        "action",
        "implement",
        "complete",
        "finish",
        "schedule",
        "assigned"
    }

    for sentence in summary:

        lower = sentence.lower()

        if any(word in lower for word in action_words):
            key_points.append("ACTION: " + sentence)
        else:
            key_points.append(sentence)

    return key_points
