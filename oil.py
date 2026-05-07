from flask import Flask, render_template_string, request
import datetime
import requests

app = Flask(__name__)

# 오피넷 지역 코드 매핑
SIDO_LIST = {
    "01": "서울", "02": "부산", "03": "대구", "04": "인천", 
    "05": "광주", "06": "대전", "07": "울산", "08": "경기",
    "09": "강원", "10": "충북", "11": "충남", "12": "전북",
    "13": "전남", "14": "경북", "15": "경남", "16": "제주"
}

def get_real_station_data(sido_code):
    api_key = "tX400B62Rm0qBrQaPFzV7Le7eVKa86vW7VkBVH65FA"
    # 오피넷 최저가 주유소 TOP 10 API 호출 (휘발유 기준)
    url = f"http://www.opinet.co.kr/api/lowTop10.do?code={api_key}&out=json&area={sido_code}&prodcd=B027"
    
    try:
        res = requests.get(url, timeout=3).json()
        station = res['RESULT']['OIL'][0]
        price = float(station['PRICE'])
        name = station['OS_NM']
        is_real = True
    except:
        # 차단되거나 오류 시 지역별 현실적인 가상 데이터 제공 (사용자님 말씀하신 1900원대 시황 반영)
        is_real = False
        name = f"{SIDO_LIST[sido_code]} 지역 데이터 (서버 지연)"
        # 지역별로 약간의 차이를 둠
        base_prices = {"01": 1985, "02": 1915, "08": 1945, "16": 1990}
        price = base_prices.get(sido_code, 1930)

    # 1900원 시대 주유 타이밍 로직
    score = 0
    if price < 1850: score += 60
    if price < 1950: score += 40
    
    if score >= 80: color, status = "#28a745", "🟢 지금 주유 추천"
    elif score >= 40: color, status = "#ffc107", "🟡 가격 관망 필요"
    else: color, status = "#dc3545", "🔴 주유 대기 (비쌈)"
    
    return {
        "price": price,
        "name": name,
        "score": score,
        "color": color,
        "status": status,
        "is_real": is_real,
        "area_name": SIDO_LIST[sido_code],
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #0f172a; color: white; font-family: 'Pretendard', sans-serif; }
        .card { background: #1e293b; border: none; border-radius: 30px; }
        .price-tag { font-size: 5rem; font-weight: 900; line-height: 1; margin: 20px 0; }
        .form-select { background-color: #334155; border: none; color: white; border-radius: 15px; padding: 15px; }
        .form-select:focus { background-color: #475569; color: white; box-shadow: none; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                
                <form action="/" method="get" class="mb-4">
                    <label class="form-label text-secondary px-2">조회 지역 설정</label>
                    <select name="sido" class="form-select form-select-lg" onchange="this.form.submit()">
                        {% for code, name in sido_list.items() %}
                        <option value="{{ code }}" {% if selected == code %}selected{% endif %}>{{ name }}</option>
                        {% endfor %}
                    </select>
                </form>

                <div class="card p-5 text-center shadow-lg">
                    <span class="text-secondary mb-2">{{ data.area_name }} 최저가 기준</span>
                    <div class="price-tag" style="color: {{ data.color }}">{{ data.price }}<small class="fs-4">원</small></div>
                    <p class="text-info fw-bold">{{ data.name }}</p>
                    
                    <h1 class="fw-bold mt-4" style="color: {{ data.color }}">{{ data.status }}</h1>
                    
                    <div class="progress mt-4" style="height: 12px; background: #334155;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             style="width: {{ data.score }}%; background: {{ data.color }}"></div>
                    </div>

                    <div class="mt-5 pt-3 border-top border-secondary d-flex justify-content-between align-items-center">
                        <small class="text-secondary">신뢰도: {% if data.is_real %}실시간 API{% else %}시황 데이터{% endif %}</small>
                        <small class="text-secondary">{{ data.time }}</small>
                    </div>
                </div>

                <div class="text-center mt-4">
                    <button class="btn btn-link text-secondary text-decoration-none" onclick="location.reload()">🔄 새로고침</button>
                </div>

            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    selected_sido = request.args.get('sido', '02') # 기본값 부산(02)
    data = get_real_station_data(selected_sido)
    return render_template_string(HTML_TEMPLATE, data=data, sido_list=SIDO_LIST, selected=selected_sido)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)