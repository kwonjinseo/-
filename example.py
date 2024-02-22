import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
import random
import requests
import json

class LOFModel:
    def __init__(self, n_neighbors=20, contamination=0.1):
        self.clf = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)

    def fit(self, X):
        self.clf.fit(X)

    def predict(self, X):
        return self.clf.fit_predict(X)

    def score_samples(self, X):
        return self.clf.negative_outlier_factor_

# CSV 파일에서 기존 데이터 읽기
file_path = './temperature_humidity_data.csv'
data_csv = pd.read_csv(file_path)


# 기존 데이터 준비
X = data_csv.values

# LOF 모델 초기화 및 학습
lof_model = LOFModel(n_neighbors=20, contamination=0.1)
lof_model.fit(X)
print(X)



mean_temperature = np.mean(X[:, 0])
std_temperature = np.std(X[:, 0])
mean_humidity = np.mean(X[:, 1])
std_humidity = np.std(X[:, 1])

# # 새로운 센서 데이터 받아오기
# new_sensor_data = []
# for _ in range(100):
#     try:
#         data = requests.get('https://3d99-112-184-243-68.ngrok-free.app')
#         if data.status_code == 200:
#             data = data.json()
#             temperature = data.get('temperature')
#             humidity = data.get('humidity')

#             # 정규화
#             temperature_normalized = (temperature - mean_temperature) / std_temperature
#             humidity_normalized = (humidity - mean_humidity) / std_humidity
#             # 새로운 센서 데이터를 딕셔너리로 저장
#             sensor_data = {
#                 'temperature_normalized': temperature_normalized,
#                 'humidity_normalized': humidity_normalized
#             }
#             new_sensor_data.append([temperature_normalized, humidity_normalized])
#         else:
#             print(f"서버 응답 실패: {data.status_code}")
#     except requests.exceptions.RequestException as e:
#         print(f"센서 데이터를 가져오는 중 오류 발생: {e}")
#     except json.JSONDecodeError as e:
#         print(f"JSON 디코딩 에러 발생: {e}")
   

# # 이상치 여부 예측
# is_outlier = lof_model.predict(X)

# # 이상치와 정상치를 구분하여 출력
# for i, outlier in enumerate(is_outlier):
#     if outlier == -1:
#         print(f"데이터 {i+1}는 이상치입니다.")
#     else:
#         print(f"데이터 {i+1}는 정상입니다.")

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
#     response = requests.post('https://3d99-112-184-243-68.ngrok-free.app', json=data)