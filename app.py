from flask import Flask, request, jsonify
import random
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
from google import genai

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


# 2. 울산 날씨 크롤링은 이전에 추가했던 버전 유지 가능
# 여기서는 생략


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

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Google 뉴스 검색 결과에서 자주 보이는 제목 선택자들 시도
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


# 5. 파라미터로 Gemini 연동하기
@app.route("/gemini-param", methods=["POST"])
def gemini_param():
    data = request.get_json(silent=True) or {}
    tt = data.get("action", {}).get("params", {}).get("파라미터", "").strip()

    if not tt:
        return jsonify(kakao_text("파라미터 값이 없습니다."))

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify(kakao_text("GEMINI_API_KEY 환경변수가 설정되지 않았습니다."))

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=tt
        )
        result_text = response.text if response.text else "응답이 비어 있습니다."
    except Exception as e:
        result_text = f"Gemini 호출 중 오류: {str(e)}"

    return jsonify(kakao_text(result_text))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# --- 여기서부터 MBTI 환상궁합 AI 스킬 코드 ---
@app.route('/mbti', methods=['POST'])
def get_mbti_match():
    # 1. 카카오톡에서 보낸 메시지 데이터 받기
    kakao_request = request.get_json()
    user_message = kakao_request['userRequest']['utterance'].strip().upper() # 사용자가 입력한 MBTI (예: INFP)

    # 간단한 MBTI 유효성 검사 (자료구조 리스트 활용!)
    mbti_list = ["INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP", 
                 "ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP"]
    
    if user_message not in mbti_list:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": "올바른 MBTI 4자리를 입력해주세요! (예: INFP)"}}]
            }
        })

    # 2. 인공지능(Gemini)에게 질문 던지기
    try:
        # 기존에 설정된 gemini_param 함수나 client가 있다면 그걸 활용해도 되지만, 
        # 가장 표준적인 방법인 고유 프롬프트로 생성 요청을 보냅니다.
        prompt = f"너는 MBTI 전문가야. 사용자가 자신의 MBTI를 입력하면, 그 유형과 가장 환상의 궁합(가장 잘 맞는)인 MBTI 유형 하나를 콕 집어 추천하고, 왜 두 유형이 잘 맞는지 3줄 이내로 친절하고 유머러스하게 설명해줘. 내 MBTI는 {user_message}야."
        
        # 너의 기존 코드 방식에 맞춰 아래 라인을 사용하거나, 이미 상단에 정의된 client를 사용하면 돼.
        # 여기서는 가장 대중적인 최신 google-genai 라이브러리 구조 예시를 들었어.
        from google import genai
        client = genai.Client() # 상단에 설정되어 있다면 지워도 무방해
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_answer = response.text
    except Exception as e:
        ai_answer = f"앗, AI 서버에 문제가 생겼어요: {str(e)}"

    # 3. 카카오톡 답변 양식(JSON 트리 구조)에 맞춰서 리턴하기
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": ai_answer
                    }
                }
            ]
        }
    })
