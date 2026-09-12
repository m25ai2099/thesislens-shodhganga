import streamlit as st

st.set_page_config(
    page_title="Semantic Search",
    page_icon="🔍",
    layout="wide"
)

from src.sidebar import render_sidebar
from src.data_loader import load_data
from src.searcher import search

df = load_data()
filtered_df = render_sidebar(df=df, show_filters=True)

# Pre-fill discipline from bibliometrics click
if "selected_discipline" in st.session_state:
    st.info(f"🔗 Filtered by: "
            f"**{st.session_state['selected_discipline']}**")

st.title("🔍 Semantic Search")
st.markdown("Search Shodhganga theses by meaning — not just keywords")
st.markdown("---")

# Show active filter summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Theses in filter", f"{len(filtered_df):,}")
with col2:
    st.metric("Disciplines",
              f"{filtered_df['discipline'].nunique():,}")
with col3:
    if len(filtered_df) > 0:
        st.metric("Year range",
                  f"{int(filtered_df['year'].min())}–"
                  f"{int(filtered_df['year'].max())}")

st.markdown("---")

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
    if len(filtered_df) == 0:
        st.warning("No theses match your filters. "
                   "Try adjusting the discipline or year range.")
    else:
        with st.spinner("Searching..."):
            results = search(query, filtered_df, top_k=top_k)

        st.markdown(
            f"**Top {len(results)} results for:** *{query}*"
        )
        st.markdown("---")

        for i, r in enumerate(results, 1):
            with st.expander(
                f"{i}. {r['title'][:100]}  —  Score: {r['score']}"
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
                st.markdown(f"**Subjects:** {r['subjects']}")
                st.markdown(f"**Abstract:** {r['abstract']}")

elif search_btn and not query:
    st.warning("Please enter a search query.")