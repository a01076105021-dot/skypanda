import os
from flask import Flask
import requests

app = Flask(__name__)

# -------------------------------------------------------------
# 1. 설정 및 변수
# -------------------------------------------------------------
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1538586452664000543/YlO8otTVQh0cw3JJzMp7gAEPtYS7WUzMX2Ewk3o1cL8YpkKttktgNHlG1LkxC9nd0cdL'

TWITTER_BEARER_TOKEN = 'YOUR_TWITTER_BEARER_TOKEN'  # 본인 트위터 Bearer Token
TWITTER_USER_NAME = 'ArahashiTabi'
TARGET_HASHTAG = 'tabiart'

last_tweet_id = None

# -------------------------------------------------------------
# 2. 알림 및 점검 함수
# -------------------------------------------------------------
def send_discord_alarm(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message}, timeout=5)
    except Exception as e:
        print(f'디스코드 전송 실패: {e}', flush=True)

def check_twitter():
    """트위터 태그 감지"""
    global last_tweet_id
    
    if TWITTER_BEARER_TOKEN == 'YOUR_TWITTER_BEARER_TOKEN':
        return

    headers = {
        'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        query = f'from:{TWITTER_USER_NAME} #{TARGET_HASHTAG}'
        url = f'https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=5'
        
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
    except Exception as e:
        print(f'트위터 점검 에러: {e}', flush=True)

def check_instagram():
    """인스타그램 점검"""
    try:
        pass
    except Exception as e:
        print(f'인스타 점검 에러: {e}', flush=True)

# -------------------------------------------------------------
# 3. UptimeRobot 신호 수신 시 자동 실행되는 웹 루트
# -------------------------------------------------------------
@app.route('/')
def home():
    print(">>> [UptimeRobot 신호 수신] 점검을 시작합니다.", flush=True)
    
    # 신호를 받을 때마다 모니터링 실행
    check_twitter()
    check_instagram()
    
    return 'Bot is alive and checked!', 200

# -------------------------------------------------------------
# 4. 실행부
# -------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
