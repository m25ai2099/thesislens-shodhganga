import requests
import pandas as pd
import time
import os
import random
from langdetect import detect, LangDetectException

DATA_PATH = "data/shodhganga.parquet"
CHECKPOINT_DIR = "data/checkpoints"

# 25 disciplines — proven to work
DISCIPLINES = [
    "computer science", "engineering", "medicine", "agriculture",
    "economics", "education", "chemistry", "physics", "biology",
    "sociology", "history", "law", "management", "psychology",
    "environmental science", "mathematics", "pharmacy", "nursing",
    "botany", "zoology", "political science", "geography",
    "linguistics", "biotechnology", "architecture"
]

# Only these languages allowed
ALLOWED_LANGS = ['en', 'hi', 'ta', 'te', 'mr', 'bn', 'gu', 'ur']

# Status codes worth retrying (transient server-side issues)
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

HEADERS = {"User-Agent": "ThesisLens-research-bot/1.0 (mailto:m25ai2099@iitj.ac.in)"}


def is_valid_language(text):
    """Check if text is in English or an Indian language."""
    try:
        lang = detect(text)
        return lang in ALLOWED_LANGS
    except LangDetectException:
        return True  # if detection fails, keep the record


def _request_with_retry(session, url, params, max_attempts=6, base_wait=10):
    """
    Single-page fetch with exponential backoff + jitter on any transient
    error (429 / 5xx / connection errors). Returns the Response on success,
    or None if every attempt failed.
    """
    wait_time = base_wait
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.get(url, params=params, headers=HEADERS, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"    Connection error: {e} — retrying in {wait_time:.0f}s "
                  f"(attempt {attempt}/{max_attempts})...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 120) + random.uniform(0, 3)
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code in RETRYABLE_STATUS:
            print(f"    HTTP {resp.status_code} — retrying in {wait_time:.0f}s "
                  f"(attempt {attempt}/{max_attempts})...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 120) + random.uniform(0, 3)
            continue

        # Non-retryable error (400, 401, 403, 404, ...) — no point retrying
        print(f"    Non-retryable error {resp.status_code}: {resp.text[:200]}")
        return None

    print(f"    Giving up after {max_attempts} attempts.")
    return None


def fetch_by_discipline(discipline, session, max_records=80,
                         email="m25ai2099@iitj.ac.in"):
    """
    Fetch Indian dissertations for one discipline.
    A failed page stops pagination for THIS discipline only — it no longer
    aborts with whatever was collected so far being silently discarded by
    the caller; results collected before the failure are still returned.
    """
    results = []
    cursor = "*"
    per_page = 25
    skipped = 0

    while len(results) < max_records:
        url = "https://api.openalex.org/works"
        params = {
            "filter": "institutions.country_code:IN,type:dissertation",
            "search": discipline,
            "per_page": per_page,
            "cursor": cursor,
            "mailto": email,
            "select": "id,title,abstract_inverted_index,"
                      "publication_year,authorships,concepts,doi"
        }

        response = _request_with_retry(session, url, params)
        if response is None:
            # Stop paginating this discipline, but keep what we already have.
            break

        data = response.json()
        items = data.get("results", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "")
            if not title or len(title) < 10:
                skipped += 1
                continue
            if not is_valid_language(title):
                skipped += 1
                continue

            abstract = ""
            inv_index = item.get("abstract_inverted_index")
            if inv_index:
                word_positions = []
                for word, positions in inv_index.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join(w for _, w in word_positions)

            authorships = item.get("authorships", [])
            author = ""
            institution = ""
            if authorships:
                author = authorships[0]["author"]["display_name"]
                insts = authorships[0].get("institutions", [])
                if insts:
                    institution = insts[0].get("display_name", "")

            concepts = item.get("concepts", [])
            subjects = [c["display_name"] for c in concepts[:3]]

            results.append({
                "title": title,
                "abstract": abstract,
                "year": item.get("publication_year"),
                "author": author,
                "institution": institution,
                "subjects": ", ".join(subjects),
                "discipline": discipline.title(),
                "doi": item.get("doi", ""),
                "openalex_id": item.get("id", ""),
            })

            if len(results) >= max_records:
                break

        meta = data.get("meta", {})
        cursor = meta.get("next_cursor")
        if not cursor:
            break

        time.sleep(2)  # polite gap between successful pages

    return results, skipped


def fetch_all(email="m25ai2099@iitj.ac.in", resume=True):
    """
    Fetch across all disciplines, checkpointing after each one so a crash
    or a stubborn 503 run doesn't cost you the whole session.
    """
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    all_results = []
    total_skipped = 0

    # Reuse one TCP connection (faster, fewer handshake-related failures)
    session = requests.Session()

    for i, discipline in enumerate(DISCIPLINES, 1):
        ckpt_path = os.path.join(CHECKPOINT_DIR, f"{discipline.replace(' ', '_')}.parquet")

        if resume and os.path.exists(ckpt_path):
            records_df = pd.read_parquet(ckpt_path)
            records = records_df.to_dict("records")
            print(f"[{i}/{len(DISCIPLINES)}] {discipline}: loaded {len(records)} "
                  f"from checkpoint (skipping fetch)")
            all_results.extend(records)
            continue

        print(f"[{i}/{len(DISCIPLINES)}] Fetching: {discipline}...")
        records, skipped = fetch_by_discipline(discipline, session, max_records=80, email=email)
        all_results.extend(records)
        total_skipped += skipped

        print(f"  → {len(records)} clean records (skipped {skipped}) | "
              f"total so far: {len(all_results)}")

        # Checkpoint this discipline immediately, even if it came back short.
        pd.DataFrame(records).to_parquet(ckpt_path) if records else None

        time.sleep(5)  # gap between disciplines

    print(f"\nTotal skipped (foreign/invalid): {total_skipped}")

    if not all_results:
        print("No results — OpenAlex may still be having issues.")
        return pd.DataFrame(columns=[
            "title", "abstract", "year", "author", "institution",
            "subjects", "discipline", "doi", "openalex_id"
        ])

    df = pd.DataFrame(all_results)
    df = df.drop_duplicates(subset="openalex_id")
    df = df.dropna(subset=["title"])
    df = df[df["title"].str.len() > 10]
    df = df.reset_index(drop=True)

    return df


def load_data(force_refresh=False):
    if os.path.exists(DATA_PATH) and not force_refresh:
        return pd.read_parquet(DATA_PATH)

    if not force_refresh:
        raise FileNotFoundError(
            f"No data file at {DATA_PATH}. Run: python src/data_loader.py"
        )

    df = fetch_all()
    if len(df) > 0:
        os.makedirs("data", exist_ok=True)
        df.to_parquet(DATA_PATH)
        print(f"Saved {len(df)} records to {DATA_PATH}")
    return df


if __name__ == "__main__":
    # NOTE: checkpoints let you re-run this safely — disciplines already
    # saved in data/checkpoints/ will be loaded instantly instead of
    # re-fetched. Delete data/checkpoints/ (not just the final parquet)
    # if you want a fully clean re-run.
    print("Waiting 30s before starting to avoid rate limits...")
    time.sleep(30)

    df = fetch_all(resume=True)

    if len(df) == 0:
        print("No data fetched. Check data/checkpoints/ for partial results, "
              "or try again shortly.")
    else:
        os.makedirs("data", exist_ok=True)
        df.to_parquet(DATA_PATH)

        print(f"\n{'='*50}")
        print(f"DATASET READY")
        print(f"{'='*50}")
        print(f"Total records:  {len(df):,}")
        print(f"Year range:     {int(df['year'].min())} – {int(df['year'].max())}")
        print(f"\nDiscipline breakdown:")
        print(df["discipline"].value_counts().to_string())