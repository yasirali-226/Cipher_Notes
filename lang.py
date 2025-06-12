# lang.py

import string
import random

# Generate a reproducible fixed shuffled alphabet
seed = 1234
random.seed(seed)
alphabet = list(string.ascii_lowercase)
shuffled = alphabet[:]
random.shuffle(shuffled)

# Mapping
ylang_map = dict(zip(alphabet, shuffled))
reverse_map = {v: k for k, v in ylang_map.items()}

def encrypt(text):
    return ''.join(ylang_map.get(c, c) for c in text.lower())

def decrypt(text):
    return ''.join(reverse_map.get(c, c) for c in text.lower())
