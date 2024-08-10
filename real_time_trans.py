
import streamlit as st
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from playsound import playsound
import os
import base64
import random

st.set_page_config( 
    page_title= "Real Time Translator",
    page_icon='🌍',
)

st.markdown("""
    <style>
    .main-title {
        top: 0;
        right: 0;
        padding: 10px;
        color: #20B2AA;
        font-size: 3rem;
        z-index: 1000;
        font-weight: bold;
        margin-top: -58px;
        margin-bottom: 50px;
        margin-left: -210px;
    }
    .marquee {
        width: 100%;
        overflow: hidden;
        color: white;
        padding: 10px 0;
    }
    .marquee-content {
        animation: marquee 10s linear infinite;
        font-size: 20px;
        color: lightblue;
    }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .stSidebar .css-1lcbmhc, .stSidebar .css-12oz5g7 {
        background-color: #f5f5f5;
    }
    .stSidebar select {
        font-size: 14px;
    }
    .stSidebar h1 {
        font-size: 24px;
        color: #333;
    }
    .sidebar-title {
        color: cyan;
        text-align: center;
        font-size: 104px;
        font-weight: bold;
        margin-bottom: 10px;
        margin-left: -25px;
    }
    </style>
    
    <div class="main-title">🌍 Real-Time Speech Translator</div>
    <div class="marquee">
        <div class="marquee-content">
            <strong>Translate your speech to another language in real-time!</strong>
        </div>
    </div>
""", unsafe_allow_html=True) 


def get_base64_of_video(video_file):
    with open(video_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_path = "Logo.mp4"
if os.path.exists(logo_path):
    video_base64 = get_base64_of_video(logo_path)
    st.sidebar.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            padding-top: 0rem;
        }}
        .sidebar-logo {{
            position: relative;
            top: -1rem;  
            width: 100%;
            margin-bottom: -3rem;  
        }}
        .sidebar-logo video {{
            width: 100%;
        }}
        </style>
        <div class="sidebar-logo">
            <video autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.warning("Logo video not found. Please ensure 'Logo.mp4' is in the same directory as the script.") 

recognizer = sr.Recognizer()
translator = Translator()

def get_supported_languages():
    return {lang: LANGUAGES[lang].capitalize() for lang in LANGUAGES}

supported_languages = get_supported_languages()


st.info("⚠️ This feature requires a microphone. Please ensure your browser has permission to access it.")

st.sidebar.markdown("---")
st.markdown("---")
st.write("<h1 style='color: cyan; font-size: 38px; font-weight: bold;'>Select</h1>", unsafe_allow_html=True)
st.markdown(" ")

col1, col2 = st.columns(2)
with col1:
    input_language = st.selectbox("Source Language", 
                                  list(supported_languages.keys()), 
                                  format_func=lambda x: f"{supported_languages[x]} ({x})")

with col2:
    target_language = st.selectbox("Target Language", 
                                   list(supported_languages.keys()), 
                                   format_func=lambda x: f"{supported_languages[x]} ({x})")


st.sidebar.markdown("<h1 style='color: lightblue; text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px; margin-left: -25px;'>💡 Language Facts</h1>", unsafe_allow_html=True)
st.sidebar.markdown(" ") 
facts = [
    "The most widely spoken language in the world is Mandarin Chinese.",
    "There are over 7,000 languages spoken in the world today.",
    "The language with the most words is English, with over 1 million words.",
    "The hardest language to learn for English speakers is generally considered to be Mandarin Chinese.",
    "More than half of the world's population is bilingual.",
    "The oldest written language in the world is believed to be Sumerian.",
    "There are over 200 artificial languages that have been invented for books, TV shows, and movies.",
    "The United Nations uses six official languages: Arabic, Chinese, English, French, Russian, and Spanish.",
    "The language with the most native speakers is Mandarin Chinese, followed by Spanish and then English.",
    "Papua New Guinea has the most languages, with over 840 living languages.",
    "The language Toki Pona has only 123 words but can express complex ideas.",
    "Sign languages are natural languages with their own grammar and vocabulary.",
    "The Bible is the most translated book in the world, available in over 700 languages.",
    "The word 'alphabet' comes from the first two letters of the Greek alphabet: alpha and beta.",
    "The longest word in English without a vowel is 'rhythms'.",
    "In Japan, there are over 50,000 characters in the kanji writing system, but only about 2,000 are commonly used.",
    "The Korean alphabet, Hangul, was created by King Sejong the Great in the 15th century.",
    "The 'Oxford comma' is optional in British English but often mandatory in American English.",
    "The word 'emoji' comes from Japanese, meaning 'picture character'.",
    "There are more than 300 sign languages in use around the world.",
    "The language with the most letters is Khmer (Cambodian), with 74 letters.",
    "The quickest disappearing language family is the Australian Aboriginal languages.",
    "The word 'goodbye' is a contraction of 'God be with ye'.",
    "The Basque language is considered a language isolate, unrelated to any other known language.",
    "The first known dictionary was written in cuneiform on clay tablets more than 4,000 years ago."
]
 
if 'displayed_facts' not in st.session_state:
    st.session_state.displayed_facts = set()

def get_unique_fact():
    available_facts = [fact for fact in facts if fact not in st.session_state.displayed_facts]
    if not available_facts:
        st.session_state.displayed_facts.clear()
        available_facts = facts 
    fact = random.choice(available_facts)
    st.session_state.displayed_facts.add(fact)
    return fact

fact1 = get_unique_fact()
fact2 = get_unique_fact()
fact3 = get_unique_fact()
fact4 = get_unique_fact()

st.sidebar.info(f"🤩 {fact1}")
st.sidebar.success(f"🌟 {fact2}")
st.sidebar.warning(f"🌺 {fact3}")
st.sidebar.error(f"📚 {fact4}")
st.sidebar.markdown("---")

st.markdown("---")
if st.button("🎙️ Start Recording"):
    if input_language == target_language:
        st.warning("Source and Target language cannot be the same!")
    else:
        if 'translation_results' in st.session_state:
            del st.session_state.translation_results

        st.session_state.translation_results = []

        try:
            with sr.Microphone() as source:
                st.markdown(" ")
                with st.spinner("🎤 Recording... (Speak now), the recording will stop after 5 seconds of silence!"):
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)

            st.write("✅ Recording finished.")
            st.markdown("---")

            try:
                transcript_text = recognizer.recognize_google(audio, language=input_language)
                st.write(f"**Recognized Text:** {transcript_text}")
                st.markdown("---") 

                translation = translator.translate(transcript_text, dest=target_language)
                translated_text = translation.text

                st.session_state.translation_results.append({
                    "translation": translated_text,
                    "error": None
                })

                if translated_text.strip():
                    tts = gTTS(translated_text, lang=target_language)
                    tts.save("translated_audio.mp3")

                    playsound("translated_audio.mp3")

            except sr.UnknownValueError:
                st.warning("⚠️ Speech recognition could not understand the audio!")
            except sr.RequestError as e:
                st.error(f"Could not request results from speech recognition service; {e}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        finally:
            if os.path.exists("translated_audio.mp3"):
                os.remove("translated_audio.mp3")

        if 'translation_results' in st.session_state:
            for result in st.session_state.translation_results:
                st.write(f"**Translation :** {result['translation']}")
                st.markdown("---") 
                if result['error']:
                    st.warning(result['error']) 