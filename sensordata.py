from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
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

#json파일을 데이터베이스에 업데이트
def store_sensor_data():
    with app.app_context():
        # Read data from the JSON file
        with open('sensor_data.json', 'r') as json_file:
            data = json.load(json_file)

        # Add data to the database
        for entry in data:
            temperature = entry.get('temperature')
            humidity = entry.get('humidity')
            new_data = SensorData(temperature=temperature, humidity=humidity)
            db.session.add(new_data)
            db.session.commit()

        # Limit the number of records to 100
        num_records = SensorData.query.count()
        if num_records > 100:
            excess_records = num_records - 100
            oldest_records = SensorData.query.order_by(SensorData.id).limit(excess_records).all()
            for record in oldest_records:
                db.session.delete(record)
            db.session.commit()
            
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

# 차트 보기용 라우트 추가
@app.route('/chart')
def plot():
    data = SensorData.query.all()
    xdata = [d.temperature for d in data]
    ydata = [d.humidity for d in data]

    # Plotly를 사용하여 그래프 생성
    trace = go.Scatter(x=xdata, y=ydata, mode='markers', name='Data')
    layout = go.Layout(title='Data Plot', xaxis=dict(title='Temperature'), yaxis=dict(title='Humidity'))
    fig = go.Figure(data=[trace], layout=layout)

    # 그래프를 JSON 형태로 변환하여 반환
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('chart.html', graphJSON=graphJSON)

#create_database()
sensor_thread = threading.Thread(target=store_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
