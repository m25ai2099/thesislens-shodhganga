import pandas as pd
from collections import Counter
import re

def extract_keywords(text, min_length=5):
    """Extract meaningful keywords from text."""
    stop_words = {
        # Common English words
        "this", "that", "with", "from", "have", "been",
        "were", "they", "their", "which", "study", "research",
        "using", "based", "analysis", "india", "indian",
        "data", "also", "used", "results", "found", "show",
        # Words appearing in abstracts but not meaningful
        "para", "these", "between", "chapter", "thesis",
        "different", "within", "among", "other", "more",
        "than", "such", "each", "than", "when", "over",
        "after", "before", "about", "through", "under",
        "while", "where", "there", "those", "both",
        "paper", "present", "proposed", "method", "approach",
        "work", "make", "made", "into", "only", "then",
        "three", "four", "five", "first", "second", "third",
        "however", "therefore", "thus", "hence", "further",
        "well", "high", "large", "small", "good", "many",
        "various", "significant", "important", "number",
        "total", "overall", "general", "specific", "given",
        "level", "type", "form", "case", "part", "same"
    }
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return [w for w in words
            if len(w) >= min_length and w not in stop_words]

def get_top_concepts(df, top_n=30):
    """Get most frequent concepts across all abstracts."""
    all_words = []
    for abstract in df["abstract"].dropna():
        all_words.extend(extract_keywords(abstract))
    return Counter(all_words).most_common(top_n)

def get_concept_cooccurrence(df, top_n=20):
    """Find concepts that appear together frequently."""
    top_concepts = [w for w, _ in get_top_concepts(df, top_n)]
    cooccurrence = pd.DataFrame(0,
                                index=top_concepts,
                                columns=top_concepts)
    for abstract in df["abstract"].dropna():
        words = set(extract_keywords(abstract))
        present = [w for w in top_concepts if w in words]
        for i, w1 in enumerate(present):
            for w2 in present[i+1:]:
                cooccurrence.loc[w1, w2] += 1
                cooccurrence.loc[w2, w1] += 1
    return cooccurrence