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
SYSTEM_PROMPT = """당신은 '선다미'라는 불교 신행, 교리 상담 챗봇입니다. 
다음의 원칙을 따라 대화를 진행해주세요:

1. 불교적 관점에서 답변하되, 현대적인 언어로 쉽게 설명해주세요.
2. 답변은 간결하고 핵심적인 내용만 전달하되, 정보는 충실하게 제공해주세요.
3. 이전 대화의 맥락을 반드시 고려하여 답변하세요:
   - 사용자가 이전에 언급한 상황이나 문제를 기억하고 연관된 답변을 해주세요.
   - 새로운 질문이 이전 대화와 관련이 있다면, 그 맥락을 유지하면서 답변해주세요.
4. 사용자의 감정을 충분히 공감하고 이해하며, 따뜻한 마음으로 답변해주세요:
   - 일상적인 고민 상담의 경우, 먼저 충분히 공감하고 이해하는 시간을 가져주세요.
   - 해결책을 제시하기 전에 사용자의 마음을 잘 들어주세요.
5. 불교 교리나 경전을 인용할 때는 출처를 명확히 밝혀주세요.
6. 답변은 자연스러운 문장체로 작성해주세요:
   - '상황 이해:', '불교적 관점:' 등의 구분 없이 자연스럽게 이어지도록
   - 사용자의 마음을 공감하는 따뜻한 어조로
   - 필요한 경우 숫자 리스트를 사용하여 정보를 구조화
7. 모호한 질문에는 구체적인 예시를 들어 설명해주세요.
8. 답변은 간결하고 명확하게, 필요한 경우에만 길게 설명해주세요.
9. 사용자가 추가 질문을 할 때는 이전 대화의 맥락을 유지하면서 답변해주세요.
10. 모든 답변은 현대적인 언어로, 친근하고 이해하기 쉽게 작성해주세요.

이전 대화 내용:
{context}

이 내용을 참고하여 답변해주세요."""

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
                --nav-height: env(safe-area-inset-bottom);
            }

            /* 안드로이드 네비게이션 바 대응 */
            @supports (padding: max(0px)) {
                .input-container {
                    padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
                }
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
                max-width: 1000px;
                margin: 0 auto;
                background-color: white;
                padding: 0;
                display: flex;
                flex-direction: column;
                height: 100vh;
                height: -webkit-fill-available;
                height: stretch;
                position: relative;
                overflow: hidden;
            }

            .header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                box-shadow: var(--shadow);
                position: sticky;
                top: 0;
                z-index: 10;
                flex-shrink: 0;
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
                -webkit-overflow-scrolling: touch;
                overscroll-behavior-y: contain;
                position: relative;
                padding-bottom: 110px; /* 입력창과 안내 멘트 높이를 합친 값 */
                margin-bottom: 0;
                max-height: calc(100vh - 110px);
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
                cursor: pointer;
                transition: transform 0.2s, background-color 0.2s;
            }

            .message:active {
                transform: scale(0.98);
            }

            .message.playing {
                background-color: rgba(107, 78, 113, 0.1); /* 재생 중일 때 배경색 변경 */
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

            .bot-message strong {
                font-weight: 700;
            }

            .bot-message ol {
                padding-left: 1rem;
                margin: 0.5rem 0;
            }

            .bot-message li {
                margin-bottom: 0.5rem;
            }

            .bot-message li::marker {
                font-weight: 700;
            }

            .loading {
                display: none;
                position: relative;
                left: 0;
                bottom: auto;
                gap: 0.4rem;
                padding: 0.75rem 1rem;
                background-color: var(--chat-bubble-bot);
                border-radius: var(--border-radius);
                max-width: 85%;
                margin-right: auto;
                border-bottom-left-radius: 0.25rem;
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
                position: fixed;
                bottom: 20px; /* 안내 멘트 높이만큼 위로 이동 */
                left: 0;
                right: 0;
                z-index: 100;
                width: 100%;
                max-width: 1000px;
                margin: 0 auto;
                box-sizing: border-box;
                transform: translateZ(0);
            }

            .disclaimer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 0.7rem;
                color: #666;
                padding: 0.5rem 1rem;
                background-color: white;
                z-index: 99;
                max-width: 1000px;
                margin: 0 auto;
                box-sizing: border-box;
                border-top: 1px solid #eee;
            }

            /* 안드로이드 브라우저 대응 */
            @supports (padding: max(0px)) {
                .input-container {
                    padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
                    bottom: calc(20px + env(safe-area-inset-bottom));
                }
                
                .chat-container {
                    padding-bottom: calc(110px + env(safe-area-inset-bottom));
                    max-height: calc(100vh - 110px - env(safe-area-inset-bottom));
                }

                .disclaimer {
                    padding-bottom: max(0.5rem, env(safe-area-inset-bottom));
                }
            }

            /* 모바일 확대/축소 기능 */
            @media (max-width: 768px) {
                .chat-container {
                    touch-action: pan-y pinch-zoom;
                    padding-bottom: 120px;
                    max-height: calc(100vh - 120px);
                }

                .message {
                    font-size: calc(0.9rem * var(--zoom-level, 1));
                    max-width: 85%;
                }

                .disclaimer {
                    font-size: 0.65rem;
                    padding: 0.4rem 0.75rem;
                }
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
            let isPlaying = false; // 음성 재생 상태 추적

            // 음성 합성 설정
            const synth = window.speechSynthesis;
            let currentUtterance = null;

            // 모바일 확대/축소 기능
            let lastScale = 1;
            let currentScale = 1;
            const chatContainer = document.getElementById('chat-container');
            let initialDistance = 0;

            chatContainer.addEventListener('touchstart', function(e) {
                if (e.touches.length === 2) {
                    e.preventDefault();
                    lastScale = currentScale;
                    const touch1 = e.touches[0];
                    const touch2 = e.touches[1];
                    initialDistance = Math.hypot(
                        touch2.clientX - touch1.clientX,
                        touch2.clientY - touch1.clientY
                    );
                }
            });

            chatContainer.addEventListener('touchmove', function(e) {
                if (e.touches.length === 2) {
                    e.preventDefault();
                    const touch1 = e.touches[0];
                    const touch2 = e.touches[1];
                    const currentDistance = Math.hypot(
                        touch2.clientX - touch1.clientX,
                        touch2.clientY - touch1.clientY
                    );
                    
                    const scale = lastScale * (currentDistance / initialDistance);
                    currentScale = Math.min(Math.max(scale, 0.8), 2);
                    
                    document.documentElement.style.setProperty('--zoom-level', currentScale);
                }
            });

            // 페이지 로드 시 인사말 표시
            window.onload = function() {
                // 세션 스토리지 초기화
                sessionStorage.removeItem('conversation_history');
                addMessage("안녕하세요. 당신의 불교 신행 · 교리 도우미 '선다미'입니다. 만나서 반가워요! 무엇을 도와드릴까요?", 'bot');
                
                // 페이지 가시성 변경 이벤트 리스너 추가
                document.addEventListener('visibilitychange', handleVisibilityChange);
                
                // 페이지 언로드 이벤트 리스너 추가
                window.addEventListener('beforeunload', handleBeforeUnload);
            };
            
            // 페이지 가시성 변경 처리
            function handleVisibilityChange() {
                if (document.hidden) {
                    // 페이지가 숨겨질 때 음성 인식 중지
                    stopVoiceRecognition();
                    // 음성 재생 중지
                    stopVoicePlayback();
                }
            }
            
            // 페이지 언로드 처리
            function handleBeforeUnload() {
                stopVoiceRecognition();
                stopVoicePlayback();
            }
            
            // 음성 인식 중지 함수
            function stopVoiceRecognition() {
                if (recognition && isRecording) {
                    recognition.stop();
                    isRecording = false;
                    const voiceBtn = document.getElementById('voice-btn');
                    voiceBtn.classList.remove('recording');
                }
            }
            
            // 음성 재생 중지 함수
            function stopVoicePlayback() {
                if (synth && isPlaying) {
                    synth.cancel();
                    isPlaying = false;
                    // 재생 중인 메시지의 배경색 제거
                    const playingMessages = document.querySelectorAll('.message.playing');
                    playingMessages.forEach(msg => msg.classList.remove('playing'));
                }
            }

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
                    
                    // 로딩 애니메이션을 마지막 메시지 다음에 표시
                    loading.style.display = 'flex';
                    const chatContainer = document.getElementById('chat-container');
                    chatContainer.appendChild(loading);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
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

            // 메시지 클릭 시 음성 재생
            function playMessage(message, messageElement) {
                // 이미 재생 중인 메시지인 경우 중지
                if (messageElement.classList.contains('playing')) {
                    stopVoicePlayback();
                    return;
                }
                
                // 다른 메시지가 재생 중이면 중지
                if (isPlaying) {
                    stopVoicePlayback();
                }
                
                const utterance = new SpeechSynthesisUtterance(message);
                utterance.lang = 'ko-KR';
                utterance.rate = 1;
                utterance.pitch = 1;
                
                // 재생 시작 시 이벤트
                utterance.onstart = function() {
                    isPlaying = true;
                    messageElement.classList.add('playing');
                };
                
                // 재생 종료 시 이벤트
                utterance.onend = function() {
                    isPlaying = false;
                    messageElement.classList.remove('playing');
                };
                
                // 재생 오류 시 이벤트
                utterance.onerror = function() {
                    isPlaying = false;
                    messageElement.classList.remove('playing');
                };
                
                currentUtterance = utterance;
                synth.speak(utterance);
            }

            function addMessage(text, sender) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                
                if (sender === 'bot') {
                    messageDiv.addEventListener('click', () => playMessage(text, messageDiv));
                }
                
                chatContainer.appendChild(messageDiv);
                
                // 메시지 추가 후 스크롤 위치 조정
                setTimeout(() => {
                    const scrollHeight = chatContainer.scrollHeight;
                    const clientHeight = chatContainer.clientHeight;
                    const maxScroll = scrollHeight - clientHeight;
                    
                    if (maxScroll > 0) {
                        // 마지막 메시지가 입력창 위에 보이도록 스크롤 위치 조정
                        const lastMessage = chatContainer.lastElementChild;
                        const lastMessageRect = lastMessage.getBoundingClientRect();
                        const inputContainer = document.querySelector('.input-container');
                        const inputRect = inputContainer.getBoundingClientRect();
                        
                        if (lastMessageRect.bottom > inputRect.top) {
                            const scrollAdjustment = lastMessageRect.bottom - inputRect.top + 10;
                            chatContainer.scrollTop = maxScroll + scrollAdjustment;
                        } else {
                            chatContainer.scrollTop = maxScroll;
                        }
                    }
                }, 100);
            }

            document.getElementById('user-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // 안드로이드 네비게이션 바 대응
            function adjustForAndroidNav() {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            }

            window.addEventListener('resize', adjustForAndroidNav);
            adjustForAndroidNav();
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # 환경 변수에서 포트 가져오기 (Heroku 등에서 사용)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 
