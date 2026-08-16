import time
import threading
from flask import Flask
import requests

# 1. Render 유지용 웹 서버
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# -------------------------------------------------------------
# 2. 설정
# -------------------------------------------------------------
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1538586452664000543/YlO8otTVQh0cw3JJzMp7gAEPtYS7WUzMX2Ewk3o1cL8YpkKttktgNHlG1LkxC9nd0cdL'

CHZZK_CHANNEL_ID = 'a6c4ddb09cdb160478996007bff35296'
TWITTER_USER_ID = 'ArahashiTabi'
INSTA_USER_ID = 'tabi_dayo3o'

last_chzzk_status = False

def send_discord_alarm(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message})
    except Exception as e:
        print(f'디스코드 전송 실패: {e}', flush=True)

# -------------------------------------------------------------
# 3. 개별 점검 함수들
# -------------------------------------------------------------
def check_chzzk():
    global last_chzzk_status
    try:
        url = f'https://api.chzzk.naver.com/polling/v2/channels/{CHZZK_CHANNEL_ID}/live-status'
        # timeout=10 추가 (10초 이상 응답 없으면 대기 강제 종료 후 다음 주기로 이동)
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).json()
        status = res.get('content', {}).get('status')

        if status == 'OPEN' and not last_chzzk_status:
            title = res.get('content', {}).get('liveTitle', '제목 없음')
            send_discord_alarm(
                f'🔴 **[치지직]** 뱅온! 방송이 시작되었습니다!\n제목: {title}\nhttps://chzzk.naver.com/live/{CHZZK_CHANNEL_ID}'
            )
            last_chzzk_status = True
        elif status == 'CLOSE':
            last_chzzk_status = False
    except Exception as e:
        print(f'치지직 점검 에러: {e}', flush=True)

def check_twitter():
    pass

def check_instagram():
    pass

# -------------------------------------------------------------
# 4. 30초마다 실행되는 메인 루프
# -------------------------------------------------------------
def main_loop():
    print("모니터링 시작! (30초 주기)", flush=True)
    send_discord_alarm("🤖 **[알림]** 모니터링 봇이 성공적으로 시작되었습니다!")
    
    while True:
        print("점검 진행 중...", flush=True)
        check_chzzk()
        check_twitter()
        check_instagram()
        time.sleep(30)

# -------------------------------------------------------------
# 5. 실행부
# -------------------------------------------------------------
if __name__ == '__main__':
    # Flask 서버를 백그라운드로 실행
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # 모니터링 실행
    main_loop()
