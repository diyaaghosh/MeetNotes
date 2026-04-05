import nltk
import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
model = SentenceTransformer('all-mpnet-base-v2') 

def sentence_split(text):
    return nltk.sent_tokenize(text)
def remove_fillers(sentences):
    fillers = set(["um", "uh", "like", "you know", "so", "actually", "basically"])
    return [s for s in sentences if not any(f in s.lower() for f in fillers)]
def remove_same_adjacent_words(sentences):
    cleaned = []
    for s in sentences:
        words = s.split()
        cleaned.append(" ".join([w for i, w in enumerate(words) if i == 0 or w != words[i-1]]))
    return cleaned
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
def get_embeddings(sentences):
    return model.encode(sentences)
def is_diverse(embeddings, threshold=0.65):
    if len(embeddings) == 0:
        return False  
    sim_matrix = cosine_similarity(embeddings)
    avg_sim = np.mean(sim_matrix)
    return avg_sim < threshold
def textrank(indexed_sentences, embeddings, top_n):
    sentences = [s for _, s in indexed_sentences]

    sim_matrix = cosine_similarity(embeddings)
    graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(graph)

    boosted = []

    for i, (idx, sent) in enumerate(indexed_sentences):
        score = scores[i]

        if "discuss" in sent.lower() or "topic" in sent.lower():
            score += 0.3

        score += len(sent.split()) * 0.01

    
        if sent.endswith("?"):
            score -= 0.5

        if len(sent.split()) < 4:
            score -= 0.3

        boosted.append((score, (idx, sent)))

    ranked = sorted(boosted, reverse=True)

    return [sent for _, sent in ranked[:top_n]]
def mmr_summary(sentences, embeddings, top_n, lambda_param=0.7):
    selected_idx = []

    centroid = np.mean(embeddings, axis=0)

    for _ in range(min(top_n, len(sentences))):
        mmr_scores = []

        for i in range(len(sentences)):
            if i in selected_idx:
                continue

            relevance = cosine_similarity(
                [embeddings[i]], [centroid]
            )[0][0]

            if not selected_idx:
                diversity = 0
            else:
                diversity = max(
                    cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                    for j in selected_idx
                )

            score = (
                lambda_param * relevance
                - (1 - lambda_param) * diversity
            )

            mmr_scores.append((score, i))

        best = max(mmr_scores)[1]
        selected_idx.append(best)

    return [sentences[i] for i in selected_idx]
def summarize(text, top_n=5):
    sentences = sentence_split(text)
    sentences = remove_fillers(sentences)
    sentences = remove_same_adjacent_words(sentences)

    
    sentences = [s for s in sentences if is_valid(s)]

    if not sentences:
        return ["No meaningful content to summarize."]

    indexed_sentences = list(enumerate(sentences))
    embeddings = get_embeddings(sentences)

    if len(embeddings) == 0:
        return ["Not enough data to summarize."]


    summary = mmr_summary(indexed_sentences, embeddings, top_n)


    summary = sorted(summary, key=lambda x: x[0])
    summary = [s for _, s in summary]

    return summary