from flask import Flask, request, jsonify
import random
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

app = Flask(__name__)

def kakao_text(text):
    return {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": text[:1000]
                }
            }]
        }
    }

@app.route("/", methods=["GET"])
def home():
    return "Server is running."

# 기존 테스트용
@app.route("/text", methods=["GET", "POST"])
def text_skill():
    return jsonify(kakao_text(str(random.randint(1, 10))))

@app.route("/image", methods=["GET", "POST"])
def image_skill():
    response = {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleImage": {
                    "imageUrl": "https://t1.daumcdn.net/friends/prod/category/M001_friends_ryan2.jpg",
                    "altText": "hello I'm Ryan"
                }
            }]
        }
    }
    return jsonify(response)

# 1. 데이터 그대로 주고받기
@app.route("/echo", methods=["POST"])
def echo_skill():
    data = request.get_json(silent=True) or {}
    user_input = data.get("userRequest", {}).get("utterance", "입력값이 없습니다.")
    return jsonify(kakao_text(user_input))

# 3. 시간/발화/파라미터 확인
@app.route("/params-check", methods=["POST"])
def params_check():
    data = request.get_json(silent=True) or {}
    user_request = data.get("userRequest", {})
    action = data.get("action", {})
    params = action.get("params", {})

    a = user_request.get("timezone", "timezone 없음")
    b = user_request.get("utterance", "utterance 없음")
    c = params.get("파라미터", "파라미터 없음")
    d = params.get("파라미터2", "파라미터2 없음")

    text = f"{a} / {b} / {c} / {d}"
    return jsonify(kakao_text(text))

# 4. 파라미터 활용 구글 기사 데이터 가져오기
@app.route("/google-news", methods=["POST"])
def google_news():
    data = request.get_json(silent=True) or {}
    y = data.get("action", {}).get("params", {}).get("파라미터", "").strip()

    if not y:
        return jsonify(kakao_text("파라미터 값이 없습니다."))

    query = urllib.parse.quote(y)
    url = f"https://www.google.com/search?q={query}&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select(".n0jPhd") or soup.select(".mCBkyc") or soup.select(".DKV0Md")

        titles = []
        for item in items[:5]:
            title = item.get_text(strip=True)
            if title:
                titles.append(title)

        if titles:
            result = y + " 검색 결과:\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
        else:
            result = f"{y} 검색 결과를 찾지 못했습니다."
    except Exception as e:
        result = f"구글 뉴스 조회 중 오류: {str(e)}"

    return jsonify(kakao_text(result))


# ========================================================
# 6. MBTI 환상궁합 AI 스킬 (오픈AI 연결 완벽 수정 버전)
# ========================================================
@app.route('/mbti', methods=['POST'])
def get_mbti_match():
    kakao_request = request.get_json()
    user_message = kakao_request['userRequest']['utterance'].strip().upper()

    mbti_list = ["INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP", 
                 "ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP"]
    
    if user_message not in mbti_list:
        return jsonify(kakao_text("올바른 MBTI 4자리를 입력해주세요! (예: INFP)"))

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify(kakao_text("Render 환경변수에 OPENAI_API_KEY가 설정되지 않았습니다."))

    try:
        # 헤더 형식을 application/json으로 올바르게 전송합니다.
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages":
