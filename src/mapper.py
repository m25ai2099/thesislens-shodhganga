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
        "than", "such", "each", "when", "over",
        "after", "before", "about", "through", "under",
        "while", "where", "there", "those", "both",
        "paper", "present", "proposed", "method", "approach",
        "work", "make", "made", "into", "only", "then",
        "three", "four", "five", "first", "second", "third",
        "however", "therefore", "thus", "hence", "further",
        "well", "high", "large", "small", "good", "many",
        "various", "significant", "important", "number",
        "total", "overall", "general", "specific", "given",
        "level", "type", "form", "case", "part", "same",
        "study", "studies", "paper", "papers", "show",
        "shows", "shown", "model", "models", "effect",
        "effects", "result", "results", "group", "groups",
        "value", "values", "score", "scores", "rate", "rates",
        "measure", "measures", "factor", "factors", "sample",
        "samples", "table", "figure", "section", "chapter"
    }
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return [w for w in words
            if len(w) >= min_length and w not in stop_words]


def get_top_concepts(df, top_n=30):
    """Get most frequent concepts across all abstracts."""
    # Safety check for empty dataframe
    if df is None or len(df) == 0:
        return []

    all_words = []
    for abstract in df["abstract"].dropna():
        if abstract and len(str(abstract)) > 20:
            all_words.extend(extract_keywords(str(abstract)))

    if not all_words:
        return []

    return Counter(all_words).most_common(top_n)


def get_concept_cooccurrence(df, top_n=20):
    """Find concepts that appear together frequently."""
    # Safety check for empty dataframe
    if df is None or len(df) == 0:
        return pd.DataFrame()

    top_concepts = [w for w, _ in get_top_concepts(df, top_n)]

    if not top_concepts:
        return pd.DataFrame()

    cooccurrence = pd.DataFrame(
        0,
        index=top_concepts,
        columns=top_concepts
    )

    for abstract in df["abstract"].dropna():
        if not abstract or len(str(abstract)) < 20:
            continue
        words = set(extract_keywords(str(abstract)))
        present = [w for w in top_concepts if w in words]
        for i, w1 in enumerate(present):
            for w2 in present[i + 1:]:
                cooccurrence.loc[w1, w2] += 1
                cooccurrence.loc[w2, w1] += 1

    return cooccurrence


def get_discipline_concepts(df, discipline, top_n=20):
    """
    Get top concepts for a specific discipline.
    Used for cross-discipline comparison.
    """
    if df is None or len(df) == 0:
        return []

    disc_df = df[df["discipline"] == discipline]
    if len(disc_df) == 0:
        return []

    return get_top_concepts(disc_df, top_n)


def compare_disciplines(df, disciplines=None, top_n=15):
    """
    Compare top concepts across multiple disciplines.
    Returns a DataFrame with disciplines as columns
    and concepts as rows — useful for heatmap comparison.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()

    if disciplines is None:
        disciplines = df["discipline"].unique().tolist()

    all_concepts = set()
    disc_concepts = {}

    for disc in disciplines:
        concepts = get_discipline_concepts(df, disc, top_n)
        disc_concepts[disc] = dict(concepts)
        all_concepts.update(dict(concepts).keys())

    if not all_concepts:
        return pd.DataFrame()

    # Build comparison matrix
    comparison = pd.DataFrame(
        index=list(all_concepts),
        columns=disciplines
    ).fillna(0)

    for disc, concepts in disc_concepts.items():
        for concept, freq in concepts.items():
            comparison.loc[concept, disc] = freq

    # Sort by total frequency
    comparison["total"] = comparison.sum(axis=1)
    comparison = comparison.sort_values(
        "total", ascending=False
    ).drop(columns="total")

    return comparison.head(top_n)