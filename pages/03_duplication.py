import streamlit as st

st.set_page_config(
    page_title="Duplication Detector",
    page_icon="🔁",
    layout="wide"
)

from src.sidebar import render_sidebar
from src.data_loader import load_data
from src.duplicator import check_duplicate

df = load_data()
filtered_df = render_sidebar(df=df, show_filters=True)

st.title("🔁 Duplication Detector")
st.markdown(
    "Check if your proposed thesis topic already exists in Shodhganga"
)
st.markdown("---")

st.info("""
**How to use:** Paste your proposed PhD synopsis or research
description below. ThesisLens will find the most similar existing
theses and flag potential duplication.
""")

synopsis = st.text_area(
    "Paste your proposed PhD synopsis here",
    height=200,
    placeholder="Enter your proposed research topic or synopsis..."
)

col1, col2 = st.columns([1, 3])
with col1:
    threshold = st.slider("Similarity threshold (%)", 50, 95, 85)
with col2:
    check_btn = st.button("🔁 Check for Duplicates", type="primary")

if check_btn and synopsis:
    if len(filtered_df) == 0:
        st.warning("No theses match your filters.")
    else:
        with st.spinner(
            f"Checking against {len(filtered_df):,} theses..."
        ):
            results = check_duplicate(
                synopsis, filtered_df,
                top_k=5,
                threshold=threshold / 100
            )

        duplicates = [r for r in results if r["is_duplicate"]]
        if duplicates:
            st.error(
                f"⚠️ {len(duplicates)} potentially duplicate "
                f"thesis/theses found above {threshold}% similarity"
            )
        else:
            st.success(
                f"✅ No duplicates found above {threshold}% — "
                f"topic appears original"
            )

        st.markdown("---")
        st.subheader("Most Similar Existing Theses")

        for i, r in enumerate(results, 1):
            color = "🔴" if r["is_duplicate"] else "🟢"
            with st.expander(
                f"{color} {i}. {r['title'][:90]} "
                f"— {r['similarity']}% similar"
            ):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**Author:** {r['author']}")
                with col2:
                    st.markdown(
                        f"**Institution:** {r['institution']}"
                    )
                with col3:
                    st.markdown(f"**Year:** {r['year']}")
                with col4:
                    st.markdown(f"**Discipline:** {r.get('discipline', 'N/A')}")
                st.markdown(f"**Abstract:** {r['abstract']}")
                st.progress(r["similarity"] / 100)

elif check_btn and not synopsis:
    st.warning("Please paste a synopsis first.")