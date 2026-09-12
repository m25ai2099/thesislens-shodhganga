import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0f1b2d;
            border-right: 1px solid #1e3a5f;
        }
        [data-testid="stSidebar"] * {
            color: #e0e0e0 !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stMetric"] {
            background-color: #0f1b2d;
            border: 1px solid #1e3a5f;
            border-radius: 10px;
            padding: 16px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(df=None, show_filters=False):
    apply_custom_css()

    with st.sidebar:
        # Branding
        st.markdown("""
        <div style='text-align: center; padding: 20px 0 10px 0;'>
            <div style='font-size: 48px;'>🔬</div>
            <div style='font-size: 20px; font-weight: bold;
                        color: #4da6ff; margin-top: 8px;'>
                ThesisLens
            </div>
            <div style='font-size: 12px; color: #888; margin-top: 4px;'>
                Shodhganga Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        st.markdown("""
        <div style='padding: 0 8px; margin-bottom: 8px;'>
            <div style='font-size: 11px; color: #666;
                        text-transform: uppercase;
                        letter-spacing: 1px;'>
                NAVIGATION
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.page_link("app.py",
                     label="🏠  Home")
        st.page_link("pages/01_search.py",
                     label="🔍  Semantic Search")
        st.page_link("pages/02_bibliometrics.py",
                     label="📊  Bibliometrics")
        st.page_link("pages/03_duplication.py",
                     label="🔁  Duplication Check")
        st.page_link("pages/04_variable_map.py",
                     label="🗺️  Variable Map")

        # Filters — only shown on pages that need them
        filtered_df = df

        if show_filters and df is not None:
            st.markdown("---")
            st.markdown("""
            <div style='padding: 0 8px; margin-bottom: 8px;'>
                <div style='font-size: 11px; color: #666;
                            text-transform: uppercase;
                            letter-spacing: 1px;'>
                    FILTERS
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Discipline filter
            disciplines = ["All"] + sorted(
                df["discipline"].dropna().unique().tolist()
            )
            selected_discipline = st.selectbox(
                "📚 Discipline",
                disciplines
            )

            # Year filter
            year_min = int(df["year"].min())
            year_max = int(df["year"].max())
            year_range = st.slider(
                "📅 Year Range",
                min_value=year_min,
                max_value=year_max,
                value=(year_min, year_max)
            )

            # Apply filters
            filtered_df = df.copy()

            if selected_discipline != "All":
                filtered_df = filtered_df[
                    filtered_df["discipline"] == selected_discipline
                ]

            filtered_df = filtered_df[
                (filtered_df["year"] >= year_range[0]) &
                (filtered_df["year"] <= year_range[1])
            ].reset_index(drop=True)

            # Show filter stats
            st.markdown(f"""
            <div style='padding: 8px; font-size: 12px;
                        background: #1e3a5f; border-radius: 8px;
                        margin-top: 8px;'>
                <b style='color:#4da6ff'>Showing:</b>
                <span style='color:#fff'>{len(filtered_df):,} theses</span>
                <br>
                <b style='color:#4da6ff'>Discipline:</b>
                <span style='color:#fff'>{selected_discipline}</span>
                <br>
                <b style='color:#4da6ff'>Years:</b>
                <span style='color:#fff'>
                    {year_range[0]} – {year_range[1]}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Dataset info
        st.markdown("""
        <div style='padding: 8px; font-size: 12px; color: #666;'>
            <div style='margin-bottom: 4px;'>
                📚 <b style='color:#888'>Dataset</b>
            </div>
            <div style='color: #4da6ff;'>Shodhganga via OpenAlex</div>
            <div style='margin-top: 8px; margin-bottom: 4px;'>
                🤖 <b style='color:#888'>Models</b>
            </div>
            <div style='color: #4da6ff;'>SPECTER2 + FAISS</div>
            <div style='margin-top: 8px; margin-bottom: 4px;'>
                🏛️ <b style='color:#888'>Institution</b>
            </div>
            <div style='color: #4da6ff;'>IIT Jodhpur</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("""
        <div style='padding: 8px; font-size: 11px; color: #555;
                    text-align: center;'>
            Chaitanya Mahajan<br>
            M25AI2099 · M.Tech <br>
        </div>
        """, unsafe_allow_html=True)

    return filtered_df