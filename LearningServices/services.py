# tasks.py
from rq import get_current_job
from django_rq import job
from collections import Counter
import re
import redis
import string
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np
from django.conf import settings
from LearningAPI.models.help import RequestQuery
from LearningAPI.utils import get_redis_connection

transformer_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
redis_cache = get_redis_connection()

@job
def process_queries():
    # Connect to Redis
    # print('Process queries job started')
    # try:
    #     redis_cache = get_redis_connection()
    # except redis.exceptions.ConnectionError as e:
    #     print(f'Error connecting to Redis: {e}')
    #     return

    # Get all queries
    queries = RequestQuery.objects.filter(helpful_request__isnull=False).values_list('query', flat=True)

    # Tokenize and remove stop words
    stop_words = set(stopwords.words('english'))
    punctuation = set(string.punctuation)
    all_stop_words = stop_words.union(punctuation)

    tokens = [word for query in queries for word in word_tokenize(query.lower()) if word not in all_stop_words]

    # Count frequencies
    word_counts = Counter(tokens)

    # Get the most common words
    common_words = word_counts.most_common(settings.HELP_COMMON_TERMS_LIMIT)

    # Find phrases containing these common words
    patterns = []
    seen_sentences = set()
    for word, _ in common_words:
        # Define a pattern to capture the entire sentence containing the word
        sentence_pattern = re.compile(r'([^.?!]*\b' + re.escape(word) + r'\b[^.?!]*[.?!])', re.IGNORECASE)
        matches = [sentence_pattern.search(query).group() for query in queries if sentence_pattern.search(query)]
        for match in matches:
            if match not in seen_sentences:
                seen_sentences.add(match)
                patterns.append(match)

    # Generate sentence embeddings
    embeddings = transformer_model.encode(patterns)

    # Apply DBSCAN clustering
    clustering = DBSCAN(eps=0.3, min_samples=1, metric='cosine').fit(embeddings)
    unique_patterns = []
    for cluster_label in set(clustering.labels_):
        if cluster_label != -1:  # Ignore noise points
            cluster_indices = np.where(clustering.labels_ == cluster_label)[0]
            representative_index = cluster_indices[0]
            unique_patterns.append(patterns[representative_index])


    redis_cache.set('search_results', json.dumps(unique_patterns[:settings.POPULAR_QUERIES_LIMIT]))
