import streamlit as st

st.set_page_config(
    page_title="ThesisLens — Shodhganga",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔬 ThesisLens — Shodhganga Intelligence Platform")
st.markdown("*Unlocking knowledge from Indian doctoral thesis corpora*")
st.markdown("---")

# Load data just to get stats
from src.data_loader import load_data
df = load_data()

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Theses Indexed", f"{len(df):,}")
with col2:
    st.metric("Universities", f"{df['institution'].nunique():,}")
with col3:
    has_abstract = df['abstract'].str.len().gt(50).sum()
    st.metric("With Abstracts", f"{has_abstract:,}")
with col4:
    st.metric("Years Covered", 
              f"{int(df['year'].min())}–{int(df['year'].max())}")

st.markdown("---")
st.subheader("Available Tools")

col1, col2 = st.columns(2)
with col1:
    st.info("""
    **🔍 Semantic Search**
    
    Search Shodhganga theses by meaning not just 
    keywords. Powered by SPECTER2 and FAISS.
    
    → Use the sidebar to navigate
    """)
    st.success("""
    **🔁 Duplication Detector**
    
    Paste a PhD synopsis and check similarity 
    against existing theses. Helps avoid 
    redundant research before registration.
    
    → Use the sidebar to navigate
    """)

with col2:
    st.warning("""
    **📊 Bibliometric Analysis**
    
    Explore research output trends across 
    universities, subjects, years and languages 
    in Indian doctoral research.
    
    → Use the sidebar to navigate
    """)
    st.error("""
    **🗺️ Variable Mapping**
    
    Visualise key concepts and methods being 
    studied across the Shodhganga corpus. 
    Maps the intellectual landscape.
    
    → Use the sidebar to navigate
    """)

st.markdown("---")
st.caption("ThesisLens | IIT Jodhpur M.Tech Dissertation | Chaitanya Mahajan | M25AI2099")