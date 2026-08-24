import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.data_loader import load_data
from src.mapper import get_top_concepts, get_concept_cooccurrence

st.set_page_config(page_title="Variable Map",
                   page_icon="🗺️", layout="wide")
st.title("🗺️ Variable Mapping")
st.markdown("Visualise researched concepts across the Shodhganga corpus")
st.markdown("---")

df = load_data()

# Top concepts bar chart
st.subheader("Most Researched Concepts")
top_n = st.slider("Number of concepts to show", 10, 50, 25)
concepts = get_top_concepts(df, top_n)
concept_df = pd.DataFrame(concepts, columns=["Concept", "Frequency"])

fig = px.bar(concept_df, x="Frequency", y="Concept",
             orientation="h",
             title=f"Top {top_n} concepts across Shodhganga abstracts",
             color="Frequency",
             color_continuous_scale="teal")
fig.update_layout(yaxis=dict(autorange="reversed"), height=600)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Co-occurrence heatmap
st.subheader("Concept Co-occurrence Map")
st.markdown("Shows which research concepts appear together frequently")

top_for_heatmap = st.slider("Concepts for heatmap", 5, 20, 10)
cooc = get_concept_cooccurrence(df, top_for_heatmap)

fig2 = px.imshow(cooc,
                 title="Concept co-occurrence heatmap",
                 color_continuous_scale="Blues",
                 aspect="auto")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Subject distribution pie
st.subheader("Subject Distribution")
subjects = df["subjects"].str.split(", ").explode()
subject_counts = subjects.value_counts().head(10).reset_index()
subject_counts.columns = ["Subject", "Count"]

fig3 = px.pie(subject_counts, values="Count", names="Subject",
              title="Top 10 subjects in Shodhganga corpus",
              color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(fig3, use_container_width=True)