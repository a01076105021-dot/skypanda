import time
import threading
from flask import Flask
import requests

# 1. Render 슬립 방지용 웹 서버
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# -------------------------------------------------------------
# 2. 설정 및 알림 함수
# -------------------------------------------------------------
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1538586452664000543/YlO8otTVQh0cw3JJzMp7gAEPtYS7WUzMX2Ewk3o1cL8YpkKttktgNHlG1LkxC9nd0cdL'

# 트위터 설정
TWITTER_BEARER_TOKEN = 'YOUR_TWITTER_BEARER_TOKEN'  # 트위터 개발자 센터 Bearer Token 입력
TWITTER_USER_NAME = 'ArahashiTabi'                 # 감지할 트위터 아이디 (@ 제외)
TARGET_HASHTAG = 'tabiart'                          # 감지할 해시태그 (# 제외)

INSTA_USER_ID = 'tabi_dayo3o'

# 상태 저장 변수 (중복 알림 방지용)
last_tweet_id = None

def send_discord_alarm(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message}, timeout=5)
    except Exception as e:
        print(f'디스코드 전송 실패: {e}', flush=True)

# -------------------------------------------------------------
# 3. 개별 점검 함수들
# -------------------------------------------------------------
def check_twitter():
    """#tabiart 태그 감지"""
    global last_tweet_id
    
    if TWITTER_BEARER_TOKEN == 'YOUR_TWITTER_BEARER_TOKEN':
        return  # 토큰 미입력 시 스킵

    headers = {
        'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        query = f'from:{TWITTER_USER_NAME} #{TARGET_HASHTAG}'
        url = f'https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=5&tweet.fields=created_at'
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get('data', [])

            if tweets:
                latest_tweet = tweets[0]
                tweet_id = latest_tweet['id']
                tweet_text = latest_tweet['text']

                if tweet_id != last_tweet_id:
                    tweet_url = f'https://twitter.com/{TWITTER_USER_NAME}/status/{tweet_id}'
                    send_discord_alarm(
                        f'🎨 **[트위터]** #{TARGET_HASHTAG} 새 게시글이 등록되었습니다!\n\n'
                        f'{tweet_text}\n\n'
                        f'🔗 {tweet_url}'
                    )
                    last_tweet_id = tweet_id
        else:
            print(f'트위터 API 응답 에러 (코드: {response.status_code})', flush=True)

    except requests.exceptions.Timeout:
        print('트위터 API 응답 시간 초과 (무한 대기 방지)', flush=True)
    except Exception as e:
        print(f'트위터 점검 에러: {e}', flush=True)

def check_instagram():
    """인스타그램 점검"""
    try:
        pass
    except Exception as e:
        print(f'인스타 점검 에러: {e}', flush=True)

# -------------------------------------------------------------
# 4. 30초마다 실행되는 메인 루프 (에러 방어 및 강제 출력)
# -------------------------------------------------------------
def main_loop():
    print("모니터링 시작! (30초 주기)", flush=True)
    send_discord_alarm("🤖 **[알림]** 모니터링 봇이 성공적으로 시작되었습니다!")
    
    while True:
        try:
            print("점검 진행 중...", flush=True)
            check_twitter()
            check_instagram()
        except Exception as e:
            print(f'메인 루프 예외 발생 (자동 복구됨): {e}', flush=True)
            
        time.sleep(30)

# -------------------------------------------------------------
# 5. 실행부
# -------------------------------------------------------------
if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    main_loop()
