from django.db import models
from collections import Counter
import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

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
        for word, _ in common_words:
            pattern = re.compile(r'\b\w+\s+\w+\s+' + re.escape(word) + r'\s+\w+\s+\w+\b', re.IGNORECASE)
            matches = [pattern.search(query).group() for query in queries if pattern.search(query)]
            if matches:
                patterns.append(Counter(matches).most_common(1)[0][0])

        return patterns[:limit]

class RequestQuery(models.Model):
    query = models.TextField(null=False, blank=False)
    searcher = models.ForeignKey('NSSUser', on_delete=models.CASCADE, related_name='search_queries')
    helpful_request = models.ForeignKey('HelpRequest', on_delete=models.SET_NULL, null=True, blank=True)

    objects = RequestQueryManager()
