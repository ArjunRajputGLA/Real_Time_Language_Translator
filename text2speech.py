
import streamlit as st
import time
import os
import base64
from googletrans import Translator
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect, LangDetectException
import threading
from gtts import gTTS
import io

st.set_page_config( 
    page_title= "Text 2 Speech",
    page_icon='🗣️',
)

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


st.markdown("""
    <style>
    .sub-title {
        color: cyan;
        text-align: center;
        margin-top: 1px;
    }
    .sidebar-header {
        color: orange;
    }
    .section-header {
        color: #20B2AA;  /* Light Sea Green */
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp


def load_marian_model(src_lang, tgt_lang):
    try:
        model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
    except Exception as e:
        print(f"Direct model not available for {src_lang} to {tgt_lang}. Attempting to use English as intermediary.")
        # First, translate to English
        en_model_name = f'Helsinki-NLP/opus-mt-{src_lang}-en'
        en_tokenizer = MarianTokenizer.from_pretrained(en_model_name)
        en_model = MarianMTModel.from_pretrained(en_model_name)
        
        # Then, translate from English to target language
        tgt_model_name = f'Helsinki-NLP/opus-mt-en-{tgt_lang}'
        tgt_tokenizer = MarianTokenizer.from_pretrained(tgt_model_name)
        tgt_model = MarianMTModel.from_pretrained(tgt_model_name)
        
        return (en_tokenizer, en_model), (tgt_tokenizer, tgt_model)
    return tokenizer, model

def translate_text(text, src_lang, tgt_lang, method='marian'):
    if method == 'marian':
        try:
            model = load_marian_model(src_lang, tgt_lang)
            if isinstance(model[0], tuple):  # This means we're using two-step translation
                en_tokenizer, en_model = model[0]
                tgt_tokenizer, tgt_model = model[1]
                
                # Translate to English first
                en_translated = en_model.generate(**en_tokenizer(text, return_tensors="pt", padding=True))
                en_text = en_tokenizer.decode(en_translated[0], skip_special_tokens=True)
                
                # Then translate from English to target language
                tgt_translated = tgt_model.generate(**tgt_tokenizer(en_text, return_tensors="pt", padding=True))
                tgt_text = tgt_tokenizer.decode(tgt_translated[0], skip_special_tokens=True)
            else:
                tokenizer, model = model
                translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
                tgt_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            return tgt_text
        except Exception as e:
            print(f"An error occurred with MarianMT translation: {str(e)}")
            print("Falling back to Google Translate...")
            method = 'googletrans' 
    
    if method == 'googletrans':
        try:
            translator = Translator()
            translation = translator.translate(text, src=src_lang, dest=tgt_lang)
            return translation.text
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")

    raise ValueError("Invalid translation method specified")

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return None

def show_temporary_warning(message, duration=2):
    warning_placeholder = st.empty()
    warning_placeholder.warning(message)
    threading.Timer(duration, warning_placeholder.empty).start()

LANGUAGE_DICT = {
    'auto': 'Auto Detect',
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian',
    'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian',
    'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish',
    'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek',
    'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi',
    'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish',
    'it': 'Italian', 'ja': 'Japanese', 'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer',
    'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian',
    'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay',
    'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)',
    'ne': 'Nepali', 'no': 'Norwegian', 'or': 'Odia', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish',
    'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic',
    'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
    'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish',
    'tg': 'Tajik', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu',
    'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish',
    'yo': 'Yoruba', 'zu': 'Zulu'
}

sub_title = 'Translate text to speech among different languages'

@st.cache_data
def generate_full_subtitle(): 
    return sub_title

if 'title_displayed' not in st.session_state:
    st.session_state.title_displayed = False

if 'src_lang_auto' not in st.session_state:
    st.session_state.src_lang_auto = None

if not st.session_state.title_displayed:
    title_placeholder = st.empty()
    subtitle_placeholder = st.empty()

    full_subtitle = generate_full_subtitle()

    for i in range(len(full_subtitle.split())):
        subtitle_placeholder.markdown(f"<h1 class='sub-title'>{' '.join(full_subtitle.split()[:i+1])}</h1>", unsafe_allow_html=True)
        time.sleep(0.33)

    st.session_state.title_displayed = True
else:
    st.markdown(f"<h1 class='sub-title'>{generate_full_subtitle()}</h1>", unsafe_allow_html=True)

st.markdown("---")

src_text = st.text_area('', placeholder="Enter text to translate", height=10)

if src_text:
    st.session_state.src_lang_auto = detect_language(src_text)
    if st.session_state.src_lang_auto:
        st.markdown(f"<p class='section-header'>Detected source language: {LANGUAGE_DICT[st.session_state.src_lang_auto]}</p>", unsafe_allow_html=True)
        st.markdown("---")
    else:
        show_temporary_warning('Unable to detect language. Please select the source language manually.')

st.sidebar.markdown("---")

st.sidebar.markdown("<h2 class='sidebar-header' style='font-size:32px;'>Select</h2>", unsafe_allow_html=True)
st.sidebar.markdown(" ")

src_languages = list(LANGUAGE_DICT.keys()) 
tgt_languages = [lang for lang in src_languages if lang != 'auto']

col1, col2 = st.sidebar.columns(2)
with col1:
    src_lang_full = st.selectbox('Source language:', 
                                 [LANGUAGE_DICT[lang] for lang in src_languages],
                                 index=0 if st.session_state.src_lang_auto is None else 
                                 src_languages.index(st.session_state.src_lang_auto))
    src_lang = src_languages[[LANGUAGE_DICT[lang] for lang in src_languages].index(src_lang_full)]

with col2:
    tgt_lang_full = st.selectbox('Target language:', 
                                 [LANGUAGE_DICT[lang] for lang in tgt_languages])
    tgt_lang = tgt_languages[[LANGUAGE_DICT[lang] for lang in tgt_languages].index(tgt_lang_full)]

st.sidebar.markdown("---")

st.sidebar.markdown("<h3 class='sidebar-header' style='font-size:30px;'>Translation Method</h3>", 
unsafe_allow_html=True)

method = st.sidebar.radio('', ['Google Translate', 'MarianMT'])
st.sidebar.markdown("---")


if st.button('Translate'):
    st.markdown("---") 
    if not src_text:
        show_temporary_warning('Please enter text to translate!')
    else:
        if src_lang == 'auto':
            if st.session_state.src_lang_auto:
                src_lang = st.session_state.src_lang_auto
            else:
                show_temporary_warning('Unable to detect language. Please select a source language!')
                st.stop()
        if src_lang == tgt_lang:
            show_temporary_warning("Source and Target languages should be different!")
            st.stop()
        
        try:
            if method == 'Google Translate':
                translation = translate_text(src_text, src_lang, tgt_lang, method='googletrans')
            else:
                translation = translate_text(src_text, src_lang, tgt_lang, method='marian')
                
            st.markdown("<h3 class='section-header'>Translated Text and Audio:</h3>", unsafe_allow_html=True)
            st.text_area('', value=translation, height=20, disabled=True)
            
            audio_fp = text_to_speech(translation, tgt_lang)
            st.audio(audio_fp, format='audio/mp3')
            st.markdown("---")
        except Exception as e:
            st.error(f"An error occurred during translation or audio generation: {str(e)}") 