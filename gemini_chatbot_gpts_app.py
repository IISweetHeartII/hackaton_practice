import streamlit as st
import google.generativeai as genai
import time # Import time for the placeholder

# 페이지 제목 설정
st.title("나만의 프롬프트 기반 Gemini 챗봇")

# 설명 문구
st.write("이 챗봇은 사용자가 정한 역할에 따라 문맥을 기억하고 대화합니다.")

# 세션 상태 초기화
if "role" not in st.session_state:
    st.session_state.role = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("역할 설정")
    role_input = st.text_area("챗봇에게 부여할 역할을 입력하세요:", value=st.session_state.role, key="role_text_area")
    apply_button = st.button("역할 적용")

    if apply_button:
        st.session_state.role = st.session_state.role_text_area
        st.session_state.messages = [] # Clear messages on role change
        st.success("역할이 적용되었습니다! 대화가 초기화됩니다.")

# 현재 역할 표시
if st.session_state.role:
    st.write(f"🎭 현재 역할: {st.session_state.role}")
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
            chat_history_for_api.append({"role": "user", "parts": [f"From now on, please assume the role of a {st.session_state.role}. Respond to all my messages in character."]})

        # Add previous messages from history
        # Start from index 0 of st.session_state.messages
        for message in st.session_state.messages:
             # Ensure roles are 'user' and 'model' for the API
            api_role = "user" if message["role"] == "user" else "model"
            chat_history_for_api.append({"role": api_role, "parts": [message["content"]]})

        # Display thinking placeholder
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("⏳ 생각 중...")

        try:
            # Start chat with history (excluding the current prompt as it's sent via send_message)
            # The role prompt is now the first turn, followed by previous messages.
            # We pass all history items except the very last one (the current user prompt).
            chat = model.start_chat(history=chat_history_for_api[:-1]) # Exclude the current prompt

            # Send the current user message to the model
            response = chat.send_message(prompt)

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
