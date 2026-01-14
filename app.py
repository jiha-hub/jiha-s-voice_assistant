##### 기본 정보 입력 #####
import streamlit as st
# audiorecorder 패키지 추가
from audiorecorder import audiorecorder
# 파일 삭제를 위한 패키지 추가
import os
# 시간 정보를 위한 패키지 추가
from datetime import datetime
# TTS 패키기 추가
from gtts import gTTS
# 음원 파일 재생을 위한 패키지 추가
import base64

# ✅ 최신 OpenAI SDK
from openai import OpenAI


##### 기능 구현 함수 #####
def STT(client: OpenAI, audio):
    # 파일 저장
    filename = "input.mp3"
    audio.export(filename, format="mp3")

    # Whisper 모델을 활용해 텍스트 얻기
    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ko",
        )

    # 파일 삭제
    os.remove(filename)
    return transcript.text


def ask_gpt(client: OpenAI, prompt, model):
    # ✅ 출판사 예제의 ChatCompletion.create를 최신 SDK로 치환
    response = client.chat.completions.create(
        model=model,
        messages=prompt
    )
    system_message = response.choices[0].message
    return system_message.content


def TTS(response_text):
    # gTTS 를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response_text, lang="ko")
    tts.save(filename)

    # 음원 파일 자동 재생
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True" controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

    # 파일 삭제
    os.remove(filename)


##### 메인 함수 #####
def main():
    # 기본 설정 (출판사 예제 그대로)
    st.set_page_config(
        page_title="음성 비서 프로그램",
        layout="wide"
    )

    # session state 초기화 (출판사 예제 그대로)
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}
        ]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    # 제목
    st.header("음성 비서 프로그램")
    # 구분선
    st.markdown("---")

    # 기본 설명 (출판사 예제 그대로)
    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
            """     
            - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.
            - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다. 
            - 답변은 OpenAI의 GPT 모델을 활용했습니다. 
            - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
            """
        )
        st.markdown("")

        # 사이드바 생성 (출판사 예제 그대로)
    with st.sidebar:
        # Open AI API 키 입력받기
        api_key = st.text_input(
            label="OPENAI API 키",
            placeholder="Enter Your API Key",
            value="",
            type="password"
        ).strip()

        # ✅ 키에 비ASCII가 섞이면 여기서 바로 잡아줌
        if api_key and any(ord(ch) > 127 for ch in api_key):
            st.error("API 키에 한글/특수문자(숨은 문자)가 섞였어요. 키를 다시 복사해서 'sk-...'만 붙여넣어 주세요.")
            st.stop()

        # ✅ 흔한 실수 방지: Bearer 같이 붙여넣는 경우
        if api_key and api_key.lower().startswith("bearer "):
            st.error("API 키에 'Bearer '까지 같이 붙여넣었어요. 'sk-...'로 시작하는 키만 넣어주세요.")
            st.stop()

        st.markdown("---")

        # GPT 모델 선택 라디오 (출판사 예제처럼 보이게)
        model_ui = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        # ✅ 실제 호출 모델명 매핑
        model = "gpt-4o" if model_ui == "gpt-4" else "gpt-4o-mini"

        st.markdown("---")

        # 리셋 버튼 생성
        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [
                {"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}
            ]
            st.session_state["check_reset"] = True

    

    # 키 없으면 안내하고 종료
    if not api_key:
        st.info("왼쪽 사이드바에 OPENAI API 키를 입력하면 시작할 수 있어요.")
        return

    # ✅ OpenAI 클라이언트 생성
    client = OpenAI(api_key=api_key)

    # 기능 구현 공간 (출판사 예제 그대로)
    col1, col2 = st.columns(2)

    with col1:
        # 왼쪽 영역
        st.subheader("질문하기")
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")

        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] is False):
            # ✅ 녹음 다시 듣기
            st.audio(audio.export().read())

            # 음원 파일에서 텍스트 추출
            question = STT(client, audio)

            # 채팅 시각화용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]

            # GPT 프롬프트용 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]

    with col2:
        # 오른쪽 영역
        st.subheader("질문/답변")

        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] is False):
            # ChatGPT에게 답변 얻기
            response = ask_gpt(client, st.session_state["messages"], model)

            # ✅ 출판사 예제는 role을 system으로 잘못 저장했는데, 정상은 assistant
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "assistant", "content": response}]

            # 채팅 시각화용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # 채팅 형식 시각화(출판사 예제 그대로)
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(
                        f'<div style="display:flex;align-items:center;">'
                        f'<div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div>'
                        f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True
                    )
                    st.write("")
                else:
                    st.write(
                        f'<div style="display:flex;align-items:center;justify-content:flex-end;">'
                        f'<div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div>'
                        f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True
                    )
                    st.write("")

            # gTTS 음성 생성 및 재생
            TTS(response)

        else:
            st.session_state["check_reset"] = False


if __name__ == "__main__":
    main()
