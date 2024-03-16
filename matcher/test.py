import random
import string
from regex_matcher import PyRegexMatcher
import time

start = time.time()
# Generate 10,000 sentences with 25 words per sentence
sentences = [' '.join([''.join(random.choices(string.ascii_lowercase, k=random.randint(1, 10))) for _ in range(25)]) for
             _ in range(15000)]

# Generate 10,000 random regex patterns
patterns = [r'\b{}\b'.format(''.join(random.choices(string.ascii_lowercase, k=random.randint(1, 5)))) for _ in
            range(1500)]

# Combine sentences into a single text and encode as bytes
text = ' '.join(sentences).encode('utf-8')

# Encode patterns as bytes
patterns = [pattern.encode('utf-8') for pattern in patterns]

# Create PyRegexMatcher instance and perform matching
matcher = PyRegexMatcher(text, patterns)
matcher.match()
print(time.time() - start)
