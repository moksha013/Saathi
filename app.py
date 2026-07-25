import streamlit as st
import requests
from pypdf import PdfReader
import json

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(
    page_title="Saathi",
    page_icon="✦",
    layout="centered"
)

# -------------------------
# Custom CSS
# -------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0f1117;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background-color: #0f1117;
}

h1 {
    text-align: center;
    font-size: 52px;
    font-weight: 700;
    color: white;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #9aa0a6;
    margin-bottom: 30px;
    font-size: 18px;
}

.stChatMessage {
    border-radius: 18px;
    padding: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# Heading
# -------------------------
st.markdown("<h1>Saathi</h1>", unsafe_allow_html=True)

st.markdown(
    "<p class='subtitle'>Always by your side.</p>",
    unsafe_allow_html=True
)

st.caption("Private • Local • Powered by Ollama")

# -------------------------
# PDF Upload
# -------------------------
uploaded_file = st.file_uploader(
    "📄 Learn from Documents",
    type=["pdf"],
    help="Upload notes, books or research papers."
)

pdf_text = ""

if uploaded_file:
    pdf = PdfReader(uploaded_file)

    for page in pdf.pages:
        text = page.extract_text()

        if text:
            pdf_text += text

    st.success("📄 Document ready. Ask Saathi anything about it.")

# -------------------------
# Code Input
# -------------------------
code_input = st.text_area(
    "💻 Debug & Explain Code",
    placeholder="Paste your Python, C, Java or JavaScript code here...",
    height=180
)

# -------------------------
# Chat History
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Display previous messages
for message in st.session_state.messages:
    avatar = "💭" if message["role"] == "user" else "🤝"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# -------------------------
# Chat Input
# -------------------------
prompt = st.chat_input("Ask Saathi anything...")

if prompt:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Show user message
    with st.chat_message("user", avatar="💭"):
        st.markdown(prompt)

    # Show assistant
    with st.chat_message("assistant", avatar="🤝"):

        with st.spinner("🤝 Saathi is thinking..."):

            question = prompt.lower()

            # -------------------------
            # Decide Mode
            # -------------------------

            # CODE MODE
            if code_input.strip() and any(word in question for word in [
                "code",
                "bug",
                "debug",
                "error",
                "fix",
                "explain",
                "optimize",
                "python",
                "java",
                "c",
                "javascript"
            ]):

                context = f"""
You are Saathi, an AI coding assistant.

Rules:
- Analyze ONLY the code given.
- Never invent new code.
- Never assume missing code.
- Find syntax errors.
- Find logical errors.
- Explain the bug in simple language.
- If there is no bug, clearly say so.
- If needed, provide corrected code.

Code:
{code_input}

Question:
{prompt}

Answer:
"""

            # PDF MODE
            elif pdf_text.strip() and any(word in question for word in [
                "pdf",
                "document",
                "notes",
                "chapter",
                "summary",
                "page",
                "file"
            ]):

                context = f"""
You are Saathi, a study assistant.

Rules:
- Answer ONLY using the uploaded PDF.
- If the answer isn't in the PDF, say so.
- Explain in simple language.

PDF:
{pdf_text[:5000]}

Question:
{prompt}

Answer:
"""

            # NORMAL CHAT
            else:

                context = f"""
You are Saathi.

A friendly AI companion.

Rules:
- Reply naturally.
- Keep responses short.
- Never invent conversations.
- Never repeat the user's question.
- Be friendly.

User:
{prompt}

Assistant:
"""
                ai_response = ""
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "gemma3:1b",
                        "prompt": context,
                        "stream": True
                    },
                        stream=True,
                        timeout=120
                )

                response.raise_for_status()


                message_placeholder = st.empty()
                full_response = ""

                for line in response.iter_lines():

                    if line:

                        chunk = json.loads(line.decode("utf-8"))

                        if "response" in chunk:
                            full_response += chunk["response"]

                            message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                ai_response = full_response
            except Exception as e:
                ai_response = f"⚠️ Error: {e}"        
            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })
# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + Ollama")