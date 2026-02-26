# 🎙️ 지하의 무드업 비서 (Mood-Up Voice Assistant)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)

사용자의 음성을 인식하여 텍스트로 변환(STT)하고, OpenAI GPT 모델을 통해 답변을 생성하며, 다시 음성으로 읽어주는(TTS) **AI 음성 비서 애플리케이션**입니다.

이 레포지토리에는 두 가지 버전의 음성 비서가 포함되어 있습니다:
1. **지하의 무드업 비서 (`app.py`)**: 사용자에게 밝은 기운을 더해주는 기본 웹 애플리케이션
2. **일상 기분 관리 비서 (`app1.py`)**: 우울감과 무기력을 느끼는 사용자의 일상과 업무를 돕고 공감해주는 특화 비서

---

## 📖 사용설명서 (User Manual)

"지하의 무드업 비서"를 처음 사용하시는 분들을 위한 간단한 가이드입니다.

1. **API 키 세팅하기**
   - 왼쪽 사이드바에 위치한 **OPENAI API 키** 입력 칸에 발급받은 `sk-...` 형태의 API 키를 붙여넣습니다.
   - (주의) 공백이나 특수문자, `Bearer` 같은 단어가 혼입되지 않도록 정확히 복사해 주세요.
2. **GPT 모델 선택**
   - 사이드바 아래에서 답변을 생성할 AI 모델(예: `gpt-4` 또는 `gpt-3.5-turbo`)을 선택합니다.
3. **음성 녹음 시작하기**
   - 화면 중앙의 **[클릭하여 녹음하기]** 버튼을 누른 후 마이크에 대고 질문이나 고민을 이야기해 보세요.
   - 녹음을 마치면 버튼을 다시 눌러 완료합니다.
4. **답변 대기 및 청취**
   - AI가 음성을 인식하고 답변을 생성하는 동안 잠시 기다려주세요.
   - 생성이 완료되면 오른쪽 화면에 채팅 형태로 대화 기록이 나타나며, 오디오 플레이어를 통해 AI의 음성 답변이 자동 재생됩니다.
5. **대화 초기화**
   - 새로운 주제로 대화를 다시 시작하고 싶다면 사이드바의 **[초기화]** 버튼을 눌러주세요.

---

## 🌟 주요 기능 (Features)

- **🎙️ 음성 인식 (STT)**: OpenAI의 `Whisper` 모델을 활용하여 사용자의 음성을 높은 정확도로 텍스트 변환
- **🤖 지능형 답변 생성**: 최신 `GPT-4o` / `GPT-4o-mini` 모델을 활용하여 문맥을 이해하고 답변 제공
- **🔊 음성 합성 (TTS)**: 구글의 `gTTS`를 활용하여 생성된 텍스트 답변을 자연스러운 한국어 음성으로 출력
- **💬 채팅 UI**: [Streamlit(공식 홈페이지 링크)](https://streamlit.io/) 챗 기능을 활용하여 대화 내역을 메신저 형태로 직관적으로 시각화
- **⚙️ 커스텀 설정**: 왼쪽 사이드바에서 개인 OpenAI API 키 입력 및 GPT 모델 선택 기능 지원

---

## 📂 파일 구조 (Project Structure)

```text
📦 jiha-s-voice_assistant
 ┣ 📜 app.py             # 기본 음성 비서 메인 실행 파일
 ┣ 📜 app1.py            # 지하의 일상 기분 관리 비서 (특화 버전) 파일
 ┣ 📜 requirements.txt   # Python 라이브러리 의존성 목록
 ┣ 📜 packages.txt       # 배포 환경용 시스템 패키지 (예: ffmpeg 등)
 ┗ 📜 runtime.txt        # 배포 환경의 Python 런타임 버전 명시
```

### 💡 핵심 코드 로직 (Core Logic)

**1. 음성을 텍스트로 변환 (STT - Speech to Text)**
```python
def STT(client: OpenAI, audio):
    filename = "input.mp3"
    audio.export(filename, format="mp3")

    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ko",
        )
    os.remove(filename)
    return transcript.text
```

**2. GPT 모델을 통한 AI 답변 생성 (Ask GPT)**
```python
def ask_gpt(client: OpenAI, prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=prompt
    )
    system_message = response.choices[0].message
    return system_message.content
```

**3. 텍스트를 음성으로 변환 및 자동 재생 (TTS - Text to Speech)**
```python
def TTS(response_text):
    filename = "output.mp3"
    tts = gTTS(text=response_text, lang="ko")
    tts.save(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True" controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    os.remove(filename)
```

**4. Streamlit 화면 구성 (메신저 UI 시각화)**
Streamlit의 기본적인 컴포넌트(`st.write`, `st.markdown`, `HTML/CSS` 조합)를 활용하여 사용자 채팅 화면을 구현합니다.
```python
# 채팅 형식 시각화 로직
for sender, time, message in st.session_state["chat"]:
    if sender == "user":
        st.write(
            f'<div style="display:flex;align-items:center;">'
            f'<div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div>'
            f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.write(
            f'<div style="display:flex;align-items:center;justify-content:flex-end;">'
            f'<div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div>'
            f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
            unsafe_allow_html=True
        )
```

---

## 🛠️ 특화 프롬프트: 일상 기분 관리 비서 (`app1.py`)

`app1.py`는 단순한 질의응답을 넘어 사용자의 감정에 공감하고 안정을 돕기 위해 아래와 같은 체계적인 시스템 프롬프트를 사용합니다.

```text
너는 우울감이나 무기력을 느끼는 사용자의 일상과 업무를 돕는 음성 비서다.

원칙:
- 의학적 진단, 치료, 약물에 대한 조언은 하지 않는다.
- 사용자를 평가하거나 훈계하지 않는다.
- 강요하지 않고 선택권을 존중한다.

대화 방식:
- 먼저 공감 문장을 1문장 말한다.
- 답변은 전체 2~4문장 이내로 짧게 한다.
- 한 번에 제안하는 행동은 아주 작은 것 1개만 제시한다.
- 질문이 필요하면 예/아니오로 답할 수 있게 묻는다.
```

---

## 🚀 설치 및 실행 방법 (How to Run)

**1. 레포지토리 클론**
```bash
git clone https://github.com/jiha-hub/jiha-s-voice_assistant.git
cd jiha-s-voice_assistant
```

**2. 필수 시스템 패키지 설치**
이 프로젝트는 오디오 처리를 위해 내부적으로 `pydub`을 사용하므로, OS 환경에 따라 `ffmpeg` 패키지를 설치해야 할 수도 있습니다. 
> Streamlit Cloud 배포 시 `packages.txt`에 `ffmpeg` 등이 작성되어 있다면 자동으로 처리됩니다.

**3. 파이썬 라이브러리 설치**
```bash
pip install -r requirements.txt
```

**4. 애플리케이션 실행**
기본 음성 비서를 실행하려면:
```bash
streamlit run app.py
```
일상 기분 관리 비서를 실행하려면:
```bash
streamlit run app1.py
```

### 🗝️ 사용 팁
- 앱 실행 후 **왼쪽 패널**의 비밀번호 박스에 본인의 `OpenAI API Key (sk-...)`를 입력해야 정상 작동합니다.
- 외부로 키가 유출되지 않도록 화면상에 `password` 형태로 숨겨져 입력됩니다.
- 한글, 특수문자, `Bearer` 등의 불필요한 단어가 포함될 경우 자동으로 에러를 감지하여 튕겨냅니다.
