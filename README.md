# FormDecoder — AI-Powered Form Explanation Assistant

FormDecoder is an AI-powered web application designed to make complex forms easier to understand. It helps users interpret form fields, understand what information is required, and identify the documents they may need to prepare.

Built during a hackathon by **The Black Bits**, FormDecoder aims to make form-filling simpler, more accessible, and less confusing.

## ✨ Features

- **AI-Powered Form Analysis:** Upload a form image for AI-assisted analysis.
- **Field-by-Field Explanations:** Understand what individual fields mean and what information they require.
- **Bilingual Support:** Get explanations in English and Hindi.
- **Document Checklist:** Identify documents that may be required for the form.
- **Important Warnings:** Review relevant notes and potential issues identified during analysis.
- **PDF Report Download:** Download the analysis as a PDF report.
- **Text Report Download:** Save the results as a text file.
- **Simple Web Interface:** Use the application through an interactive Streamlit interface.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web interface |
| Google Gemini API | AI-powered form analysis |
| Pillow | Image processing |
| ReportLab | PDF report generation |
| python-dotenv | Environment variable management |

## 📁 Project Structure

```text
formDecoder/
├── backend/
│   ├── __init__.py
│   ├── form_service.py
│   └── pdf_service.py
├── frontend/
│   └── app.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── test_api.py
```

## 🚀 Getting Started

### Prerequisites

- Python installed on your computer
- A Google Gemini API key
- Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/abhay-code-creator/The-Black-Bits---formDecoder.git
```

```bash
cd The-Black-Bits---formDecoder
```

*If you chose a different repository name, replace the URL and folder
