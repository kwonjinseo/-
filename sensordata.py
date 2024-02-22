# sensordata.py

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import threading
import time
import json
import plotly.graph_objs as go
import plotly
import mariadb
import numpy as np
from sklearn.neighbors import LocalOutlierFactor

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

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"SensorData(temperature={self.temperature}, humidity={self.humidity})"

def create_database():
    with app.app_context():
        db.create_all()

# MariaDB로부터 센서 데이터를 가져와서 데이터베이스에 업데이트 및 LOF 모델 학습
def store_sensor_data_and_train_lof_model():
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

                # 데이터베이스 레코드 수가 충분하면 LOF 모델 학습
                num_records = SensorData.query.count()
                if num_records >= 100:
                    # 센서 데이터 가져오기
                    sensor_data = SensorData.query.all()
                    X = np.array([[entry.temperature, entry.humidity] for entry in sensor_data])

                    # LOF 모델 학습
                    lof_model = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
                    lof_model.fit(X)

                    # 저장된 모델을 pickle 또는 다른 방법으로 사용할 수도 있습니다.

            connection.close()
            time.sleep(3)  # 3초마다 데이터 업데이트

        except mariadb.Error as e:
            print(f"Error: {e}")
            time.sleep(3)

# 나머지 Flask 애플리케이션 코드와 함께 실행합니다.
if __name__ == '__main__':
    create_database()
    sensor_thread = threading.Thread(target=store_sensor_data_and_train_lof_model)
    sensor_thread.daemon = True
    sensor_thread.start()
    app.run(debug=True)
