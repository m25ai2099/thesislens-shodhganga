import streamlit as st

st.set_page_config(
    page_title="Bibliometrics",
    page_icon="📊",
    layout="wide"
)

import plotly.express as px
from src.sidebar import render_sidebar
from src.data_loader import load_data
from src.bibliometrics import by_year, by_institution, by_subject

df = load_data()
filtered_df = render_sidebar(df=df, show_filters=True)

st.title("📊 Bibliometric Analysis")
st.markdown("Research output trends across Indian universities and subjects")
st.markdown("---")

if len(filtered_df) == 0:
    st.warning("No theses match your filters — try adjusting them.")
    st.stop()

# Stats — use filtered_df
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Theses", f"{len(filtered_df):,}")
with col2:
    st.metric("Universities",
              f"{filtered_df['institution'].nunique():,}")
with col3:
    st.metric("Year Range",
              f"{int(filtered_df['year'].min())}–"
              f"{int(filtered_df['year'].max())}")
with col4:
    st.metric("Disciplines",
              f"{filtered_df['discipline'].nunique():,}")

st.markdown("---")

# Year chart
st.subheader("Theses by Year")
year_data = by_year(filtered_df).reset_index()
year_data.columns = ["Year", "Count"]
fig = px.line(year_data, x="Year", y="Count",
              title="Shodhganga: Thesis output over time",
              markers=True,
              color_discrete_sequence=["teal"])
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Universities
st.subheader("Top Universities")
inst_data = by_institution(filtered_df, 15).reset_index()
inst_data.columns = ["Institution", "Count"]
fig2 = px.bar(inst_data, x="Count", y="Institution",
              orientation="h",
              title="Top 15 universities by thesis count",
              color_discrete_sequence=["steelblue"])
fig2.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Discipline breakdown — clickable
st.subheader("Theses by Discipline")
disc_data = filtered_df["discipline"].value_counts().reset_index()
disc_data.columns = ["Discipline", "Count"]
fig3 = px.bar(disc_data, x="Count", y="Discipline",
              orientation="h",
              title="Thesis count by discipline — click a bar to explore",
              color="Count",
              color_continuous_scale="Blues")
fig3.update_layout(yaxis=dict(autorange="reversed"))

# Capture click event
selected = st.plotly_chart(fig3, use_container_width=True,
                           on_select="rerun",
                           key="discipline_chart")

# If user clicked a bar — store in session state
if selected and selected.get("selection", {}).get("points"):
    clicked_discipline = selected["selection"]["points"][0].get("y")
    if clicked_discipline:
        st.session_state["selected_discipline"] = clicked_discipline
        st.info(f"📚 Selected: **{clicked_discipline}** "
                f"— go to Variable Map to explore concepts")

st.markdown("---")

# Subjects
st.subheader("Top Research Subjects")
subj_data = by_subject(filtered_df, 15).reset_index()
subj_data.columns = ["Subject", "Count"]
fig4 = px.bar(subj_data, x="Count", y="Subject",
              orientation="h",
              title="Top 15 subjects in filtered corpus",
              color_discrete_sequence=["navy"])
fig4.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig4, use_container_width=True)