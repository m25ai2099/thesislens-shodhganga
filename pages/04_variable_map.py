import streamlit as st

st.set_page_config(
    page_title="Variable Map",
    page_icon="🗺️",
    layout="wide"
)

import plotly.express as px
import pandas as pd
from src.sidebar import render_sidebar
from src.data_loader import load_data
from src.mapper import get_top_concepts, get_concept_cooccurrence

df = load_data()
filtered_df = render_sidebar(df=df, show_filters=True)

st.title("🗺️ Variable Mapping")
st.markdown("Visualise researched concepts across the Shodhganga corpus")
st.markdown("---")

# ── Check if discipline was clicked from Bibliometrics ──
if "selected_discipline" in st.session_state:
    auto_disc = st.session_state["selected_discipline"]

    col1, col2 = st.columns([4, 1])
    with col1:
        st.success(f"🔗 Linked from Bibliometrics — "
                   f"showing concepts for: **{auto_disc}**")
    with col2:
        if st.button("❌ Clear"):
            del st.session_state["selected_discipline"]
            st.rerun()

    # Override filtered_df with clicked discipline
    filtered_df = filtered_df[
        filtered_df["discipline"] == auto_disc
    ].reset_index(drop=True)

if len(filtered_df) == 0:
    st.warning("No theses match your filters. "
               "Try adjusting discipline or year range.")
    st.stop()

# ── Stats ──
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Theses in view", f"{len(filtered_df):,}")
with col2:
    st.metric("Disciplines",
              f"{filtered_df['discipline'].nunique():,}")
with col3:
    if len(filtered_df) > 0:
        st.metric("Year range",
                  f"{int(filtered_df['year'].min())}–"
                  f"{int(filtered_df['year'].max())}")

st.markdown("---")

# ── Top concepts bar chart ──
st.subheader("Most Researched Concepts")
top_n = st.slider("Number of concepts to show", 10, 50, 25)

# Use filtered_df for concepts
concepts = get_top_concepts(filtered_df, top_n)

if not concepts:
    st.warning("Not enough abstract data to extract concepts "
               "for this filter.")
else:
    concept_df = pd.DataFrame(concepts,
                               columns=["Concept", "Frequency"])
    fig = px.bar(concept_df,
                 x="Frequency", y="Concept",
                 orientation="h",
                 title=f"Top {top_n} concepts — "
                       f"{filtered_df['discipline'].iloc[0] if filtered_df['discipline'].nunique() == 1 else 'filtered corpus'}",
                 color="Frequency",
                 color_continuous_scale="teal")
    fig.update_layout(yaxis=dict(autorange="reversed"), height=600)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Co-occurrence heatmap ──
st.subheader("Concept Co-occurrence Map")
st.markdown("Shows which research concepts appear together frequently")

top_for_heatmap = st.slider("Concepts for heatmap", 5, 20, 10)

# Use filtered_df for cooccurrence
cooc = get_concept_cooccurrence(filtered_df, top_for_heatmap)

if cooc.empty or cooc.sum().sum() == 0:
    st.warning("Not enough data for co-occurrence map "
               "with current filters.")
else:
    fig2 = px.imshow(cooc,
                     title="Concept co-occurrence heatmap",
                     color_continuous_scale="Blues",
                     aspect="auto")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Subject distribution pie ──
st.subheader("Subject Distribution")

# Use filtered_df for subjects
subjects = filtered_df["subjects"].str.split(", ").explode()
subjects = subjects[subjects.str.strip() != ""]
subject_counts = subjects.value_counts().head(10).reset_index()
subject_counts.columns = ["Subject", "Count"]

if len(subject_counts) == 0:
    st.warning("No subject data available for current filters.")
else:
    fig3 = px.pie(subject_counts,
                  values="Count",
                  names="Subject",
                  title="Top 10 subjects — filtered corpus",
                  color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── Discipline breakdown ──
st.subheader("Disciplines in View")
disc_counts = filtered_df["discipline"].value_counts().reset_index()
disc_counts.columns = ["Discipline", "Count"]

fig4 = px.bar(disc_counts,
              x="Discipline", y="Count",
              title="Thesis count by discipline — current filter",
              color="Count",
              color_continuous_scale="teal")
fig4.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig4, use_container_width=True)