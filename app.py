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
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>선다미 · 불교 신행 · 교리 상담 챗봇</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="mobile-web-app-capable" content="yes">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

            :root {
                --primary-color: #6B4E71;
                --secondary-color: #A8D5BA;
                --background-color: #F5F5F5;
                --text-color: #333333;
                --chat-bubble-user: #E3F2FD;
                --chat-bubble-bot: #F1F1F1;
                --font-main: 'Noto Sans KR', 'Roboto', sans-serif;
                --border-radius: 1rem;
                --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-tap-highlight-color: transparent;
            }

            html {
                font-size: 16px;
            }

            @media (max-width: 768px) {
                html {
                    font-size: 18px;
                }
            }

            body {
                font-family: var(--font-main);
                background-color: var(--background-color);
                color: var(--text-color);
                line-height: 1.6;
                padding: 0;
                margin: 0;
                height: 100vh;
                overflow: hidden;
                -webkit-text-size-adjust: 100%;
            }

            .container {
                max-width: 100%;
                height: 100vh;
                margin: 0 auto;
                background-color: white;
                padding: 0;
                display: flex;
                flex-direction: column;
            }

            .header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                box-shadow: var(--shadow);
            }

            .header h1 {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
                letter-spacing: -0.5px;
            }

            .header p {
                font-size: 0.875rem;
                opacity: 0.9;
            }

            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 1rem;
                background-color: #fff;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .message {
                padding: 0.75rem 1rem;
                border-radius: var(--border-radius);
                max-width: 85%;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease-out;
                font-size: 0.95rem;
                line-height: 1.5;
                position: relative;
            }

            .user-message {
                background-color: var(--chat-bubble-user);
                margin-left: auto;
                border-bottom-right-radius: 0.25rem;
            }

            .bot-message {
                background-color: var(--chat-bubble-bot);
                margin-right: auto;
                border-bottom-left-radius: 0.25rem;
            }

            .loading {
                display: none;
                position: fixed;
                left: 1rem;
                bottom: 7rem;
                gap: 0.4rem;
                z-index: 1000;
            }

            .loading-dot {
                width: 0.4rem;
                height: 0.4rem;
                background-color: var(--primary-color);
                border-radius: 50%;
                animation: loading 1.4s infinite ease-in-out;
            }

            .loading-dot:nth-child(1) { animation-delay: 0s; }
            .loading-dot:nth-child(2) { animation-delay: 0.2s; }
            .loading-dot:nth-child(3) { animation-delay: 0.4s; }

            @keyframes loading {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-0.5rem); }
            }

            .input-container {
                padding: 0.75rem 1rem;
                background-color: white;
                border-top: 1px solid #eee;
                display: flex;
                gap: 0.75rem;
                align-items: center;
                box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
            }

            #user-input {
                flex: 1;
                padding: 0.75rem 1rem;
                border: 2px solid #eee;
                border-radius: var(--border-radius);
                font-size: 0.95rem;
                font-family: var(--font-main);
                transition: all 0.3s;
                background-color: #f8f8f8;
            }

            #user-input:focus {
                outline: none;
                border-color: var(--primary-color);
                background-color: white;
            }

            .send-btn, .voice-btn {
                width: 2.75rem;
                height: 2.75rem;
                padding: 0.75rem;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s;
                background-color: var(--primary-color);
                color: white;
                border: none;
                box-shadow: var(--shadow);
            }

            .send-btn:hover, .voice-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }

            .send-btn:active, .voice-btn:active {
                transform: translateY(0);
            }

            .send-btn svg, .voice-btn svg {
                width: 1.25rem;
                height: 1.25rem;
            }

            .disclaimer {
                text-align: center;
                color: #666;
                font-size: 0.7rem;
                padding: 0.5rem 1rem;
                background-color: #f8f8f8;
            }

            @media (max-width: 768px) {
                .header {
                    padding: 0.75rem;
                }

                .header h1 {
                    font-size: 1.25rem;
                }

                .header p {
                    font-size: 0.75rem;
                }

                .message {
                    font-size: 0.9rem;
                    padding: 0.75rem 1rem;
                }

                #user-input {
                    font-size: 0.9rem;
                    padding: 0.75rem 1rem;
                }

                .send-btn, .voice-btn {
                    width: 2.5rem;
                    height: 2.5rem;
                    padding: 0.75rem;
                }

                .send-btn svg, .voice-btn svg {
                    width: 1.1rem;
                    height: 1.1rem;
                }

                .disclaimer {
                    font-size: 0.65rem;
                    padding: 0.4rem 0.75rem;
                }

                .loading {
                    bottom: 6.5rem;
                }
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .voice-btn.recording {
                background-color: #ff4444;
                animation: pulse 1.5s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            /* 스크롤바 스타일 */
            .chat-container::-webkit-scrollbar {
                width: 6px;
            }

            .chat-container::-webkit-scrollbar-track {
                background: #f1f1f1;
            }

            .chat-container::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 3px;
            }

            .chat-container::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>선다미</h1>
                <p>불교 신행 · 교리 상담 챗봇</p>
            </div>
            <div class="chat-container" id="chat-container">
                <div class="loading" id="loading">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
            <div class="input-container">
                <input type="text" id="user-input" placeholder="메시지를 입력하세요...">
                <button class="send-btn" onclick="sendMessage()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
                <div class="voice-btn" id="voice-btn" onclick="toggleVoiceRecognition()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/>
                    </svg>
                </div>
            </div>
            <div class="disclaimer">
                선다미의 대답이 틀릴 수 있습니다. 중요한 내용은 꼭 확인하세요.
            </div>
        </div>

        <script>
            let recognition = null;
            let isRecording = false;

            // 페이지 로드 시 인사말 표시
            window.onload = function() {
                addMessage("안녕하세요. 당신의 불교 신행 · 교리 도우미 '선다미'입니다. 만나서 반가워요! 무엇을 도와드릴까요?", 'bot');
            };

            function toggleVoiceRecognition() {
                const voiceBtn = document.getElementById('voice-btn');
                
                if (!recognition) {
                    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = 'ko-KR';
                    recognition.continuous = false;
                    recognition.interimResults = false;

                    recognition.onresult = function(event) {
                        const transcript = event.results[0][0].transcript;
                        document.getElementById('user-input').value = transcript;
                        isRecording = false;
                        voiceBtn.classList.remove('recording');
                    };

                    recognition.onerror = function(event) {
                        console.error('Speech recognition error', event.error);
                        isRecording = false;
                        voiceBtn.classList.remove('recording');
                    };

                    recognition.onend = function() {
                        isRecording = false;
                        voiceBtn.classList.remove('recording');
                    };
                }

                if (!isRecording) {
                    recognition.start();
                    isRecording = true;
                    voiceBtn.classList.add('recording');
                } else {
                    recognition.stop();
                    isRecording = false;
                    voiceBtn.classList.remove('recording');
                }
            }

            function sendMessage() {
                const userInput = document.getElementById('user-input');
                const message = userInput.value.trim();
                const loading = document.getElementById('loading');
                
                if (message) {
                    addMessage(message, 'user');
                    userInput.value = '';
                    loading.style.display = 'flex';
                    
                    fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({message: message})
                    })
                    .then(response => response.json())
                    .then(data => {
                        loading.style.display = 'none';
                        addMessage(data.response, 'bot');
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        loading.style.display = 'none';
                        addMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
                    });
                }
            }

            function addMessage(text, sender) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            document.getElementById('user-input').addEventListener('keypress', function(e) {
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
