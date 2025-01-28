import streamlit as st
from streamlit_chat import message
import openai

# Title and instructions
st.title("AI Agent Demo with Document Processing")
st.write("This app simulates an AI agent integrated with document processing. Upload a document or ask a question to start.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI agent. You can upload a document for analysis or ask me a question."}
    ]

# Sidebar for OpenAI API Key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

openai.api_key = api_key

# File upload for document processing
document = st.file_uploader("Upload a document (PDF or text format) for analysis", type=["pdf", "txt"])

def mock_document_analysis(doc_content):
    # This simulates ABI Vantage processing
    if "invoice" in doc_content.lower():
        return "It looks like this is an invoice document. I detected potential issues with the VAT rate."  
    return "Document processed successfully with no detected issues."

# Display the message history
for msg in st.session_state.messages:
    message(msg["content"], is_user=(msg["role"] == "user"))

# Handle file processing
if document:
    try:
        content = document.read().decode("utf-8", errors="ignore")
        analysis_result = mock_document_analysis(content)
        st.session_state.messages.append({"role": "assistant", "content": analysis_result})
        message(analysis_result, is_user=False)
    except Exception as e:
        st.error(f"Error reading the document: {e}")

# Handle user input for chat
user_input = st.text_input("Ask a question or request further analysis:", key="user_input")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate AI response using OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )
        assistant_reply = response["choices"][0]["message"]["content"]
    except Exception as e:
        assistant_reply = f"Error connecting to OpenAI: {e}"

    # Append and display the response
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    message(assistant_reply, is_user=False)

st.write("\nPro Tip: Try uploading an invoice-like document to see intelligent recommendations.")
