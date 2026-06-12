import re
import numpy as np
import networkx as nx

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sent_tokenize(text):
    return [
        s.strip()
        for s in re.split(r'(?<=[.!?])\s+', text)
        if s.strip()
    ]


def preprocess_sentences(sentences):
    cleaned = []

    noise_phrases = {
        "hello",
        "hi",
        "can you hear me",
        "am i audible",
        "are you audible",
        "good morning",
        "good evening"
    }

    for sentence in sentences:
        s = sentence.strip()

        if len(s.split()) < 5:
            continue

        lower = s.lower()

        if any(noise in lower for noise in noise_phrases):
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

    summary = [sentences[i] for i in selected_indices]

    return summary


def extract_key_points(summary):
    bullets = []

    for sentence in summary:
        sentence = sentence.strip()

        if sentence.endswith("."):
            sentence = sentence[:-1]

        bullets.append(sentence)

    return bullets
