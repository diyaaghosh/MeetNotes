from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
# import nltk

# # Download punkt tokenizer once
# nltk.download("punkt")

def get_summary(text, top_n=5):
    """
    Summarize text offline using TF-IDF ranking.
    Returns top_n sentences as summary.
    """
    sentences = sent_tokenize(text)
    if len(sentences) <= top_n:
        return " ".join(sentences)

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    # Rank sentences by sum of TF-IDF scores
    scores = X.sum(axis=1)
    # Convert matrix to 1D numpy array and argsort
    scores_arr = scores.A1 if hasattr(scores, 'A1') else scores.toarray().ravel()
    ranked_idx = scores_arr.argsort()[::-1]

    # Return top_n sentences as a single string
    ranked_sentences = [sentences[int(i)] for i in ranked_idx[:top_n]]
    return " ".join(ranked_sentences)