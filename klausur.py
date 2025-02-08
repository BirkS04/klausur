import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

import base64
import json

# Load environment variables from a .env file.  This is a common practice for managing API keys and other sensitive information.
load_dotenv()
# Set environment variables for Google and OpenAI API keys.  These are retrieved from the .env file.
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")


# Initialize the large language model (LLM).  Here, Google's Gemini is used.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
# The following line is commented out, indicating that OpenAI's GPT model is an alternative that could be used instead.
# llm = ChatOpenAI(model="gpt-4o-mini")

# Access Streamlit's session state.  Session state allows data to persist across multiple runs of the app.
sess = st.session_state
# Initialize session state variables if they don't already exist.  These are used to store various aspects of the application's state.
if "password" not in sess:
    sess.password = ""
if "logged_in" not in sess:
    sess.logged_in = False

if "message_list" not in sess:
    sess.message_list = []

if "images_list" not in sess:
    sess.images_list = []

with open("verhalten.txt", "r", encoding="utf-8") as file:
    verhalten = json.load(file)

with open("PO.txt", "r", encoding="utf-8") as file:
    PO = json.load(file)


option = st.radio(
    label="Whäle eine Option",
    options=("verhalten", "PO")
)
if option == "verhalten":
    sess.message_list = verhalten
else:
    sess.message_list = PO
#st.write(sess.message_list[0])

system_prompt = """Du bist ein Professor im Fach Verhaltenwissenschafliche Grundlagen, Organisationslehre und Personalwirtschaft. Im Folgenden wirst du die Vorlesungsunterlagen dieses Semesters erhalten. Lies diese gründlich durch. Danach wirst Du Fotos von Multiple Choice Aufgaben erhalten, bei denen jeweils nur eine Anwortmöglichkeit zu wählen ist. ##Ziel: Dein Ziel ist es die Multiple Choice Aufgabe zu beantworten. Gehe dabei Schritt für Schritt die Antwortmöglichkeiten durch und gib schließlich eine Antwort. Prüfe deine Antwort auf Korrektheit. ##Beispiele : """
def invoke(query):
    message_list = sess.message_list
    message_list.insert(0, system_prompt)
    message_list.append({"role": "user", "content": "###Fotos der Aufgaben:"})

    for image in sess.images_list:
        message_list.append(image)

    message_list.append({"role": "user", "content": query })

    st.write(len(message_list))
    st.write(message_list[1])
    with st.chat_message("AI"):
        ai_response = st.write_stream(llm.stream(message_list))


def convert(uploaded_file):
    file_content = uploaded_file.getvalue()

    # In Base64 kodieren
    encoded_string = base64.b64encode(file_content).decode("utf-8")

    message = {"role": "user", "content": {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}}

    return message


# Set the title of the Streamlit app.
st.title("🤖Bot🤖")

# Main application logic, handling user authentication and chat functionality.
if not sess.logged_in:
    st.chat_input("Passwort eingeben!", disabled=True)
    with st.sidebar:
        sess.password = st.text_input(type="password", label="passwort eingeben")
        st.write(sess.password)
        if sess.password and "birk" == sess.password:
            sess.logged_in = True
            st.rerun(scope="app")
else:
    query = st.chat_input("Frag etwas")


    if query:
            invoke(query)

    with st.sidebar:
        with st.expander(label="Upload Images"):

            files = st.file_uploader(label="Upload a PDF", type=["jpg", "png", "jpeg"], accept_multiple_files= True)

            if files:
                upload = st.button("Upload Images")
                if upload:
                    for i, file in enumerate(files):
                        with st.spinner("Images being processed"):
                            # upload_button = st.button(f"ADD: {file.name}")

                            image = convert(file)
                            sess.images_list.append(image)
                            st.success(f"PDF {i + 1} processed")
                            # st.write(sess.images_list[i]["type"])




        messages = []
        for msg in messages:
            id = msg[0]
            role = msg[2]
            content = msg[3]
            if role == "system":
                with st.chat_message(role):
                    st.markdown(content)
            elif role == "pdf":
                with st.expander(label=f":page_facing_up: Your PDF"):
                    json_string = json.loads(content)
                    for i, item in enumerate(json_string):
                        st.text_area(label=f"{i}",value=item, height=200, key=f"{id},{i}")
            else:
                with st.chat_message(role):
                    st.markdown(content)

