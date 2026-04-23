import streamlit as st
import requests
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Career Coach", page_icon="🚀", layout="wide")

# --- AI CONFIG ---
# Using the 2b-it model for faster free inference
# The stable, actively hosted endpoint
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b-it"
# Access token from Streamlit Secrets
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def query_gemma(payload):
    # 'wait_for_model' tells Hugging Face to hold the request until the model is loaded
    payload["options"] = {"wait_for_model": True, "use_cache": True}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            return {"error": "Model is loading... please wait a moment and try again."}
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

# --- UI SETUP ---
st.sidebar.title("🛠️ Career Tools")
app_mode = st.sidebar.selectbox("Choose a Mode", ["Resume Auditor", "Mock Interviewer"])

# --- MODE 1: RESUME AUDITOR ---
if app_mode == "Resume Auditor":
    st.header("📝 Resume Gap Analysis")
    st.markdown("Past your resume below to find missing skills for **Data Science & ML** roles.")
    
    resume_text = st.text_area("Resume Content:", height=300, placeholder="Copy and paste your resume text here...")
    
    if st.button("🚀 Analyze My Resume"):
        if resume_text:
            with st.spinner("Gemma is auditing your resume..."):
                prompt = f"<start_of_turn>user\nYou are an expert Technical Recruiter. Analyze this resume for a Data Science Fresher role. \n1. Identify 3 missing technical skills.\n2. Suggest 2 projects to add.\nResume:\n{resume_text}<end_of_turn>\n<start_of_turn>model\n"
                
                result = query_gemma({"inputs": prompt})
                
                if isinstance(result, dict) and "error" in result:
                    st.error(result["error"])
                else:
                    # Successfully received JSON list
                    output = result[0]['generated_text'].split("model\n")[-1]
                    st.success("Audit Complete!")
                    st.markdown(output)
        else:
            st.warning("Please paste your resume text first.")

# --- MODE 2: MOCK INTERVIEWER ---
else:
    st.header("🤖 Mock Interviewer")
    st.info("I will act as a TCS Technical Interviewer. Let's practice!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display Chat
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if user_input := st.chat_input("Answer the question..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Evaluating..."):
                system_prompt = "Act as a Senior Interviewer. Evaluate the user's answer and ask the next technical question regarding Python or Machine Learning."
                full_prompt = f"<start_of_turn>user\n{system_prompt}\nUser Answer: {user_input}<end_of_turn>\n<start_of_turn>model\n"
                
                result = query_gemma({"inputs": full_prompt})
                
                if isinstance(result, dict) and "error" in result:
                    st.error(result["error"])
                else:
                    response = result[0]['generated_text'].split("model\n")[-1]
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
