import pandas as pd

def get_stats(df):
    return {
        "total":       len(df),
        "universities": df["institution"].nunique(),
        "years":       f"{int(df['year'].min())}–{int(df['year'].max())}",
        "with_abstract": df["abstract"].str.len().gt(50).sum()
    }

def by_year(df):
    return df["year"].value_counts().sort_index()

def by_institution(df, top_n=15):
    return df["institution"].value_counts().head(top_n)

def by_subject(df, top_n=15):
    subjects = df["subjects"].str.split(", ").explode()
    return subjects.value_counts().head(top_n)