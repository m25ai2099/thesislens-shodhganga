import requests
import pandas as pd
import time
import os

DATA_PATH = "data/shodhganga.parquet"

def fetch_shodhganga_openalex(max_results=500, email="m25ai2099@iitj.ac.in"):
    """
    Fetch Indian dissertation metadata from OpenAlex.
    Includes titles, abstracts, authors, years, institutions.
    """
    results = []
    cursor = "*"
    per_page = 50

    print(f"Fetching up to {max_results} records from OpenAlex...")

    while len(results) < max_results:
        url = "https://api.openalex.org/works"
        params = {
            "filter": "institutions.country_code:IN,type:dissertation",
            "per_page": per_page,
            "cursor": cursor,
            "mailto": email,
            "select": "id,title,abstract_inverted_index,publication_year,authorships,concepts,doi,primary_location"
        }

        r = requests.get(url, params=params, timeout=30)

        if r.status_code != 200:
            print(f"Error: {r.status_code}")
            break

        data = r.json()
        items = data.get("results", [])

        if not items:
            break

        for item in items:
            # Reconstruct abstract from inverted index
            abstract = ""
            inv_index = item.get("abstract_inverted_index")
            if inv_index:
                word_positions = []
                for word, positions in inv_index.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join(w for _, w in word_positions)

            # Get author and institution
            authorships = item.get("authorships", [])
            author = ""
            institution = ""
            if authorships:
                author = authorships[0]["author"]["display_name"]
                insts = authorships[0].get("institutions", [])
                if insts:
                    institution = insts[0].get("display_name", "")

            # Get concepts/subjects
            concepts = item.get("concepts", [])
            subjects = [c["display_name"] for c in concepts[:3]]

            results.append({
                "title":       item.get("title", ""),
                "abstract":    abstract,
                "year":        item.get("publication_year"),
                "author":      author,
                "institution": institution,
                "subjects":    ", ".join(subjects),
                "doi":         item.get("doi", ""),
                "openalex_id": item.get("id", ""),
            })

        print(f"  Fetched {len(results)} records so far...")

        # Next page cursor
        meta = data.get("meta", {})
        cursor = meta.get("next_cursor")
        if not cursor:
            break

        time.sleep(0.3)

    df = pd.DataFrame(results)
    return df


def load_data():
    """
    Load Shodhganga data — from cache if available,
    otherwise fetch from OpenAlex.
    """
    if os.path.exists(DATA_PATH):
        print(f"Loading cached data from {DATA_PATH}")
        return pd.read_parquet(DATA_PATH)

    print("No cache found — fetching from OpenAlex...")
    df = fetch_shodhganga_openalex(max_results=500)

    # Clean up
    df = df.dropna(subset=["title"])
    df = df[df["title"].str.len() > 5]
    df = df.reset_index(drop=True)

    # Save cache
    os.makedirs("data", exist_ok=True)
    df.to_parquet(DATA_PATH)
    print(f"Saved {len(df)} records to {DATA_PATH}")

    return df


if __name__ == "__main__":
    df = load_data()
    print(f"\nDataset ready: {len(df)} records")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nSample:")
    print(df.head(3))