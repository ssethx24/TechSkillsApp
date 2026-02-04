import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from src.text_clean import normalize_title
from src.extract import aggregate_skills
from src.report import make_pdf_report

DATA_PATH = "data/job_dataset.csv"

st.set_page_config(page_title="Tech Skills Recommender", layout="wide")
st.title("Tech Skills Recommender (using real dataset)")
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

col1, col2 = st.columns([2, 1])
with col1:
    query = st.text_input("Enter a job title (e.g., .NET Developer, Data Analyst)", value=".NET Developer")
with col2:
    top_n = st.slider("Top N skills", 5, 30, 15)

filtered = df[df["Title"].str.contains(query, case=False, na=False)]
matched = len(filtered)

st.write(f"Matched **{matched}** rows for: **{query}**")

if matched == 0:
    st.warning("No matches. Tip: try a broader term like 'Developer', 'Engineer', or 'Analyst'.")
    st.stop()

# Aggregate skills from filtered rows
rows = filtered[["Skills", "Keywords"]].to_dict(orient="records")
top = aggregate_skills(rows, top_n=top_n)
top_df = pd.DataFrame(top, columns=["Skill", "Mentions"])

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
