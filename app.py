import streamlit as st
from groq import Groq

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
        # Using Llama 3 8B - Fast, highly capable, and stable
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
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

# --- UI SETUP ---
st.sidebar.title("🛠️ Career Tools")
app_mode = st.sidebar.selectbox("Choose a Tool", ["Resume Auditor", "Mock Interviewer"])

# --- MODE 1: RESUME AUDITOR ---
if app_mode == "Resume Auditor":
    st.header("📝 Resume Gap Analysis")
    st.markdown("Paste your resume. The audit will be ruthless. Identify your gaps before recruiters do.")
    
    resume_text = st.text_area("Resume Content:", height=300)
    
    if st.button("🚀 Execute Audit"):
        if resume_text:
            with st.spinner("Analyzing architecture and project depth..."):
                sys_prompt = "You are a strict, senior engineering manager auditing a fresher's resume for Data Science and Machine Learning roles. Do not sugarcoat. Identify exactly 3 technical gaps and suggest 2 rigorous projects to fix them."
                
                result = query_ai(resume_text, sys_prompt)
                
                if "API Error" in result:
                    st.error(result)
                else:
                    st.success("Audit Complete.")
                    st.markdown(result)
        else:
            st.warning("Input required. Paste your resume text.")

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
                
                # Pass the last few interactions for context
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history[-3:]])
                
                result = query_ai(context, sys_prompt)
                
                if "API Error" in result:
                    st.error(result)
                else:
                    st.markdown(result)
                    st.session_state.chat_history.append({"role": "assistant", "content": result})
