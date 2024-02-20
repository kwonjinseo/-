from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import deque
import threading
import time
import random
import json
import plotly.graph_objs as go
import plotly

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"SensorData(temperature={self.temperature}, humidity={self.humidity})"

def create_database():
    with app.app_context():
        db.create_all()

def store_sensor_data():
    with app.app_context():
        while True:
            temperature = round(random.uniform(20, 30), 2)
            humidity = round(random.uniform(40, 60), 2)
            new_data = SensorData(temperature=temperature, humidity=humidity)
            db.session.add(new_data)
            db.session.commit()
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def get_data():
    data = SensorData.query.all()
    data_json = [{"mode": "markers+lines","name": "Data","temperature": d.temperature, "humidity": d.humidity} for d in data]

    # JSON 데이터를 파일에 쓰기
    with open('sensor_data.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

    return jsonify(data_json)

# View Chart를 위한 라우트 추가
@app.route('/chart')
def plot():
    with open('sensor_data.json', 'r') as json_file:
        data_json = json.load(json_file)
    
    xdata_json = [d["temperature"] for d in data_json]
    ydata_json = [d["humidity"] for d in data_json]

    # Plotly를 사용하여 그래프 생성
    trace = go.Scatter(x=xdata_json, y=ydata_json, mode='markers+lines', name='Data')
    layout = go.Layout(title='Data Plot', xaxis=dict(title='Temperature'), yaxis=dict(title='Humidity'))
    fig = go.Figure(data=[trace], layout=layout)

    # 그래프를 JSON 형태로 변환하여 반환
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

create_database()
sensor_thread = threading.Thread(target=store_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
