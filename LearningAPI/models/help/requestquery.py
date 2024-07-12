from django.db import models
from collections import Counter
import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import DBSCAN
import numpy as np

class RequestQueryManager(models.Manager):

    def get_common_patterns(self, limit=10):
        # Get all queries
        queries = self.filter(helpful_request__isnull=False).values_list('query', flat=True)

        # Tokenize and remove stop words
        stop_words = set(stopwords.words('english'))
        punctuation = set(string.punctuation)
        all_stop_words = stop_words.union(punctuation)

        tokens = [word for query in queries for word in word_tokenize(query.lower()) if word not in all_stop_words]

        # Count frequencies
        word_counts = Counter(tokens)

        # Get the most common words
        common_words = word_counts.most_common(limit)

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
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        embeddings = model.encode(patterns)

        # Apply DBSCAN clustering
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine').fit(embeddings)
        unique_patterns = []
        for cluster_label in set(clustering.labels_):
            if cluster_label != -1:  # Ignore noise points
                cluster_indices = np.where(clustering.labels_ == cluster_label)[0]
                representative_index = cluster_indices[0]
                unique_patterns.append(patterns[representative_index])

        return unique_patterns[:limit]

class RequestQuery(models.Model):
    query = models.TextField(null=False, blank=False)
    searcher = models.ForeignKey('NSSUser', on_delete=models.CASCADE, related_name='search_queries')
    helpful_request = models.ForeignKey('HelpRequest', on_delete=models.SET_NULL, null=True, blank=True)

    objects = RequestQueryManager()
