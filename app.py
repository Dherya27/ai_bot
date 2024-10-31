__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import streamlit as st
from dsrag.llm import OpenAIChatAPI
from knowledge_base import KnowledgeBaseHandler
from utils import reformulate_question, stream_output
from prompt_template import get_system_prompt
from dotenv import load_dotenv
import os
# # Load environment variables
# env_file_path = ".env"
# load_dotenv(dotenv_path=env_file_path)

def get_openai_chat_api():
    # Get the API key from Streamlit secrets
    api_key = st.secrets["OPENAI_API_KEY"]
    
    # Temporarily set the environment variable
    os.environ["OPENAI_API_KEY"] = api_key
    # Initialize the OpenAIChatAPI
    chat_api = OpenAIChatAPI(
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=1000
    )
    
    return chat_api

api_key = st.secrets["OPENAI_API_KEY"]

# Initialize knowledge base handler
kb_handler = KnowledgeBaseHandler(kb_id="arlo",storage_directory="database")

# Initialize Streamlit App
st.title("Arlo AI Assistant--VERSION-2.0")

# Initialize Chat History and retrieved_info
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize retrieved_info with an empty string
retrieved_info = ""

# Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Enter your query"):
    # Add the user's query to the chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    contextualized_prompt = f"Let's think step by step. {reformulate_question(prompt, st.session_state.chat_history)}"
    # print("##############################################")
    # print("contextualized_prompt =========> ",contextualized_prompt)
    
    # Retrieve Relevant Information from the Knowledge Base using the reformulated query
    retrieved_info = kb_handler.retrieve_information(contextualized_prompt)
    # print("##############################################")
    # print("retrieved_info =========> ",retrieved_info)

    context_message = get_system_prompt(prompt, st.session_state.chat_history, retrieved_info)
    chat_messages = [{"role": "system", "content": context_message}]
    
    # Add the previous conversation history to the chat messages
    for message in st.session_state.chat_history:
        chat_messages.append(message)

    # Include the new user prompt
    chat_messages.append({"role": "user", "content": prompt})

    # Initialize OpenAIChatAPI
    # chat_api = OpenAIChatAPI(model="gpt-4o-mini", temperature=0.2, max_tokens=1000)
    chat_api = get_openai_chat_api()

    # Call the language model
    response = chat_api.make_llm_call(chat_messages)
    
    with st.chat_message("assistant"):
        st.write_stream(stream_output(response))
    
    # Update Chat History
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history.pop(0)

# Sidebar to Display Retrieved Context
with st.sidebar:
    st.sidebar.title('Source Documents')
    st.sidebar.text_area(label='Retrieved Context', value=retrieved_info if retrieved_info else "No context retrieved yet.", height=900)