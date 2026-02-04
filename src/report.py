from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def make_pdf_report(job_title: str, matched_count: int, top_df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    _, h = letter

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
