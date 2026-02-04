

# 🚀 Tech Skills Recommender

🔗 **Live App:**
[https://ssethx24-techskillsapp-app-mqbc1h.streamlit.app/](https://ssethx24-techskillsapp-app-mqbc1h.streamlit.app/)

---

## 📌 Overview

**Tech Skills Recommender** is an interactive data analytics web application built with **Python and Streamlit** that helps users explore the most in-demand technical skills for specific job roles.

By analysing a real-world dataset of job descriptions, the app allows students, job seekers, and career planners to identify which skills are most frequently required for different roles — and to compare skill requirements between two job titles.

---

## 🎯 Key Features

### 🔍 Single Role Analysis

* Enter a job title (e.g. *Software Engineer*, *.NET Developer*, *Data Analyst*)
* View:

  * Top recurring skills
  * Interactive bar chart
  * Optional word cloud
* Download results as:

  * 📄 CSV
  * 📄 PDF report

### ⚖️ Compare Two Roles

* Compare **two job titles side-by-side**
* Identify:

  * Common skills between roles
  * Skills unique to each role
* Export comparison results as CSV

---

## 🧠 Dataset

This project uses the **2025 Job Descriptions – Tech & Non-Tech Roles** dataset from Kaggle:

🔗 [https://www.kaggle.com/datasets/adityarajsrv/job-descriptions-2025-tech-and-non-tech-roles](https://www.kaggle.com/datasets/adityarajsrv/job-descriptions-2025-tech-and-non-tech-roles)

### Dataset Fields Used

| Column             | Purpose                        |
| ------------------ | ------------------------------ |
| `Title`            | Job title used for filtering   |
| `Skills`           | Primary structured skill data  |
| `Keywords`         | Additional skill-related terms |
| `Responsibilities` | Contextual role information    |

Rather than relying only on raw text, this project focuses on **structured skill fields** to produce cleaner and more reliable insights.

---

## ⚙️ How It Works

1. Load and preprocess job data using **Pandas**
2. Normalise job titles for consistent matching
3. Filter records based on user input
4. Extract and aggregate skills from `Skills` and `Keywords`
5. Rank skills by frequency
6. Visualise results and enable downloads

---

## 🛠 Tech Stack

* **Python**
* **Streamlit** – interactive web UI
* **Pandas** – data processing
* **Matplotlib** – charts
* **WordCloud** – skill visualisation
* **ReportLab** – PDF generation

---

## 🗂 Project Structure

```
TechSkillsApp/
├── app.py
├── requirements.txt
├── data/
│   └── job_dataset.csv
├── src/
│   ├── __init__.py
│   ├── text_clean.py
│   ├── extract.py
│   └── report.py
└── README.md
```

---

## 💻 Running Locally

1. Clone the repository:

```bash
git clone https://github.com/your-username/TechSkillsApp.git
cd TechSkillsApp
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

---

## ☁️ Deployment

The application is deployed using **Streamlit Cloud** and automatically updates on every push to the main branch.

---

## 📊 Example Use Cases

* Students identifying skills to prioritise before applying
* Job seekers comparing roles (e.g. Developer vs Cloud Engineer)
* Career advisors generating market insights
* Portfolio demonstration of data analytics and deployment skills

---

## 🔮 Future Enhancements

* Filters for experience level or domain
* Trend analysis across years
* Enhanced NLP extraction from responsibilities text
* Skill category grouping (Languages, Cloud, DevOps, etc.)

---

## 👤 Author

**Shaurya Seth**
GitHub: [https://github.com/ssethx24](https://github.com/ssethx24)

---

## 📜 License

This project is licensed under the **MIT License**.

---
