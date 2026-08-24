import streamlit as st
from src.data_loader import load_data
from src.duplicator import check_duplicate

st.set_page_config(page_title="Duplication Detector",
                   page_icon="🔁", layout="wide")
st.title("🔁 Duplication Detector")
st.markdown("Check if your proposed thesis topic already exists in Shodhganga")
st.markdown("---")

df = load_data()

st.info("""
**How to use:** Paste your proposed PhD synopsis or research description 
below. ThesisLens will find the most similar existing theses and flag 
potential duplication.
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
    with st.spinner("Checking against Shodhganga corpus..."):
        results = check_duplicate(
            synopsis, df,
            top_k=5,
            threshold=threshold/100
        )

    # Summary
    duplicates = [r for r in results if r["is_duplicate"]]
    if duplicates:
        st.error(f"⚠️ {len(duplicates)} potentially duplicate thesis/theses found above {threshold}% similarity")
    else:
        st.success(f"✅ No duplicates found above {threshold}% threshold — topic appears original")

    st.markdown("---")
    st.subheader("Most Similar Existing Theses")

    for i, r in enumerate(results, 1):
        color = "🔴" if r["is_duplicate"] else "🟢"
        with st.expander(
            f"{color} {i}. {r['title'][:90]} — {r['similarity']}% similar"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Author:** {r['author']}")
            with col2:
                st.markdown(f"**Institution:** {r['institution']}")
            with col3:
                st.markdown(f"**Year:** {r['year']}")
            st.markdown(f"**Abstract:** {r['abstract']}")
            st.progress(r["similarity"] / 100)