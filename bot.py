import asyncio
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
DISCORD_WEBHOOK_URL = '여기에_디스코드_웹훅_주소_입력'

CHZZK_CHANNEL_ID = '치지직_채널_ID'
TWITTER_USER_ID = '트위터_유저_ID'
INSTA_USER_ID = '인스타_유저_ID'

# 상태 저장용 변수
last_chzzk_status = False


def send_discord_alarm(message):
  try:
    requests.post(DISCORD_WEBHOOK_URL, json={'content': message})
  except Exception as e:
    print(f'디스코드 전송 실패: {e}')


# -------------------------------------------------------------
# 3. 개별 점검 함수들 (동시 실행될 작업들)
# -------------------------------------------------------------
async def check_chzzk():
  """치지직 점검"""
  global last_chzzk_status
  try:
    url = f'https://api.chzzk.naver.com/polling/v2/channels/{CHZZK_CHANNEL_ID}/live-status'
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
    status = res.get('content', {}).get('status')

    if status == 'OPEN' and not last_chzzk_status:
      title = res.get('content', {}).get('liveTitle', '제목 없음')
      send_discord_alarm(
          f'🔴 **[치지직]** 뱅온! 방송이 시작되었습니다!\n제목: {title}'
      )
      last_chzzk_status = True
    elif status == 'CLOSE':
      last_chzzk_status = False
  except Exception as e:
    print(f'치지직 점검 에러: {e}')


async def check_twitter():
  """트위터 점검"""
  try:
    # 트위터 점검 로직 작성 위치
    pass
  except Exception as e:
    print(f'트위터 점검 에러: {e}')


async def check_instagram():
  """인스타그램 점검"""
  try:
    # 인스타그램 점검 로직 작성 위치
    pass
  except Exception as e:
    print(f'인스타 점검 에러: {e}')


# -------------------------------------------------------------
# 4. 30초마다 3개를 동시에 실행하는 메인 루프
# -------------------------------------------------------------
async def main_loop():
  print('모니터링을 시작합니다...')
  while True:
    # asyncio.gather로 3개 함수를 동시에 병렬 실행
    await asyncio.gather(
        check_chzzk(),
        check_twitter(),
        check_instagram(),
    )
    # 3개 작업이 모두 끝나면 30초 대기
    await asyncio.sleep(30)


# -------------------------------------------------------------
# 5. 실행부
# -------------------------------------------------------------
if __name__ == '__main__':
  t = threading.Thread(target=run_flask)
  t.daemon = True
  t.start()

  asyncio.run(main_loop())
