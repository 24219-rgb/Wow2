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

@app.route("/echo", methods=["POST"])
def echo_skill():
    data = request.get_json(silent=True) or {}
    user_input = data.get("userRequest", {}).get("utterance", "입력값이 없습니다.")
    return jsonify(kakao_text(user_input))

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
# 6. MBTI 환상궁합 AI 스킬
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
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "너는 유머러스한 MBTI 전문가야."},
                {"role": "user", "content": f"내 MBTI는 {user_message}야. 나랑 가장 환상의 궁합인 MBTI 유형 딱 하나를 콕 집어 추천하고, 왜 잘 맞는지 핵심만 2줄 이내로 웃기게 설명해줘."}
            ],
            "max_tokens": 150
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=4)
        
        if response.status_code == 200:
            result_json = response.json()
            ai_answer = result_json["choices"][0]["message"]["content"].strip()
        else:
            ai_answer = f"GPT 서버 응답 오류 (코드 {response.status_code})"

    except Exception as e:
        ai_answer = f"앗, AI 서버에 문제가 생겼어요: {str(e)}"

    return jsonify(kakao_text(ai_answer))


# ========================================================
# 7. MBTI 연애 스타일 AI 스킬
# ========================================================
@app.route('/mbti-love', methods=['POST'])
def get_mbti_love():
    kakao_request = request.get_json()
    user_message = kakao_request['userRequest']['utterance'].strip().upper()

    mbti = user_message.replace("연애", "").strip()

    mbti_list = ["INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP", 
                 "ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP"]
    
    if mbti not in mbti_list:
        return jsonify(kakao_text("MBTI 뒤에 '연애'를 붙여서 입력해주세요! (예: INFP 연애)"))

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify(kakao_text("Render 환경변수에 OPENAI_API_KEY가 설정되지 않았습니다."))

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "너는 팩폭을 잘하는 솔직하고 유머러스한 연애 상담사야."},
                {"role": "user", "content": f"{mbti} 유형의 연애 스타일과 특징을 장점 하나, 단점 하나로 나누어서 3줄 이내로 핵심만 웃기게 요약해줘."}
            ],
            "max_tokens": 150
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=4)
        
        if response.status_code == 200:
            result_json = response.json()
            ai_answer = result_json["choices"][0]["message"]["content"].strip()
        else:
            ai_answer = f"GPT 서버 응답 오류 (코드 {response.status_code})"

    except Exception as e:
        ai_answer = f"앗, AI 서버에 문제가 생겼어요: {str(e)}"

    return jsonify(kakao_text(ai_answer))


# ========================================================
# 8. MBTI 플러팅 스타일 AI 스킬
# ========================================================
@app.route('/mbti-flirt', methods=['POST'])
def get_mbti_flirt():
    kakao_request = request.get_json()
    user_message = kakao_request['userRequest']['utterance'].strip().upper()

    mbti = user_message.replace("플러팅", "").strip()

    mbti_list = ["INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP", 
                 "ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP"]
    
    if mbti not in mbti_list:
        return jsonify(kakao_text("MBTI 뒤에 '플러팅'을 붙여서 입력해주세요! (예: INFP 플러팅)"))

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify(kakao_text("Render 환경변수에 OPENAI_API_KEY가 설정되지 않았습니다."))

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "너는 사람들의 심리를 꿰뚫어 보는 연애 관찰자야."},
                {"role": "user", "content": f"{mbti} 유형의 사람이 누군가를 좋아할 때 부리는 '꼬시기 행동(플러팅 스타일)'의 핵심 특징 2가지를 아주 구체적이고 위트 있게 3줄 이내로 대답해줘."}
            ],
            "max_tokens": 150
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=4)
        
        if response.status_code == 200:
            result_json = response.json()
            ai_answer = result_json["choices"][0]["message"]["content"].strip()
        else:
            ai_answer = f"GPT 서버 응답 오류 (코드 {response.status_code})"

    except Exception as e:
        ai_answer = f"앗, AI 서버에 문제가 생겼어요: {str(e)}"

    return jsonify(kakao_text(ai_answer))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
