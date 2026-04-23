import streamlit as st
import requests
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Career Coach", page_icon="🚀")

# --- AI CONFIG (Hugging Face Free Inference API) ---
# Get your free token at: https://huggingface.co/settings/tokens
API_URL = "https://api-inference.huggingface.co/models/google/gemma-1.1-2b-it"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def query_gemma(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose a Tool", ["Resume Auditor", "Mock Interviewer"])

# --- MODE 1: RESUME AUDITOR ---
if app_mode == "Resume Auditor":
    st.header("📝 Resume Gap Analysis")
    st.info("Upload your resume text to see where you can improve for Data Science roles.")
    
    resume_input = st.text_area("Paste your Resume Text here:", height=300)
    
    if st.button("Analyze Resume"):
        if resume_input:
            with st.spinner("Gemma is auditing your profile..."):
                prompt = f"<start_of_turn>user\nAnalyze this resume for a Data Science Fresher role. Identify missing technical skills and suggest 3 improvements:\n{resume_input}<end_of_turn>\n<start_of_turn>model\n"
                result = query_gemma({"inputs": prompt})
                # Handle API response
                if isinstance(result, list):
                    st.markdown(result[0]['generated_text'].split("model\n")[-1])
                else:
                    st.error("API is still loading the model. Please try again in 30 seconds.")
        else:
            st.warning("Please paste your resume first!")

# --- MODE 2: MOCK INTERVIEWER ---
else:
    st.header("🤖 Technical Mock Interview")
    st.write("Prepare for your upcoming interviews (like TCS NQT) with AI.")
    
    job_role = st.text_input("Target Job Role:", value="Data Scientist / Python Developer")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your answer..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_prompt = f"Act as a Technical Recruiter for {job_role}. Evaluate the user's last answer and ask one follow-up technical question."
                full_query = f"<start_of_turn>user\n{system_prompt}\nUser says: {prompt}<end_of_turn>\n<start_of_turn>model\n"
                
                result = query_gemma({"inputs": full_query})
                response_text = result[0]['generated_text'].split("model\n")[-1] if isinstance(result, list) else "Model is warming up..."
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
