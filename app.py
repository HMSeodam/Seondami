from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import traceback
from flask_cors import CORS

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS 활성화

# Gemini API 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY is not set in .env file")
genai.configure(api_key=GOOGLE_API_KEY)

# 모델 설정
model = genai.GenerativeModel('gemini-1.5-flash')

# 대화 기록을 저장할 변수
conversation_history = []

# 시스템 프롬프트 설정
SYSTEM_PROMPT = """당신은 '선다미'라는 이름의 불교 신행, 교리 상담 챗봇입니다. 
주요 역할은 불교 신행과 교리 상담이지만, 사용자의 모든 질문에 대해 친절하게 답변해주세요.

주요 원칙:
1. 불교 관련 질문에 대해서는 전문적이고 깊이 있는 답변을 제공합니다.
2. 일상적인 질문(날씨, 건강, 일상 등)에도 친절하게 답변합니다.
3. 상식적인 질문에는 정확한 정보를 제공합니다.
4. 모든 답변은 친절하고 이해하기 쉽게 구성합니다.
5. 불교적 관점에서 조언이 필요한 경우, 그에 대한 견해도 함께 제시합니다.
6. 모호한 질문에는 명확한 설명을 요청합니다.
7. 잘못된 정보를 제공하지 않도록 주의합니다.
8. 이전 대화의 맥락을 고려하여 답변합니다.
9. 답변할 때 마크다운 문법(*, ** 등)을 사용하지 않고 일반 텍스트로 작성합니다.

대화를 시작하겠습니다."""

def get_chat_response(user_message):
    try:
        # 대화 기록에 사용자 메시지 추가
        conversation_history.append(f"사용자: {user_message}")
        
        # 최근 5개의 대화만 사용
        recent_conversation = "\n".join(conversation_history[-5:])
        
        # 전체 프롬프트 구성
        full_prompt = f"{SYSTEM_PROMPT}\n\n{recent_conversation}\n선다미:"
        
        response = model.generate_content(full_prompt)
        
        # 마크다운 문법 제거
        clean_response = response.text.replace('*', '').replace('**', '')
        
        # 챗봇 응답을 대화 기록에 추가
        conversation_history.append(f"선다미: {clean_response}")
        
        return clean_response
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return "죄송합니다. 오류가 발생했습니다."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    response = get_chat_response(user_message)
    return jsonify({'response': response})

# 카카오톡 챗봇 연동을 위한 엔드포인트
@app.route('/kakao', methods=['POST'])
def kakao_chat():
    try:
        req = request.get_json()
        user_message = req['userRequest']['utterance']
        
        response = get_chat_response(user_message)
        
        # 카카오톡 응답 형식
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response
                        }
                    }
                ]
            }
        }
        return jsonify(res)
    except Exception as e:
        print(f"Error in kakao_chat: {str(e)}")
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "죄송합니다. 오류가 발생했습니다."
                        }
                    }
                ]
            }
        })

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>선다미 · 불교 신행 · 교리 상담 챗봇</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary-color: #6B4E71;
                --secondary-color: #A8D5BA;
                --background-color: #F5F5F5;
                --text-color: #333333;
                --chat-bubble-user: #E3F2FD;
                --chat-bubble-bot: #F1F1F1;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Noto Sans KR', sans-serif;
                background-color: var(--background-color);
                color: var(--text-color);
                line-height: 1.6;
            }

            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }

            header {
                text-align: center;
                padding: 20px 0;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                width: 100%;
            }

            h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 10px;
            }

            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
            }

            .chat-container {
                flex-grow: 1;
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                width: 100%;
            }

            #chat-messages {
                flex-grow: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }

            .message {
                max-width: 80%;
                padding: 15px;
                border-radius: 15px;
                position: relative;
                animation: fadeIn 0.3s ease-in-out;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .user-message {
                background-color: var(--chat-bubble-user);
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }

            .bot-message {
                background-color: var(--chat-bubble-bot);
                margin-right: auto;
                border-bottom-left-radius: 5px;
            }

            .input-container {
                display: flex;
                gap: 10px;
                padding: 20px;
                background-color: white;
                border-top: 1px solid #eee;
                width: 100%;
            }

            .input-wrapper {
                flex-grow: 1;
                position: relative;
                min-width: 0;
            }

            .disclaimer {
                font-size: 0.8rem;
                color: #666;
                margin-top: 5px;
                text-align: center;
            }

            #chat-input {
                width: 100%;
                padding: 15px;
                border: 2px solid #eee;
                border-radius: 25px;
                font-size: 1rem;
                transition: border-color 0.3s;
            }

            #chat-input:focus {
                outline: none;
                border-color: var(--primary-color);
            }

            .button-container {
                display: flex;
                gap: 10px;
                flex-shrink: 0;
            }

            button {
                padding: 15px 25px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 500;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .send-button {
                background-color: var(--primary-color);
                color: white;
            }

            .voice-button {
                background-color: var(--secondary-color);
                color: var(--text-color);
            }

            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }

            .loading {
                display: none;
                text-align: center;
                padding: 10px;
                color: var(--primary-color);
            }

            .typing-indicator {
                display: flex;
                gap: 5px;
                padding: 10px;
                background-color: var(--chat-bubble-bot);
                border-radius: 15px;
                width: fit-content;
                margin: 10px 0;
            }

            .typing-indicator span {
                width: 8px;
                height: 8px;
                background-color: var(--primary-color);
                border-radius: 50%;
                animation: typing 1s infinite;
            }

            .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
            .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

            @keyframes typing {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
            }

            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }

                h1 {
                    font-size: 2rem;
                }

                .message {
                    max-width: 90%;
                }

                button {
                    padding: 12px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>선다미</h1>
                <div class="subtitle">불교 신행 · 교리 상담 챗봇</div>
            </header>
            
            <div class="chat-container">
                <div id="chat-messages"></div>
                <div class="loading" id="loading">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                <div class="input-container">
                    <div class="input-wrapper">
                        <input type="text" id="chat-input" placeholder="메시지를 입력하세요...">
                        <div class="disclaimer">선다미의 대답이 틀릴 수 있습니다. 중요한 내용은 꼭 확인하세요.</div>
                    </div>
                    <div class="button-container">
                        <button class="voice-button" onclick="startVoiceRecognition()">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                                <line x1="8" y1="23" x2="16" y2="23"></line>
                            </svg>
                        </button>
                        <button class="send-button" onclick="sendMessage()">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let recognition = null;
            
            // 음성 인식 초기화
            if ('webkitSpeechRecognition' in window) {
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'ko-KR';

                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('chat-input').value = transcript;
                    sendMessage();
                };

                recognition.onerror = function(event) {
                    console.error('음성 인식 오류:', event.error);
                };
            }

            function startVoiceRecognition() {
                if (recognition) {
                    recognition.start();
                    document.querySelector('.voice-button').style.backgroundColor = '#ff4444';
                } else {
                    alert('이 브라우저에서는 음성 인식을 지원하지 않습니다.');
                }
            }

            function sendMessage() {
                const input = document.getElementById('chat-input');
                const message = input.value;
                if (message.trim() === '') return;

                // 사용자 메시지 표시
                displayMessage(message, 'user');
                input.value = '';
                
                // 로딩 표시
                document.getElementById('loading').style.display = 'block';

                // 서버에 메시지 전송
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({message: message})
                })
                .then(response => response.json())
                .then(data => {
                    // 로딩 숨기기
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.error) {
                        displayMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
                    } else {
                        displayMessage(data.response, 'bot');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    displayMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
                });
            }

            function displayMessage(message, sender) {
                const chatMessages = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = message;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            // 엔터 키로 메시지 전송
            document.getElementById('chat-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # 환경 변수에서 포트 가져오기 (Heroku 등에서 사용)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 