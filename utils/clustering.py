import numpy as np
import pandas as pd
import openai
import umap
import hdbscan
from sklearn.feature_extraction.text import CountVectorizer
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_embeddings(texts, model="text-embedding-ada-002"):
    
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = openai.Embedding.create(input=batch, model=model)
        batch_embeddings = [item["embedding"] for item in response["data"]]
        all_embeddings.extend(batch_embeddings)
    
    return np.array(all_embeddings)
def cluster_comments(comments_df, min_cluster_size=10):
    
    texts = comments_df['text'].tolist()
    embeddings = get_embeddings(texts)
    
    umap_embeddings = umap.UMAP(
        n_neighbors=15,
        n_components=5,
        metric='cosine'
    ).fit_transform(embeddings)
    
    cluster = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom'
    ).fit(umap_embeddings)
    
    comments_df = comments_df.copy()
    comments_df['cluster'] = cluster.labels_
    
    cluster_summaries = {}
    for cluster_id in set(cluster.labels_):
        if cluster_id == -1:
            continue
        cluster_texts = comments_df[comments_df['cluster'] == cluster_id]['text'].tolist()
        cluster_summaries[cluster_id] = " ".join(cluster_texts)
    
    return comments_df, cluster_summaries

def analyze_sentiment(comments_df):

    def get_sentiment(text):
        negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'not']
        score = sum(word in text.lower() for word in negative_words)
        return -score if score > 0 else 0
    
    comments_df = comments_df.copy()
    comments_df['sentiment'] = comments_df['text'].apply(get_sentiment)
    
    return comments_df

def get_negative_comments(comments_df, threshold=-1):
    
    return comments_df[comments_df['sentiment'] <= threshold]
