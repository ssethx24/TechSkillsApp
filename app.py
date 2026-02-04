import re
from io import BytesIO
from collections import Counter

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from wordcloud import WordCloud
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Tech Skills Recommender", layout="wide")
st.title("Tech Skills Recommender (using real dataset)")
st.caption("Type a job title and get the most recurring technical skills from the dataset.")

DATA_PATH = "data/job_dataset.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"Title", "Skills", "Keywords", "Responsibilities"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")
    for c in ["Title", "Skills", "Keywords", "Responsibilities"]:
        df[c] = df[c].fillna("").astype(str)
    return df

def normalize_title(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def split_skills(text: str) -> list[str]:
    """
    Dataset uses semi-structured skills like:
    'C#; .NET Core; SQL Server ...'
    and keywords like:
    '.NET; C#; ASP.NET MVC; ...'
    We'll split on ; and , and clean tokens.
    """
    if not text:
        return []
    parts = re.split(r"[;,]\s*", text)
    out = []
    for p in parts:
        p = p.strip()
        p = re.sub(r"\s+", " ", p)
        # remove tiny noise
        if len(p) < 2:
            continue
        out.append(p)
    return out

def make_pdf_report(job_title: str, matched_count: int, top_df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 50, "Tech Skills Recommender Report")

    c.setFont("Helvetica", 11)
    c.drawString(50, h - 80, f"Job title query: {job_title}")
    c.drawString(50, h - 100, f"Matched roles: {matched_count}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, h - 130, "Top recommended skills:")

    c.setFont("Helvetica", 11)
    y = h - 155
    for _, row in top_df.iterrows():
        c.drawString(60, y, f"- {row['Skill']} ({row['Mentions']})")
        y -= 16
        if y < 60:
            c.showPage()
            y = h - 60
            c.setFont("Helvetica", 11)

    c.save()
    return buf.getvalue()

df = load_data(DATA_PATH)
df["Title"] = df["Title"].map(normalize_title)

# ---- UI controls ----
col1, col2 = st.columns([2, 1])
with col1:
    query = st.text_input("Enter a job title (e.g., .NET Developer, Data Analyst)", value=".NET Developer")
with col2:
    top_n = st.slider("Top N skills", 5, 30, 15)

# title match (contains)
filtered = df[df["Title"].str.contains(query, case=False, na=False)]
matched = len(filtered)

st.write(f"Matched **{matched}** rows for: **{query}**")

if matched == 0:
    st.warning("No matches. Tip: try a broader term (e.g., 'Developer', 'Engineer', 'Analyst').")
    st.stop()

# ---- skill aggregation ----
counter = Counter()
for _, row in filtered.iterrows():
    # Structured sources (best)
    counter.update(split_skills(row["Skills"]))
    counter.update(split_skills(row["Keywords"]))

top = counter.most_common(top_n)
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

