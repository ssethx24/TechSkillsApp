import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter


from src.text_clean import normalize_title
from src.extract import aggregate_skills
from src.report import make_pdf_report

DATA_PATH = "data/job_dataset.csv"

st.set_page_config(page_title="Tech Skills Recommender", layout="wide")
st.title("Tech Skills Recommender")
st.caption("Type a job title and get the most recurring technical skills from the dataset.")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"Title", "Skills", "Keywords", "Responsibilities"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    for c in ["Title", "Skills", "Keywords", "Responsibilities"]:
        df[c] = df[c].fillna("").astype(str)

    df["Title"] = df["Title"].map(normalize_title)
    return df

df = load_data(DATA_PATH)

def skills_counter_for_query(df: pd.DataFrame, query: str) -> tuple[pd.DataFrame, int, Counter]:
    """
    Returns:
      - filtered_df
      - matched_count
      - Counter of skills (from Skills + Keywords)
    """
    filtered = df[df["Title"].str.contains(query, case=False, na=False)]
    matched = len(filtered)
    rows = filtered[["Skills", "Keywords"]].to_dict(orient="records")
    top = aggregate_skills(rows, top_n=10_000)  # big N to get full counter

    c = Counter()
    for skill, count in top:
        c[skill] = count

    return filtered, matched, c


mode = st.radio("Mode", ["Single Role", "Compare Two Roles"], horizontal=True)

if mode == "Single Role":
    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_input("Enter a job title (e.g., .NET Developer, Data Analyst)", value=".NET Developer")
    with col2:
        top_n = st.slider("Top N skills", 5, 30, 15)

    filtered, matched, counter = skills_counter_for_query(df, query)

    st.write(f"Matched **{matched}** rows for: **{query}**")
    if matched == 0:
        st.warning("No matches. Tip: try a broader term like 'Developer', 'Engineer', or 'Analyst'.")
        st.stop()

    top_df = pd.DataFrame(counter.most_common(top_n), columns=["Skill", "Mentions"])

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Top skills (table)")
        st.dataframe(top_df, use_container_width=True)

        csv_bytes = top_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"top_skills_{query.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )

        pdf_bytes = make_pdf_report(query, matched, top_df)
        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name=f"skills_report_{query.replace(' ', '_').lower()}.pdf",
            mime="application/pdf"
        )

    with right:
        st.subheader("Bar chart")
        fig, ax = plt.subplots()
        ax.bar(top_df["Skill"], top_df["Mentions"])
        ax.set_ylabel("Mentions")
        ax.set_xlabel("Skill")
        ax.set_xticklabels(top_df["Skill"], rotation=60, ha="right")
        st.pyplot(fig, clear_figure=True)

    st.subheader("Word cloud (optional)")
    if st.toggle("Show word cloud"):
        wc = WordCloud(width=900, height=450, background_color="white").generate(" ".join(top_df["Skill"].tolist()))
        fig2, ax2 = plt.subplots()
        ax2.imshow(wc, interpolation="bilinear")
        ax2.axis("off")
        st.pyplot(fig2, clear_figure=True)

    st.divider()
    st.subheader("Matched titles preview")
    st.write(sorted(filtered["Title"].unique())[:20])

else:
    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
        query_a = st.text_input("Role A (e.g., .NET Developer)", value=".NET Developer")
    with c2:
        query_b = st.text_input("Role B (e.g., Cloud Engineer)", value="Cloud Engineer")
    with c3:
        top_n = st.slider("Top N skills", 5, 30, 15)

    filtered_a, matched_a, counter_a = skills_counter_for_query(df, query_a)
    filtered_b, matched_b, counter_b = skills_counter_for_query(df, query_b)

    st.write(f"Matched **{matched_a}** rows for **{query_a}** | Matched **{matched_b}** rows for **{query_b}**")

    if matched_a == 0 or matched_b == 0:
        st.warning("One of the roles has 0 matches. Try broader terms like 'Developer', 'Engineer', or 'Analyst'.")
        st.stop()

    # Overlap and differences
    set_a = set(counter_a.keys())
    set_b = set(counter_b.keys())

    common = set_a & set_b
    only_a = set_a - set_b
    only_b = set_b - set_a

    common_df = pd.DataFrame(
        [(s, counter_a[s], counter_b[s]) for s in common],
        columns=["Skill", f"{query_a} Mentions", f"{query_b} Mentions"]
    ).sort_values(by=[f"{query_a} Mentions", f"{query_b} Mentions"], ascending=False).head(top_n)

    only_a_df = pd.DataFrame(
        [(s, counter_a[s]) for s in only_a],
        columns=["Skill", "Mentions"]
    ).sort_values(by="Mentions", ascending=False).head(top_n)

    only_b_df = pd.DataFrame(
        [(s, counter_b[s]) for s in only_b],
        columns=["Skill", "Mentions"]
    ).sort_values(by="Mentions", ascending=False).head(top_n)

    st.subheader("Comparison Insights")
    top_common = common_df["Skill"].head(5).tolist() if not common_df.empty else []
    if top_common:
        st.write(f"Top overlapping skills: **{', '.join(top_common)}**")
    st.write(f"Unique skills in **{query_a}**: **{len(only_a)}** | Unique skills in **{query_b}**: **{len(only_b)}**")

    t1, t2 = st.columns(2)
    with t1:
        st.subheader(f"Top skills — {query_a}")
        top_a_df = pd.DataFrame(counter_a.most_common(top_n), columns=["Skill", "Mentions"])
        st.dataframe(top_a_df, use_container_width=True)

    with t2:
        st.subheader(f"Top skills — {query_b}")
        top_b_df = pd.DataFrame(counter_b.most_common(top_n), columns=["Skill", "Mentions"])
        st.dataframe(top_b_df, use_container_width=True)

    st.divider()
    st.subheader("Common skills (overlap)")
    st.dataframe(common_df, use_container_width=True)

    cta1, cta2 = st.columns(2)
    with cta1:
        st.subheader(f"Skills unique to {query_a}")
        st.dataframe(only_a_df, use_container_width=True)
    with cta2:
        st.subheader(f"Skills unique to {query_b}")
        st.dataframe(only_b_df, use_container_width=True)

    # Download comparison CSV
    export_common = common_df.copy()
    export_only_a = only_a_df.copy()
    export_only_b = only_b_df.copy()

    # Create a single multi-sheet-like CSV by adding section headers
    export_lines = []
    export_lines.append("=== Common Skills ===")
    export_lines.append(export_common.to_csv(index=False))
    export_lines.append("\n=== Unique Skills (Role A) ===")
    export_lines.append(export_only_a.to_csv(index=False))
    export_lines.append("\n=== Unique Skills (Role B) ===")
    export_lines.append(export_only_b.to_csv(index=False))

    comparison_csv = "\n".join(export_lines).encode("utf-8")

    st.download_button(
        "Download Comparison CSV",
        data=comparison_csv,
        file_name=f"compare_{query_a.replace(' ', '_').lower()}_vs_{query_b.replace(' ', '_').lower()}.csv",
        mime="text/csv"
    )

with right:
    st.subheader("Bar chart")
    fig, ax = plt.subplots()
    ax.bar(top_df["Skill"], top_df["Mentions"])
    ax.set_ylabel("Mentions")
    ax.set_xlabel("Skill")
    ax.set_xticklabels(top_df["Skill"], rotation=60, ha="right")
    st.pyplot(fig, clear_figure=True)

st.subheader("Word cloud (optional)")
if st.toggle("Show word cloud"):
    wc = WordCloud(width=900, height=450, background_color="white").generate(" ".join(top_df["Skill"].tolist()))
    fig2, ax2 = plt.subplots()
    ax2.imshow(wc, interpolation="bilinear")
    ax2.axis("off")
    st.pyplot(fig2, clear_figure=True)

st.divider()
st.subheader("Matched titles preview")
st.write(sorted(filtered["Title"].unique())[:20])
