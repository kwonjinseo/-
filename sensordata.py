from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import threading
import time
import random

app = Flask(__name__) # Flask 애플리케이션 생성
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db' # 데이터베이스 설정
db = SQLAlchemy(app) # SQLAlchemy를 사용하여 데이터베이스와 연동

# 센서 데이터를 저장하기 위한 데이터베이스 모델 정의
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"SensorData(temperature={self.temperature}, humidity={self.humidity})"

# 데이터베이스 생성 함수
def create_database():
    with app.app_context():
        db.create_all()

# 센서 데이터를 수집하고 데이터베이스에 저장하는 함수
def store_sensor_data():
    with app.app_context():  # 백그라운드 스레드에서 애플리케이션 컨텍스트 생성
        while True:
            temperature = round(random.uniform(20, 30), 2)
            humidity = round(random.uniform(40, 60), 2)
            new_data = SensorData(temperature=temperature, humidity=humidity) # 새로운 센서 데이터 객체 생성
            db.session.add(new_data) # 세션에 새로운 데이터 추가
            db.session.commit() # 변경 사항을 데이터베이스에 반영
            time.sleep(1) # 1초 대기
            
# 홈 페이지를 렌더링하는 라우트        
@app.route('/')
def index():
    return render_template('index.html')

# 센서 데이터를 가져와 JSON 형식으로 반환하는 라우트
@app.route('/data', methods=['GET'])
def get_data():
    data = SensorData.query.all() # 데이터베이스에서 모든 센서 데이터를 가져옴
    data_json = [{"temperature": d.temperature, "humidity": d.humidity} for d in data] # JSON 형식으로 변환
    return render_template('data.html',data=data_json)  # data.html 템플릿에 데이터 전달

create_database()
sensor_thread = threading.Thread(target=store_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
    

# 위의 코드는 다음을 수행합니다:

# 1. Flask 애플리케이션을 생성합니다.
# 2. 데이터베이스를 설정하고 연동합니다. 여기서는 SQLite 데이터베이스를 사용합니다.
# 3. `SensorData` 클래스를 정의하여 센서 데이터를 저장할 데이터베이스 모델을 생성합니다.
# 4. `/` 경로에 접근하면 홈 페이지를 렌더링하는 함수를 정의합니다.
# 5. `/data` 경로에 GET 요청이 오면 데이터베이스에서 센서 데이터를 가져와 JSON 형식으로 변환하여 반환하는 함수를 정의합니다.
# 6. 데이터베이스를 생성하고, 백그라운드 스레드를 생성하여 주기적으로 센서 데이터를 생성하고 데이터베이스에 저장합니다.
# 7. 애플리케이션을 실행합니다.

# 또한, 주어진 코드에서는 Flask 애플리케이션과 데이터베이스 모델, 그리고 HTML 템플릿 파일들이 필요합니다. 이러한 파일들을 생성하여 적절한 경로에 배치해야 합니다. 특히 `index.html`과 `data.html` 템플릿 파일들은 각각 홈 페이지와 센서 데이터를 표시하는 페이지를 렌더링하기 위해 필요합니다.

