import streamlit as st
import plotly.express as px
from src.sidebar import render_sidebar
from src.data_loader import load_data
from src.bibliometrics import by_year, by_institution, by_subject

st.set_page_config(page_title="Bibliometrics", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Bibliometric Analysis")
st.markdown("Research output trends across Indian universities and subjects")
st.markdown("---")

df = load_data()

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Theses", f"{len(df):,}")
with col2:
    st.metric("Universities", f"{df['institution'].nunique():,}")
with col3:
    st.metric("Year Range",
              f"{int(df['year'].min())}–{int(df['year'].max())}")
with col4:
    st.metric("Subjects Covered",
              f"{df['subjects'].str.split(', ').explode().nunique():,}")

st.markdown("---")

# Theses by year
st.subheader("Theses by Year")
year_data = by_year(df).reset_index()
year_data.columns = ["Year", "Count"]
fig = px.line(year_data, x="Year", y="Count",
              title="Shodhganga: Thesis output over time",
              markers=True, color_discrete_sequence=["teal"])
st.plotly_chart(fig, use_container_width=True)

# Top institutions
st.subheader("Top Universities")
inst_data = by_institution(df, 15).reset_index()
inst_data.columns = ["Institution", "Count"]
fig2 = px.bar(inst_data, x="Count", y="Institution",
              orientation="h",
              title="Top 15 universities by thesis count",
              color_discrete_sequence=["steelblue"])
fig2.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig2, use_container_width=True)

# Top subjects
st.subheader("Top Research Subjects")
subj_data = by_subject(df, 15).reset_index()
subj_data.columns = ["Subject", "Count"]
fig3 = px.bar(subj_data, x="Count", y="Subject",
              orientation="h",
              title="Top 15 subjects in Shodhganga corpus",
              color_discrete_sequence=["navy"])
fig3.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig3, use_container_width=True)