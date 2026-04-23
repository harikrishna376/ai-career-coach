import streamlit as st
from groq import Groq
import PyPDF2
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Career Coach", page_icon="⚙️", layout="wide")

# --- INITIALIZE CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("FATAL ERROR: GROQ_API_KEY is missing from Streamlit Secrets.")
    st.stop()

def query_ai(prompt, system_prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

def extract_text_from_pdf(uploaded_file):
    try:
        # Read the PDF file directly from memory
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            # Extract text from each page and append
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

# --- UI SETUP ---
st.sidebar.title("🛠️ Career Tools")
app_mode = st.sidebar.selectbox("Choose a Tool", ["Resume Auditor", "Mock Interviewer"])

# --- MODE 1: RESUME AUDITOR ---
if app_mode == "Resume Auditor":
    st.header("📝 Resume Gap Analysis")
    st.markdown("Upload your resume in PDF format. The audit will be ruthless. Identify your gaps before recruiters do.")
    
    # The new File Uploader widget
    uploaded_pdf = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
    
    if uploaded_pdf is not None:
        st.info("PDF loaded into memory. Ready for extraction.")
        
        if st.button("🚀 Execute Audit"):
            with st.spinner("Extracting text and analyzing architecture..."):
                # Extract text
                resume_text = extract_text_from_pdf(uploaded_pdf)
                
                if "Error extracting PDF" in resume_text:
                    st.error(resume_text)
                elif not resume_text.strip():
                    st.error("The PDF appears to be empty or contains only unreadable images.")
                else:
                    # Show the extracted text briefly so the user knows it worked
                    with st.expander("View Extracted Text"):
                        st.text(resume_text)
                        
                    # Send to LLM
                    sys_prompt = "You are a strict, senior engineering manager auditing a fresher's resume for Data Science and Machine Learning roles. Do not sugarcoat. Identify exactly 3 technical gaps and suggest 2 rigorous projects to fix them."
                    result = query_ai(resume_text, sys_prompt)
                    
                    if "API Error" in result:
                        st.error(result)
                    else:
                        st.success("Audit Complete.")
                        st.markdown(result)

# --- MODE 2: MOCK INTERVIEWER ---
else:
    st.header("🤖 Technical Mock Interview")
    st.info("Strict technical evaluation for Data Science and Python Engineering roles.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if user_input := st.chat_input("Submit your answer..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Evaluating logic..."):
                sys_prompt = "Act as a ruthless Technical Interviewer assessing a candidate for a competitive Data Science role. Evaluate their previous answer for logical flaws, lack of depth, or poor architecture. Ask the next highly technical question related to machine learning pipelines, regression models, or data structures. Do not break character."
                
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history[-3:]])
                
                result = query_ai(context, sys_prompt)
                
                if "API Error" in result:
                    st.error(result)
                else:
                    st.markdown(result)
                    st.session_state.chat_history.append({"role": "assistant", "content": result})
                    
