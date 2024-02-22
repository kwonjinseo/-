from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import threading
import time
import json
import plotly.graph_objs as go
import plotly
import mariadb
import numpy as np
from example import LOFModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db = SQLAlchemy(app)

# MariaDB 연결 정보 입력
db_config = {
    'host': '192.168.1.134',
    'port': 3306,
    'user': 'raspi_usr',
    'password': 'disntm',
    'database': 'test'
}

# LOF 모델 초기화
lof_model = LOFModel(n_neighbors=20, contamination=0.1)


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"SensorData(temperature={self.temperature}, humidity={self.humidity})"

def create_database():
    with app.app_context():
        db.create_all()

# MariaDB로부터 센서 데이터를 가져와서 데이터베이스에 업데이트
def store_sensor_data():
    while True:
        try:
            # MariaDB 연결
            connection = mariadb.connect(**db_config)
            cursor = connection.cursor()

            # 센서 데이터 가져오기
            cursor.execute("SELECT temperature, humidity FROM test.test_data1")
            data = cursor.fetchall()

            # 데이터베이스 업데이트
            with app.app_context():
                for entry in data:
                    temperature, humidity = entry
                    new_data = SensorData(temperature=temperature, humidity=humidity)
                    db.session.add(new_data)
                    db.session.commit()

                # 데이터베이스 레코드 수가 100개를 초과하면 오래된 데이터 삭제
                num_records = SensorData.query.count()
                if num_records > 100:
                    excess_records = num_records - 100
                    oldest_records = SensorData.query.order_by(SensorData.id).limit(excess_records).all()
                    for record in oldest_records:
                        db.session.delete(record)
                    db.session.commit()
                
                # 새로운 데이터를 기존 데이터 배열에 추가하여 2D 배열 유지
                for entry in data:
                    temperature, humidity = entry
                    data.append([temperature, humidity])

                # LOF 모델에 데이터 추가 및 학습
                lof_model.fit(data)

            connection.close()
            time.sleep(3)  # 3초마다 데이터 업데이트

        except mariadb.Error as e:
            print(f"Error: {e}")
            time.sleep(3)

# vlaue = is_outlier
# if value == 1 :
    #그래프 파란색으로 표시
# elif value ==-1 :
#  그래프 빨간색 점으로 표시

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        data = SensorData.query.all()
        data_json = [{"temperature": d.temperature, "humidity": d.humidity} for d in data]
        return jsonify(data_json)
    elif request.method == 'POST':
        data = request.json
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        new_data = SensorData(temperature=temperature, humidity=humidity)
        db.session.add(new_data)
        db.session.commit()
        return jsonify({"message": "Data received successfully"})

@app.route('/chart')
def plot():
    data = SensorData.query.all()
    # 새로운 데이터가 들어올 때마다 LOF 모델에 추가하여 학습
    
    is_outlier = lof_model.predict(data)
    xdata = [d.temperature for d in data]
    ydata = [d.humidity for d in data]
    
      # LOF 모델에 데이터 추가 및 학습
      
    #   # # 이상치와 정상치를 구분하여 출력
    # for i, outlier in enumerate(is_outlier):
    #    if outlier == -1:
    #     print(f"데이터 {i+1}는 이상치입니다.")
    #    else:
    #     print(f"데이터 {i+1}는 정상입니다.")

# #예측결과 서버에 전송
# for i, outlier in enumerate(is_outlier):
#     # 이상치인 경우 -1, 정상치인 경우 1로 변환하여 전송
#     if outlier == -1:
#         outlier_label = -1
#         print(outlier_label)
#     else:
#         outlier_label = 1
#         print(outlier_label)
#     data = {
#         'index': i + 1,
#         'outlier': outlier_label
#     }

    # Plotly를 사용하여 그래프 생성
    trace_data = []

    for i, outlier in enumerate(is_outlier):
        if outlier == -1:
            trace = go.Scatter(x=[xdata[i]], y=[ydata[i]], mode='markers', marker=dict(color='red'), name='Outlier')
        else:
            trace = go.Scatter(x=[xdata[i]], y=[ydata[i]], mode='markers', marker=dict(color='blue'), name='Normal')
        trace_data.append(trace)

    layout = go.Layout(title='Data Plot', xaxis=dict(title='Temperature'), yaxis=dict(title='Humidity'))
    fig = go.Figure(data=trace_data, layout=layout)
    
    # 그래프를 JSON 형태로 변환하여 반환
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('chart.html', graphJSON=graphJSON)

create_database()
sensor_thread = threading.Thread(target=store_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

if __name__ == '__main__':
    app.run(debug=True)