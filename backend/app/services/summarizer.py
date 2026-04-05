from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
# # Download punkt tokenizer once
# nltk.download("punkt")
def get_summary(text, top_n=5):
    sentences = sent_tokenize(text)
    if len(sentences) <= top_n:
        return " ".join(sentences)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    scores = X.sum(axis=1)
    scores_arr = scores.A1 if hasattr(scores, 'A1') else scores.toarray().ravel()
    ranked_idx = scores_arr.argsort()[::-1]
    ranked_sentences = [sentences[int(i)] for i in ranked_idx[:top_n]]
    return " ".join(ranked_sentences)

# it gives low accuracy :(
