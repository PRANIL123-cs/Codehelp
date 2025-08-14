import streamlit as st
from io import BytesIO
from gtts import gTTS
import qrcode
from datetime import datetime
import requests

# ================================
# UI Theme
# ================================
def apply_theme(dark_mode: bool):
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&family=Roboto&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
    bg_color = "#121212" if dark_mode else "#FDF6E3"
    text_color = "white" if dark_mode else "black"
    st.markdown(f"""
<style>
.stApp {{background-color: {bg_color}; color: {text_color};}}
h1, h2, h3 {{font-family: 'Poppins', sans-serif; font-weight: 600; color: {text_color};}}
p, label, .stMarkdown, div, span {{font-family: 'Roboto', sans-serif; font-size: 16px; color: {text_color};}}
.stButton>button {{
    background-color: #FF6B6B; color: white !important; border-radius: 10px;
    font-size: 16px; padding: 0.5em 1em; font-family: 'Poppins', sans-serif;
}}
.stButton>button:hover {{background-color: #FF4C4C;}}
</style>
""", unsafe_allow_html=True)

# ================================
# Helpers
# ================================
def make_qr_image(url: str) -> bytes:
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

def upload_fileio(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            res = requests.post("https://file.io", files={"file": f}, timeout=30)
        data = res.json()
        if data.get("success") and data.get("link"):
            return data["link"]
    except Exception:
        pass
    return ""

# ================================
# Language choices
# ================================
LANG_CHOICES = {
    "English (US)": "en",
    "English (UK)": "en-uk",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Hindi": "hi",
}

# ================================
# Page State
# ================================
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# ================================
# Welcome Page
# ================================
def render_welcome():
    st.markdown("<h1 style='text-align: center;'>🎧 Welcome to EchoVerse</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("🚀 How it works")
    st.markdown("""
1. *Enter or upload* your text  
2. *Choose* a language and tone  
3. *Generate* and preview your audiobook  
4. *Download* or share instantly  
""")

    st.subheader("💡 Features")
    st.markdown("""
- Free Google-powered text-to-speech  
- Multiple languages supported  
- QR code sharing  
- Dark mode  
""")

    if st.button("🎬 Start Creating"):
        st.session_state.page = "generator"

# ================================
# Generator Page
# ================================
def render_generator():
    colA, colB = st.columns([1, 1])
    with colA:
        st.title("🎧 EchoVerse — Free Audiobook Generator")
    with colB:
        dark_mode = st.toggle("🌙 Dark Mode", value=False)
    apply_theme(dark_mode)

    st.header("📄 Text Input")
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    input_text = st.text_area("Or paste your text here:")
    if uploaded_file:
        input_text = uploaded_file.read().decode("utf-8")

    st.header("🌍 Choose Language")
    target_lang_label = st.selectbox("Language", list(LANG_CHOICES.keys()), index=0)
    target_lang = LANG_CHOICES[target_lang_label]

    st.header("✨ Tone")
    tone = st.selectbox("Narration tone (for tag only)", ["Neutral", "Friendly", "Professional", "Dramatic"], index=0)

    st.header("⚡ Generate Audiobook")
    if st.button("Generate Audiobook"):
        if not input_text.strip():
            st.warning("Please enter or upload text before generating audio.")
        else:
            text_for_audio = f"[{tone} Version] {input_text}"
            try:
                tts = gTTS(text=text_for_audio, lang=target_lang.split("-")[0], slow=False)
                mp3_buffer = BytesIO()
                tts.write_to_fp(mp3_buffer)
                mp3_data = mp3_buffer.getvalue()
            except Exception as e:
                st.error(f"Audio generation failed: {e}")
                st.stop()

            st.subheader("🎧 Preview & Download")
            st.audio(mp3_data, format="audio/mp3")
            st.download_button("⬇ Download MP3", mp3_data, file_name="narration.mp3", type="primary")

            tmp_filename = f"narration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
            with open(tmp_filename, "wb") as f:
                f.write(mp3_data)

            share_url = upload_fileio(tmp_filename)
            if share_url:
                st.success(f"Shareable link: {share_url}")
                qr_png = make_qr_image(share_url)
                st.image(qr_png, caption="Scan to listen on mobile")
            else:
                st.info("Could not create shareable link.")

# ================================
# Render page based on state
# ================================
if st.session_state.page == "welcome":
    render_welcome()
else:
    render_generator()