import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up page configurations
st.set_page_config(
    page_title="Asilbek AI - Sun'iy Intellekt",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM GLASSMORPHIC CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global Fonts & Custom Scrollbar */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
        background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%) !important;
        color: #f8fafc !important;
    }
    
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(56, 189, 248, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(56, 189, 248, 0.6);
    }

    /* Sidebar Styling Override */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Header Container */
    .header-container {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: fadeIn 0.8s ease-out;
    }
    
    .header-title-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .header-logo {
        font-size: 40px;
        filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.5));
    }

    .header-text h1 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-text p {
        margin: 5px 0 0 0 !important;
        font-size: 14px !important;
        color: #94a3b8 !important;
    }

    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        color: #10b981;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
        animation: pulse 2.0s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Sidebar Title */
    .sidebar-brand {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .sidebar-brand h2 {
        font-size: 24px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
    }
    .sidebar-brand p {
        font-size: 12px !important;
        color: #64748b !important;
        margin: 5px 0 0 0 !important;
    }

    /* Info cards */
    .premium-card {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    /* Standard Streamlit chat message containers overrides */
    div[data-testid="stChatMessage"] {
        background-color: rgba(30, 41, 59, 0.35) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        padding: 18px !important;
        margin-bottom: 15px !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        animation: fadeIn 0.4s ease-out;
    }

    div[data-testid="stChatMessage"]:hover {
        border-color: rgba(56, 189, 248, 0.35) !important;
        box-shadow: 0 10px 30px rgba(56, 189, 248, 0.08) !important;
        transform: translateY(-1px);
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATIONS ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Asilbek AI</h2>
        <p>Llama 3.1 & Groq Cloud</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="premium-card"><b>🇺🇿 Til:</b> O\'zbek tili<br><b>🗣️ Shaxsiyat:</b> Virtual yordamchi</div>', unsafe_allow_html=True)
    
    st.subheader("⚙️ Sozlamalar")
    
    # Model Selection (both are Llama 3.1 on Groq!)
    model_option = st.selectbox(
        "SI Modeli",
        ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"],
        help="Llama 3.1 8B tezkor va samarali, 70B esa chuqurroq tahliliy fikrlash qobiliyatiga ega."
    )
    
    # Temperature parameter (Creativity)
    temperature = st.slider(
        "Kreativlik (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Yuqori qiymat ijodiy va noodatiy javoblarni beradi, past qiymat esa aniqroq va faktik javob beradi."
    )
    
    # Max tokens
    max_tokens = st.slider(
        "Maksimal javob uzunligi",
        min_value=256,
        max_value=4096,
        value=2048,
        step=128,
        help="Asilbek qaytaradigan javobning maksimal so'z/token hajmi."
    )
    
    st.markdown("---")
    
    # Clear chat history button
    if st.button("🗑️ Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.success("Suhbat tarixi tozalandi!")
        st.rerun()
        
    st.markdown("""
    <div class="premium-card" style="font-size: 12px; color: #94a3b8; text-align: center;">
        Dasturchi: <b>Asilbek</b><br>
        Texnologiya: <b>Streamlit & Groq Cloud</b><br>
        Llama 3.1 Model Integratsiyasi
    </div>
    """, unsafe_allow_html=True)

# --- MAIN APP HEADER ---
st.markdown("""
<div class="header-container">
    <div class="header-title-section">
        <div class="header-logo">🤖</div>
        <div class="header-text">
            <h1>Asilbek AI</h1>
            <p>Sizning o'zbek tilidagi aqlli sun'iy intellekt yordamchingiz</p>
        </div>
    </div>
    <div class="status-badge">
        <div class="pulse-dot"></div>
        Online
    </div>
</div>
""", unsafe_allow_html=True)

# --- INITIALIZE GROQ CLIENT ---
# Load API key from environment variable
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    # Fallback to sidebar text input if .env is missing or doesn't have the key
    st.error("⚠️ GROQ_API_KEY topilmadi! Iltimos, .env faylini tekshiring yoki API kalitini kiriting.")
    groq_api_key = st.text_input("Groq API Kaliti (gsk_...):", type="password")

if not groq_api_key:
    st.info("💡 Davom etish uchun .env fayliga API kalitini yozing yoki yuqoridagi maydonga kiriting.")
    st.stop()

# Initialize Client
try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    st.error(f"Groq API mijozini ishga tushirishda xatolik yuz berdi: {e}")
    st.stop()

# --- SYSTEM PROMPT (PERSONA DEFINITION) ---
SYSTEM_PROMPT = (
    "Sizning ismingiz - Asilbek. Siz foydalanuvchilarga har qanday mavzuda yordam beradigan "
    "juda aqlli, xushmuomala, muloyim va do'stona sun'iy intellekt yordamchisiz.\n\n"
    "MUHIM MULOQOT QOIDALARI:\n"
    "1. Siz FAQAT va FAQAT O'ZBEK TILIDA gapirishingiz shart. Boshqa tillarda yozilgan har qanday savolga ham "
    "muloyimlik bilan faqat o'zbek tilida yordam bera olishingizni tushuntiring va muloqotni o'zbek tilida olib boring.\n"
    "2. Foydalanuvchiga har doim hurmat bilan, 'Siz' deb murojaat qiling.\n"
    "3. Javoblaringiz aniq, batafsil, imlo qoidalariga rioya qilgan holda va chiroyli formatlangan (Markdown, jadvallar, "
    "ro'yxatlar orqali) bo'lishi lozim.\n"
    "4. Hech qachon o'zingiz bilmagan ma'lumotlarni to'qimang, agar javobini bilmasangiz, buni samimiy tan oling."
)

# --- SESSION STATE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- USER INPUT & CHAT COMPLETION ---
if prompt := st.chat_input("Asilbek AI ga savol bering..."):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Add user message to session history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate assistant response
    with st.chat_message("assistant"):
        # Placeholder for streaming text
        response_placeholder = st.empty()
        full_response = ""
        
        # Build message history for the model API (including system prompt)
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Append recent chat logs to keep context
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        try:
            # Call Groq Chat Completion with streaming
            completion = client.chat.completions.create(
                model=model_option,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Stream tokens to the screen
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            # Show final cleaned markdown response
            response_placeholder.markdown(full_response)
            
            # Append assistant response to session history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ulanishda xatolik yuz berdi: {str(e)}")
            st.info("Iltimos, API kalitingiz va internet ulanishingizni tekshiring.")
