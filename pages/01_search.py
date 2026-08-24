import streamlit as st
from src.data_loader import load_data
from src.searcher import search

st.set_page_config(page_title="Semantic Search", page_icon="🔍", layout="wide")
st.title("🔍 Semantic Search")
st.markdown("Search Shodhganga theses by meaning — not just keywords")
st.markdown("---")

df = load_data()

query = st.text_input(
    "Enter your search query",
    placeholder="e.g. machine learning for disease detection in India"
)

col1, col2 = st.columns([1, 4])
with col1:
    top_k = st.slider("Results to show", 3, 20, 5)
with col2:
    search_btn = st.button("🔍 Search", type="primary")

if search_btn and query:
    with st.spinner("Searching..."):
        results = search(query, df, top_k=top_k)

    st.markdown(f"**Top {len(results)} results for:** *{query}*")
    st.markdown("---")

    for i, r in enumerate(results, 1):
        with st.expander(f"{i}. {r['title'][:100]}  —  Score: {r['score']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Author:** {r['author']}")
            with col2:
                st.markdown(f"**Institution:** {r['institution']}")
            with col3:
                st.markdown(f"**Year:** {r['year']}")
            st.markdown(f"**Subjects:** {r['subjects']}")
            st.markdown(f"**Abstract:** {r['abstract']}")