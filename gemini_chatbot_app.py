import streamlit as st
import google.generativeai as genai
import os

# Streamlit 페이지 설정
st.set_page_config(
    page_title="🐹 덕환이의 코딩친구 AI 🚀", 
    page_icon="🐹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7);
        background-size: 400% 400%;
        animation: gradient 8s ease infinite;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin: 0;
        font-family: 'Comic Sans MS', cursive;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: white;
        margin-top: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .chat-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stChatMessage {
        border-radius: 15px !important;
        margin: 0.5rem 0 !important;
    }
    
    .sidebar-content {
        background: linear-gradient(180deg, #FFE53B 0%, #FF2525 74%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .emoji-divider {
        text-align: center;
        font-size: 2rem;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🐹 김덕환의 바이브 코딩 연습 챗봇 🚀</h1>
    <p class="sub-title">✨ 코딩이 재밌어지는 마법의 공간 ✨</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 꾸미기
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <h2 style="text-align: center; color: white;">🎮 덕환이의 코딩 스테이터스</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔥 오늘의 코딩 기분")
    mood = st.selectbox(
        "현재 기분을 선택해주세요!",
        ["🚀 오늘은 코딩킹!", "🤔 살짝 헷갈려요", "😴 카페인 충전 필요", "💪 불타오르네!", "🎯 집중모드 ON"]
    )
    
    st.markdown("### 📊 오늘의 학습 목표")
    goal = st.text_area("오늘 뭘 배우고 싶나요?", placeholder="예: React Hooks 마스터하기!")
    
    st.markdown("### 🎵 코딩 BGM")
    bgm_options = ["🎼 로파이 힙합", "🎸 신나는 팝", "🎹 클래식", "🎧 일렉트로닉", "🎺 재즈"]
    selected_bgm = st.radio("오늘의 코딩 BGM:", bgm_options)

# 이모지 구분선
st.markdown('<div class="emoji-divider">🌟⭐🌟⭐🌟⭐🌟</div>', unsafe_allow_html=True)

# .streamlit/secrets.toml 파일에서 API 키 불러오기
try:
    genai.configure(api_key=st.secrets["gemini_api_key"])
except AttributeError:
    st.error("🚨 Gemini API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일에 `gemini_api_key = \"YOUR_API_KEY\"` 형식으로 추가해주세요.")
    st.stop()

# Gemini 모델 초기화 및 채팅 기록 설정
if "chat_model" not in st.session_state:
    st.session_state.chat_model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 컨테이너
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("💬 덕환이에게 코딩 질문을 해보세요! (예: 'React에서 useState는 어떻게 써요?')"):
    # 사용자 메시지 대화 기록에 추가 및 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    # 대화 시작 또는 이어가기
    if "chat_session" not in st.session_state:
        # 개성있는 시스템 프롬프트 추가
        system_prompt = f"""
        안녕! 나는 김덕환의 코딩 친구 AI야! 🐹✨
        현재 덕환이의 기분: {mood}
        오늘의 학습 목표: {goal if goal else "멋진 코딩 배우기!"}
        선택한 BGM: {selected_bgm}
        
        나는 항상 친근하고 재미있게 코딩을 가르쳐줄게! 
        이모지도 많이 쓰고, 덕환이가 이해하기 쉽게 설명해줄 거야! 🚀
        """
        
        st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])
        # 이전 대화 기록을 새로 시작하는 chat session에 추가
        for message in st.session_state.messages[:-1]: # 마지막 사용자 메시지 제외
             st.session_state.chat_session.history.append(message)

    try:
        # 현재 사용자 메시지로 응답 얻기
        response = st.session_state.chat_session.send_message(prompt)

        # AI 응답 대화 기록에 추가 및 화면에 표시
        with st.chat_message("assistant"):
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"🚨 챗봇 응답 생성 중 오류가 발생했습니다: {e}")
        st.session_state.messages.pop() # 오류 발생 시 마지막 사용자 메시지 제거하여 재시도 가능하게 함

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <h3>🎯 김덕환의 코딩 여정을 응원합니다! 🎯</h3>
    <p style="color: #666;">Made with ❤️ by 덕환이와 AI친구들</p>
    <p>🌈 오늘도 즐거운 코딩 되세요! 🌈</p>
</div>
""", unsafe_allow_html=True)
