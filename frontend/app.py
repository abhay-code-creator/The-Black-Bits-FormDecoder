import json
import hashlib

import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.form_service import analyze_form
from backend.pdf_service import generate_pdf

st.set_page_config(
    page_title="FormDecoder | Smart Form Assistant",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(
        ellipse at 15% 0%,
        rgba(120,102,255,.12),
        transparent 40%
    );
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 2.5rem;
    border-radius: 24px;
    background: linear-gradient(125deg, #211d45, #302768, #174c60);
    border: 1px solid rgba(255,255,255,.12);
    margin-bottom: 1.5rem;
}

.hero h1 {
    color: white;
    font-size: clamp(32px, 4vw, 48px);
    font-weight: 800;
    line-height: 1.15;
}

.hero p {
    color: #e0e4fa;
    line-height: 1.8;
    font-size: 16px;
}

.tag {
    color: #d8d2ff;
    font-size: 12px;
    letter-spacing: 1px;
    font-weight: 700;
}

.feature {
    padding: 18px;
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 16px;
    background: var(--secondary-background-color);
    min-height: 125px;
}

.feature-title {
    font-weight: 700;
    margin: 8px 0 5px;
}

.muted {
    color: #929bb2;
    font-size: 13px;
    line-height: 1.6;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #7866ff, #6254e8);
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
}

div[data-testid="stExpander"] {
    border-radius: 12px;
    margin-bottom: 8px;
}

div[data-testid="stFileUploader"] {
    border: 1px dashed #8174d9;
    border-radius: 16px;
    padding: 12px;
}

.footer {
    border-top: 1px solid rgba(128,128,128,.2);
    margin-top: 3rem;
    padding-top: 1.2rem;
    text-align: center;
    color: #929bb2;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## 📄 FormDecoder")
    st.caption("Your intelligent form companion")
    st.divider()

    st.markdown("### ✨ Features")
    st.markdown(
        "- 🔍 Smart field explanations\n"
        "- 🌐 English and Hindi\n"
        "- 📋 Interactive checklist\n"
        "- 📥 Downloadable reports"
    )

    st.divider()
    st.markdown("### 🔒 Privacy")
    st.caption(
        "Uploaded forms are sent to the configured AI service "
        "for analysis. Avoid uploading sensitive documents "
        "unless you are comfortable sharing them with that service."
    )

    st.divider()
    st.caption("Python · Streamlit · Gemma · Gemini API")


st.markdown("""
<div class="hero">
    <div class="tag">✦ YOUR AI FORM ASSISTANT</div>
    <h1>Paperwork,<br>made simple.</h1>
    <p>
        Understand confusing forms one field at a time.
        Get simple explanations, a document checklist, and
        important instructions in English or Hindi.
    </p>
</div>
""", unsafe_allow_html=True)


c1, c2, c3 = st.columns(3)

for column, icon, title, description in [
    (c1, "🔍", "Smart form reading",
     "Identify fields and understand what to enter."),
    (c2, "🌐", "Your language",
     "Read explanations in English or हिंदी."),
    (c3, "📋", "Stay prepared",
     "Review documents and important instructions.")
]:
    with column:
        st.markdown(
            f"""
            <div class="feature">
                <div style="font-size:26px">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="muted">{description}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown("## Let's understand your form")
st.markdown(
    '<p class="muted">Upload a clear photo of the entire form to begin.</p>',
    unsafe_allow_html=True
)

language = st.radio(
    "Choose your language / अपनी भाषा चुनें",
    ["English", "हिंदी"],
    horizontal=True
)

uploaded = st.file_uploader(
    "Upload your form",
    type=["jpg", "jpeg", "png"]
)


def make_text_report(data):
    lines = [
        str(data.get("form_type", "Form Analysis")),
        "=" * 40,
        "",
        "FIELDS TO FILL",
        ""
    ]

    for field in data.get("fields", []):
        if not isinstance(field, dict):
            continue

        lines.append(str(field.get("name", "Field")))
        lines.append(str(field.get("explanation", "")))

        if field.get("example"):
            lines.append("Example: " + str(field["example"]))

        lines.append("")

    lines.extend(["DOCUMENTS TO PREPARE", ""])

    for document in data.get("documents_needed", []):
        lines.append("- " + str(document))

    lines.extend(["", "IMPORTANT INFORMATION", ""])

    for warning in data.get("warnings", []):
        lines.append("- " + str(warning))

    return "\n".join(lines)


if uploaded:
    signature = hashlib.sha256(uploaded.getvalue()).hexdigest()
    analysis_key = f"{signature}:{language}"

    if st.session_state.get("analysis_key") != analysis_key:
        st.session_state.pop("analysis_data", None)
        st.session_state["analysis_key"] = analysis_key

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("### 🖼️ Your form")

        st.image(
            uploaded,
            caption=uploaded.name,
            width="stretch"
        )

    with right:
        st.markdown("### Ready to decode?")
        st.write(
            "We'll identify the visible fields, explain what to "
            "enter, and suggest documents to prepare."
        )

        st.markdown(
            '<p class="muted">Tip: Use a clear image with good lighting.</p>',
            unsafe_allow_html=True
        )

        if st.button(
            "✨ Explain this form",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Reading your form..."):
                try:
                    uploaded.seek(0)
                    result = analyze_form(uploaded, language)

                    st.session_state["analysis_data"] = result
                    st.session_state["analysis_key"] = analysis_key

                except Exception as error:
                    st.error(
                        "The form could not be analyzed. "
                        "Please try again with a clear image."
                    )

                    with st.expander("Technical details"):
                        st.code(str(error))

    data = st.session_state.get("analysis_data")

    if (
        data
        and st.session_state.get("analysis_key") == analysis_key
    ):
        st.divider()
        st.markdown("## ✨ Your form, explained")
        st.caption("Explore the results in the sections below.")

        fields = [
            field for field in data.get("fields", [])
            if isinstance(field, dict)
        ]

        documents = data.get("documents_needed", [])
        warnings = data.get("warnings", [])

        m1, m2, m3 = st.columns(3)
        m1.metric("Fields identified", len(fields))
        m2.metric("Documents suggested", len(documents))
        m3.metric("Important notes", len(warnings))

        fields_tab, docs_tab, warnings_tab = st.tabs([
            "🔍 Field explanations",
            "📋 Document checklist",
            "⚠️ Important notes"
        ])

        with fields_tab:
            search = st.text_input(
                "Search fields",
                placeholder="Search for Customer ID, address, etc."
            )

            matching_fields = [
                field for field in fields
                if search.lower() in (
                    str(field.get("name", "")) + " " +
                    str(field.get("explanation", ""))
                ).lower()
            ]

            if not matching_fields:
                st.info("No matching fields found.")

            for index, field in enumerate(matching_fields):
                name = field.get("name", f"Field {index + 1}")

                with st.expander(str(name)):
                    st.write(field.get("explanation", ""))

                    if field.get("example"):
                        st.info("Example: " + str(field["example"]))

        with docs_tab:
            st.caption(
                "Tick items as you prepare them. "
                "Confirm actual requirements with your institution."
            )

            if documents:
                for index, document in enumerate(documents):
                    st.checkbox(
                        str(document),
                        key=f"doc_{signature[:12]}_{index}"
                    )
            else:
                st.info("No specific documents were identified.")

        with warnings_tab:
            if warnings:
                for warning in warnings:
                    st.warning(str(warning))
            else:
                st.success("No additional warnings were returned.")

            st.info(
                "AI can make mistakes. Verify important details "
                "with the relevant bank or institution."
            )

        st.divider()
        
        st.markdown("### 📥 Download your results")

        d1, d2 = st.columns(2)

        pdf_bytes = generate_pdf(data, language)

        with d1:
            st.download_button(
                "📄 Download PDF report",
                data=pdf_bytes,
                file_name="formdecoder_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with d2:
            st.download_button(
                "📝 Download text report",
                data=make_text_report(data),
                file_name="formdecoder_report.txt",
                mime="text/plain",
                use_container_width=True
            )

else:
    st.info("👆 Upload a form to begin your analysis.")


st.markdown("""
<div class="footer">
    <strong>FormDecoder</strong> · Making paperwork easier to understand
    <br><br>
    Powered by AI · Built with Python and Streamlit
</div>
""", unsafe_allow_html=True)
