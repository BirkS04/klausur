import streamlit as st
import os
#from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import base64
import json
#import tiktoken
import mimetypes

# Load environment variables from a .env file.  This is a common practice for managing API keys and other sensitive information.
#load_dotenv()
# Set environment variables for Google and OpenAI API keys.  These are retrieved from the .env file.
#os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
# Initialize the large language model (LLM).  Here, Google's Gemini is used.
llm2 = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
# The following line is commented out, indicating that OpenAI's GPT model is an alternative that could be used instead.
# llm = ChatOpenAI(model="o1-preview-2024-09-12")
# llm = ChatAnthropic(model="claude-3-5-haiku-20241022")
llm1 = ChatAnthropic(model="claude-3-5-sonnet-latest")

model = st.radio(
    label="Whäle eine Option",
    options=("gemini", "claude")
)
if model == "gemini":
    llm = llm2
else:
    llm = llm1



#test
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

with open("verhalten2.txt", "r", encoding="utf-8") as file:
    verhalten2 = [{"role": "user", "content": f"{file.read()}"}]

with open("PO2.txt", "r", encoding="utf-8") as file:
    PO2 = [{"role": "user", "content": f"{file.read()}"}]

passwort = st.secrets["passwort"]

system_message1 = """Du bist ein Professor im Fach Verhaltenwissenschafliche Grundlagen, Organisationslehre und Personalwirtschaft. Im Folgenden wirst du die Vorlesungsunterlagen dieses Semesters erhalten. Lies diese gründlich durch. Danach wirst Du Fotos von Multiple Choice Aufgaben erhalten, bei denen jeweils nur eine Anwortmöglichkeit zu wählen ist. ##Ziel: Dein Ziel ist es die Multiple Choice Aufgabe zu beantworten. Gehe dabei Schritt für Schritt die Antwortmöglichkeiten durch und gib schließlich eine Antwort. Prüfe deine Antwort auf Korrektheit. ##Beispiele und Ausgabeformat : 
Aufgabe:
5. Welche Aussage zu empirischen Wissenschaften trifft nicht vollständig zu? Entscheiden Sie sich für eine Aussage (1 aus 5)!
A) Es sollen möglichst allgemeingültige Aussagen über den Forschungsgegenstand getroffen werden, um Phänomene oder deren Bedingungen zu erklären, vorherzusagen oder zu modifizieren.
B) Hypothesen geben Auskunft über reale Zusammenhänge von mindestens zwei Variablen.
C) Aussagen haben dann einen empirischen Gehalt, wenn sich deren dazugehörigen Phänomene anhand von Erfahrung überprüfen lassen.
D) Die Wissenschaftstheorie befasst sich mit einer Vielzahl von Fragen, diedem Schema empirischer Wissenschaften zugrunde liegen.
E) Die Aussage W e n n Menschen in einem Arbeitsteam sehr unterschiedliche
Persönlichkeitseigenschaften besitzen, dann kann ein solches Team Probleme besser lösen" ist prinzipiell empirisch überprüfbar.

Antwort und Ausgabe:
5: B||
##Wichtig: Deine Ausgabe darf nur die Buchstaben der Lösung und die Nummer der Aufgabe enthalten. Schreibe nie mehr.
"""
system_message2 = """Du bist ein Professor im Fach Verhaltenwissenschafliche Grundlagen, Organisationslehre und Personalwirtschaft. Im Folgenden wirst du die Vorlesungsunterlagen dieses Semesters erhalten. Lies diese gründlich durch. Danach wirst Aufgaben erhalten. ##Ziel: Dein Ziel ist es die Aufgaben so knapp wie möglich zu beantworten. Gib nur Stichpunkte zu den wichtigsten informationen an, vernachllässige unwichtige Informationen.
"""

option = st.radio(
    label="Whäle eine Option",
    options=("verhalten", "PO")
)
if option == "verhalten":
    sess.message_list = verhalten2

else:
    sess.message_list = PO2

mode = st.radio(
    label="Whäle eine Option",
    options=("MC", "TEXT")
)
if mode == "MC":
    system_prompt = system_message1
else:
    system_prompt = system_message2
#st.write(sess.message_list[0])


def invoke(query):
    message_list = sess.message_list
    message_list.insert(0, system_prompt)
    message_list.append({"role": "user", "content": "###Fotos der Aufgaben:"})

    for image in sess.images_list:
        message_list.append(image)

    message_list.append({"role": "user", "content": query })

    # st.write(len(message_list))
    # st.write(message_list[1])
    # st.write(message_list)
    with st.chat_message("AI"):
        ai_response = st.write_stream(llm.stream(message_list))


def convert(uploaded_file):
    file_content = uploaded_file.getvalue()

    # In Base64 kodieren
    encoded_string = base64.b64encode(file_content).decode("utf-8")

    message = {"role": "user", "content": {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}}

    return message


def image_to_base64_dict(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == 'png':
        mime_type = 'image/png'
    elif file_extension in ('jpg', 'jpeg'):
        mime_type = 'image/jpeg'
    else:
        raise ValueError("Nicht unterstütztes Format. Nur PNG, JPG und JPEG sind erlaubt.")

    # Lese die Bilddaten aus dem FileUploader
    image_bytes = uploaded_file.read()
    encoded_bytes = base64.b64encode(image_bytes)
    base64_str = {"role": "user", "content": {"typy": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded_bytes.decode('utf-8')}"}}}

    # Erstelle ein Dictionary für die Weiterverarbeitung mit LangChain
    return base64_str


def image_to_base64(image_bytes):
    """Konvertiert Bildbytes in einen Base64-String."""
    try:
        return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        st.error(f"Fehler bei der Base64-Konvertierung: {e}")
        return ""



def create_image_json(image_ext, base64_string):
    """Erstellt das JSON-Format für die Bilddaten, das an die KI übergeben werden kann."""
    return {"role": "user", "content": [{
        "type": "image_url",
        "image_url": {
            "url": f"data:image/{image_ext};base64,{base64_string}"
        }
    }]}






# Set the title of the Streamlit app.
st.title("🤖Bot🤖")

# Main application logic, handling user authentication and chat functionality.
if not sess.logged_in:
    st.chat_input("Passwort eingeben!", disabled=True)
    with st.sidebar:
        sess.password = st.text_input(type="password", label="passwort eingeben")
        st.write(sess.password)
        if sess.password and passwort == sess.password:
            sess.logged_in = True
            st.rerun(scope="app")
else:
    query = st.chat_input("Frag etwas")


    if query:
            invoke(query)


    with st.sidebar:
        with st.expander(label="Upload Images"):

            uploaded_files = st.file_uploader("Lade ein Bild hoch", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)

            if uploaded_files:
                button = st.button(label="hochladen")
                if button:
                    for uploaded_file in uploaded_files:
                        # Lese die Bildbytes
                        image_bytes = uploaded_file.read()

                        # Bestimme den MIME-Typ des hochgeladenen Bildes
                        mime_type, _ = mimetypes.guess_type(uploaded_file.name)

                        # Extrahiere die Dateierweiterung aus dem MIME-Typ
                        image_ext = mime_type.split('/')[
                            1] if mime_type else "jpeg"  # Default auf "jpeg", falls MIME-Typ nicht erkannt wird

                        # Konvertiere die Bildbytes in einen Base64-String
                        base64_string = image_to_base64(image_bytes)

                        if base64_string:
                            # Erstelle das JSON im gewünschten Format für die KI
                            image_json = create_image_json(image_ext, base64_string)
                            # st.write(llm.invoke([image_json,{"role": "user", "content":"was ist zu sehen auf dem bild ?"} ]))
                            # st.write(image_json)
                            sess.images_list.append(image_json)

                        else:
                            st.error("Fehler beim Konvertieren des Bildes.")
            # files = st.file_uploader(label="Upload a PDF", type=["jpg", "png", "jpeg"], accept_multiple_files= True)
            #
            # if files:
            #     upload = st.button("Upload Images")
            #     if upload:
            #         for i, file in enumerate(files):
            #             with st.spinner("Images being processed"):
            #                 # upload_button = st.button(f"ADD: {file.name}")
            #
            #                 image = image_to_base64_dict(file)
            #                 sess.images_list.append(image)
            #                 st.success(f"PDF {i + 1} processed")
            #                 # st.write(sess.images_list[i]["type"])




        messages = []
        for msg in messages:
            id = msg[0]
            role = msg[2]
            content = msg[3]
            if role == "system":
                with st.chat_message(role):
                    st.markdown(content)
            elif role == "pdf":
                with st.expander(label=":page_facing_up: Your PDF"):
                    json_string = json.loads(content)
                    for i, item in enumerate(json_string):
                        st.text_area(label=f"{i}",value=item, height=200, key=f"{id},{i}")
            else:
                with st.chat_message(role):
                    st.markdown(content)



