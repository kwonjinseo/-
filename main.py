import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from flask import Flask, request

app = Flask(__name__)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json  # 라즈베리 파이에서 보낸 데이터를 JSON 형식으로 받음
    print("Received data:", data)
    
    # 데이터를 이상치 탐지 모델에 입력할 형식으로 변환
    X = np.array([[data['temperature'], data['humidity']]])  # 예시로 온도와 습도 데이터를 사용
    
    # 이상치 탐지 모델 적용
    clf = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
    y_pred = clf.fit_predict(X)
    X_scores = clf.negative_outlier_factor_
    
    # 시각화
    plt.title("Local Outlier Factor (LOF)")
    plt.scatter(X[:, 0], X[:, 1], color='b', s=3., label='Data points')
    
    # 이상치 점수를 이용한 이상치 시각화
    radius = (X_scores.max() - X_scores) / (X_scores.max() - X_scores.min())
    plt.scatter(X[:, 0], X[:, 1], s=1000 * radius, edgecolors='r',
                facecolors='none', label='Outlier scores')
    n = np.copy(X_scores)
    n[n > -1.3] = np.nan
    n = np.round(n, 2)
    for i, txt in enumerate(n):
        if np.isnan(txt):
            continue
        plt.annotate(txt, (X[i, 0], X[i, 1]))
    legend = plt.legend(loc='upper left')
    plt.show()
    
    return 'Data received successfully'

if __name__ == '__main__':
    app.run(debug=True)  # 디버그 모드로 서버 실행
