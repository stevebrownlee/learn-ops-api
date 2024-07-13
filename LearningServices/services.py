# Module to hold all Redis Queue jobs
import re
import logging
import string
import json
import numpy as np
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from django.conf import settings

from LearningAPI.models.help import RequestQuery
from LearningServices.utils import get_redis_connection

transformer_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
redis_connection = get_redis_connection()
logger = logging.getLogger("LearningPlatform")

def process_queries():
    try:

        # Get all queries
        logger.debug("Starting process_queries job.")
        queries = RequestQuery.objects.filter(helpful_request__isnull=False).values_list('query', flat=True)

        # Tokenize and remove stop words
        stop_words = set(stopwords.words('english'))
        punctuation = set(string.punctuation)
        all_stop_words = stop_words.union(punctuation)

        tokens = [word for query in queries for word in word_tokenize(query.lower()) if word not in all_stop_words]
        logger.debug("Generated tokens.")

        # Count frequencies
        word_counts = Counter(tokens)

        # Get the most common words
        common_words = word_counts.most_common(settings.HELP_COMMON_TERMS_LIMIT)
        logger.debug("Found common words.")

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
        logger.debug("Found top sentence patterns.")

        # Generate sentence embeddings
        logger.debug("START: Encoding the patterns with the transformer model.")
        logger.debug("      patterns: %s", patterns)
        logger.debug("      transformer_model: %s", transformer_model)
        embeddings = transformer_model.encode(patterns, batch_size=8)
        logger.debug("END: Encoded the patterns with the transformer model.")

        # Apply DBSCAN clustering
        logger.debug("START: Create instance of DBSCAN()")
        scan = DBSCAN(eps=0.3, min_samples=1, metric='cosine')
        logger.debug("END: Created instance of DBSCAN()")

        logger.debug("START: Performing DBSCAN clustering.")
        clustering = scan.fit(embeddings)
        logger.debug("END: Performed DBSCAN clustering.")

        unique_patterns = []
        for cluster_label in set(clustering.labels_):
            if cluster_label != -1:  # Ignore noise points
                cluster_indices = np.where(clustering.labels_ == cluster_label)[0]
                representative_index = cluster_indices[0]
                unique_patterns.append(patterns[representative_index])
        logger.debug("Extracted unique patterns.")

        redis_connection.set('search_results', json.dumps(unique_patterns[:settings.POPULAR_QUERIES_LIMIT]))
        logger.debug("Stored results in Redis.")

    except Exception as e:
        logger.debug(f"Error in process_queries job: {e}", exc_info=True)