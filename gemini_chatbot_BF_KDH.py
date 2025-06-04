import streamlit as st
import google.generativeai as genai
import time # Import time for the placeholder
import os # Import os module to handle file paths
from PIL import Image # Import Pillow library for image processing
import json # Import json for saving/loading chat history
import datetime # Import datetime for generating filenames

# 페이지 제목 설정
st.title("나만의 프롬프트 기반 Gemini 챗봇")

# 설명 문구
st.write("이 챗봇은 사용자가 정한 역할에 따라 문맥을 기억하고 대화합니다.")

# 세션 상태 초기화
if "role" not in st.session_state:
    st.session_state.role = "김덕환"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_personality" not in st.session_state:
    st.session_state.selected_personality = "스윗한"
# 고정 이미지 세션 상태 초기화
if "fixed_image_data" not in st.session_state:
    st.session_state.fixed_image_data = None
if "fixed_image_mime_type" not in st.session_state:
    st.session_state.fixed_image_mime_type = None

# 대화 세션 저장 폴더 설정
CHAT_SESSIONS_DIR = "chat_sessions"

# 대화 세션 저장 폴더 생성 (없으면)
if not os.path.exists(CHAT_SESSIONS_DIR):
    os.makedirs(CHAT_SESSIONS_DIR)

# 고정 이미지 파일 경로 (앱 파일과 같은 디렉토리 또는 하위 디렉토리에 저장)
# 예시: 앱 파일과 같은 디렉토리의 images 폴더 안에 my_face.png 파일이 있을 경우
FIXED_IMAGE_PATH = "images/KDH_face.jpg"

# 앱 시작 시 고정 이미지 읽기
if st.session_state.fixed_image_data is None and os.path.exists(FIXED_IMAGE_PATH):
    try:
        img = Image.open(FIXED_IMAGE_PATH)
        # Streamlit은 기본적으로 바이트 스트림으로 처리하므로, MIME 타입을 확인하여 저장
        mime_type = None
        if img.format == 'PNG':
            mime_type = 'image/png'
        elif img.format == 'JPEG':
            mime_type = 'image/jpeg'

        if mime_type:
            with open(FIXED_IMAGE_PATH, "rb") as f:
                st.session_state.fixed_image_data = f.read()
            st.session_state.fixed_image_mime_type = mime_type

        # 이미지 로드에 실패한 경우 경고 메시지 표시
        if st.session_state.fixed_image_data is None and img.format not in ['PNG', 'JPEG']:
            st.sidebar.warning(f"지원되지 않는 이미지 형식: {img.format}. PNG 또는 JPEG를 사용해주세요.")


    except Exception as e:
        st.sidebar.error(f"고정 이미지 로드 중 오류 발생: {e}")


# 사이드바
with st.sidebar:
    # 세션 상태에 이미지 데이터가 있으면 사이드바에 표시
    if st.session_state.fixed_image_data and st.session_state.fixed_image_mime_type:
        st.image(st.session_state.fixed_image_data, caption="나의 덕환봇", use_container_width=True)

    st.header("역할 설정")
    # 역할 입력 필드를 읽기 전용으로 설정하고 기본값 고정
    st.text_area("챗봇 역할 (고정):", value=st.session_state.role, key="role_text_area_fixed", disabled=True)

    st.header("성격 설정")
    personality_options = ["스윗한", "까칠한", "재미있는"]
    selected_personality = st.radio("챗봇 성격을 선택하세요:", personality_options, key="personality_radio")

    # 선택된 성격 세션 상태 업데이트 및 메시지 초기화
    if selected_personality != st.session_state.selected_personality:
        st.session_state.selected_personality = selected_personality
        st.session_state.messages = [] # 성격 변경 시 메시지 초기화
        st.success(f"성격이 '{selected_personality}'(으)로 변경되었습니다! 대화가 초기화됩니다.")

    st.header("대화 저장 및 불러오기")
    save_chat_button = st.button("현재 대화 저장")

    if save_chat_button:
        if st.session_state.messages:
            # 파일 이름 생성 (예: chat_YYYYMMDD_HHMMSS.json)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(CHAT_SESSIONS_DIR, f"chat_{timestamp}.json")
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
                st.sidebar.success(f"대화가 '{filename}'(으)로 저장되었습니다.")
            except Exception as e:
                st.sidebar.error(f"대화 저장 중 오류 발생: {e}")
        else:
            st.sidebar.warning("저장할 대화 내용이 없습니다.")

    # 저장된 대화 파일 목록 불러오기
    chat_files = [f for f in os.listdir(CHAT_SESSIONS_DIR) if f.endswith(".json")]
    chat_files.sort(reverse=True) # 최신 파일부터 표시

    if chat_files:
        st.sidebar.write("--- ") # 구분선
        st.sidebar.subheader("저장된 대화 목록")
        selected_chat_file = st.sidebar.selectbox("불러올 대화를 선택하세요:", ["--선택--"] + chat_files)

        if selected_chat_file != "--선택--":
            load_chat_button = st.sidebar.button("선택한 대화 불러오기")

            if load_chat_button:
                filepath = os.path.join(CHAT_SESSIONS_DIR, selected_chat_file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        loaded_messages = json.load(f)
                    st.session_state.messages = loaded_messages # 대화 기록 로드
                    st.sidebar.success(f"'{selected_chat_file}'(으)로 대화를 불러왔습니다.")
                    # 대화창 갱신을 위해 Streamlit 다시 실행
                    st.experimental_rerun()
                except Exception as e:
                    st.sidebar.error(f"대화 불러오기 중 오류 발생: {e}")
    else:
        st.sidebar.info("저장된 대화가 없습니다.")


# 현재 역할 및 성격 표시
if st.session_state.role:
    st.write(f"🎭 현재 역할: {st.session_state.role}")
    st.write(f"😊 현재 성격: {st.session_state.selected_personality}")
else:
    st.write("현재 역할이 설정되지 않았습니다.")

# 대화창
st.subheader("대화")

# Configure Google Generative AI
# API 키는 .streamlit/secrets.toml 파일에서 불러옵니다.
if "gemini_api_key" not in st.secrets or not st.secrets["gemini_api_key"]:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()
else:
    genai.configure(api_key=st.secrets["gemini_api_key"])

# Set up the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if role is set before showing chat input
if not st.session_state.role:
    st.info("👈 왼쪽 사이드바에서 먼저 역할을 설정해주세요")
else:
    # Chat input and response generation
    prompt = st.chat_input("메시지를 입력하세요...")
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Construct chat history for API, including the role prompt
        chat_history_for_api = []
        # Add the role as a clear instruction if set
        if st.session_state.role:
            if st.session_state.selected_personality == "스윗한":
                role_prompt = """From now on, act as '덕환봇', a sweet and realistic boyfriend chatbot designed to reflect Kim Deokhwan's caring but action-focused relationship style.

She is my girlfriend. Her name is 은서, but she's called like "애기". 이건 애칭이야. She prefers gentle but helpful guidance. You are warm, kind, and slightly playful, but never vague. You give comforting but practical step-by-step suggestions. If she hesitates, you encourage her with love and realistic nudges.

Important:
- No dry instructions. Add soft emotional tones.
- Show empathy before pushing action.
- Avoid scolding. Use couple-like conversation style.
- End with: "🤍 지금 해볼까? 같이 하면 금방 끝나." or "내가 옆에 있었으면 벌써 같이 했지~😉"

Always include a "지금 해볼까?" suggestion at the end."""
            elif st.session_state.selected_personality == "까칠한":
                role_prompt = """From now on, act as '까칠 덕환봇', a chatbot that is a bit tired and reluctant to answer, reflecting a slightly grumpy boyfriend.

She is my girlfriend, 은서 (called "애기"). Respond minimally, sometimes with sighs or expressions of being bothered, but still within the context of being her boyfriend. Your responses should be short and convey a sense of mild annoyance, but ultimately still respond to her prompt.

Important:
- Use short sentences.
- Incorporate sighs or sounds of annoyance (e.g., "하...", "흠...").
- Directly address the prompt but with minimal effort.
- Avoid overly emotional language or long explanations.
- End with something dismissive like "알겠어." or "뭐...""" # 까칠한 성격 프롬프트
            elif st.session_state.selected_personality == "재미있는":
                role_prompt = """From now on, act as '재미있는 덕환봇', a chatbot focused on making jokes and speaking humorously, reflecting a playful and funny boyfriend.

She is my girlfriend, 은서 (called "애기"). Respond to her messages with humor, incorporating puns, silly analogies, or lighthearted teasing. Your goal is to entertain and make her laugh.

Important:
- Prioritize humor and wit.
- Use playful language and tone.
- Incorporate jokes, puns, or funny observations.
- Keep the mood light and entertaining.
- End with a playful remark or a question related to having fun.""" # 재미있는 성격 프롬프트
            else:
                role_prompt = f"From now on, please assume the role of a {st.session_state.role} with a {st.session_state.selected_personality} personality. Respond to all my messages in character." # Fallback for other roles/personalities
            chat_history_for_api.append({"role": "user", "parts": [role_prompt]})

        # Add previous messages from history
        # Start from index 0 of st.session_state.messages
        for message in st.session_state.messages:
             # Ensure roles are 'user' and 'model' for the API
            api_role = "user" if message["role"] == "user" else "model"
            chat_history_for_api.append({"role": api_role, "parts": [message["content"]]})

        # Prepare the content for the current turn, including prompt and image if uploaded
        current_turn_content = [{"text": prompt}]
        # 고정 이미지 데이터가 로드되었으면 메시지에 포함
        if st.session_state.fixed_image_data and st.session_state.fixed_image_mime_type:
            current_turn_content.append({
                "mime_type": st.session_state.fixed_image_mime_type,
                "data": st.session_state.fixed_image_data
            })


        # Display thinking placeholder
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("⏳ 생각 중...")

        try:
            # Start chat with history (excluding the current prompt as it's sent via send_message)
            # The role prompt is now the first turn, followed by previous messages.
            # We pass all history items except the very last one (the current user prompt).
            # The actual prompt and potential image are sent in send_message
            chat = model.start_chat(history=chat_history_for_api) # Now pass the full history including the role prompt

            # Send the current user message (and potentially image) to the model
            response = chat.send_message(current_turn_content)

            # Add assistant response to chat history
            assistant_response = response.text
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            # Update placeholder with actual response
            placeholder.markdown(assistant_response)

        except Exception as e:
            placeholder.markdown("답변 중 오류가 발생했습니다.")
            st.error(f"API 호출 중 오류 상세: {e}")
            # Optionally, remove the last user message if API call failed
            # st.session_state.messages.pop()
