import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler #데이터 스케일 조정
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# 데이터 생성 함수
def generate_random_gas_concentration_data(start_date, end_date):
    # 데이터 생성을 위한 날짜 범위 설정
    num_hours = pd.date_range(start=start_date, end=end_date, freq='H').shape[0]
    
    # 임의의 수소와 질소 농도 데이터 생성
    hydrogen_concentration = np.random.uniform(0.1, 0.5, num_hours)
    #nitrogen_concentration = np.random.uniform(0.01, 0.1, num_hours)
    
    data = {
        'timestamp': pd.date_range(start=start_date, end=end_date, freq='H'),
        'hydrogen_concentration': hydrogen_concentration,  # 임의의 수소 농도 생성 (0.1에서 0.5 사이)
        #'nitrogen_concentration': nitrogen_concentration  # 임의의 질소 농도 생성 (0.01에서 0.1 사이)
    }

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)

    # CSV 파일로 저장
    csv_filename = 'random_gas_concentration_data.csv'
    df.to_csv(csv_filename, index=False)
    print(f"Data generated and saved to {csv_filename}")

# 시계열 데이터 생성 예시
start_date = '2024-01-01'
end_date = '2024-01-31'
generate_random_gas_concentration_data(start_date, end_date)

# 데이터 전처리 함수
def preprocess_data(data):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    return scaled_data, scaler

# LSTM 입력 데이터 생성 함수
def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(len(data)-seq_length):
        X.append(data[i:i+seq_length, :])
        y.append(data[i+seq_length, 0])  # 예측할 대상 (수소 농도)
    return np.array(X), np.array(y)

# 데이터 로드 및 전처리
data = pd.read_csv('random_gas_concentration_data.csv')
data.set_index('timestamp', inplace=True) #timestamp를 인덱스로 설정한다
scaled_data, scaler = preprocess_data(data)

print(scaled_data)
print(scaler)

# LSTM 입력 데이터 생성
seq_length = 24  # 24시간 단위로 데이터를 분할
X, y = create_sequences(scaled_data, seq_length)
print(X)
print(y)

# 데이터 분할 (학습 데이터와 테스트 데이터)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_test)

# LSTM 모델 생성
model = Sequential([
    LSTM(units=50, input_shape=(X.shape[1], X.shape[2])),
    Dense(units=1)
])
model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 학습
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=2)

# 모델 예측
predicted_hydrogen_concentration = model.predict(X_test)
# 스케일러 역변환
predicted_hydrogen_concentration = scaler.inverse_transform(predicted_hydrogen_concentration)
actual_hydrogen_concentration = scaler.inverse_transform(y_test.reshape(-1, 1))

# 예측된 값과 실제 값 출력
print(predicted_hydrogen_concentration)
print(actual_hydrogen_concentration)

# 예측 결과 그래프로 출력
plt.figure(figsize=(12, 6))
plt.plot(actual_hydrogen_concentration, label='Actual Hydrogen Concentration')
plt.plot(predicted_hydrogen_concentration, label='Predicted Hydrogen Concentration')
plt.title('Hydrogen Concentration Prediction')
plt.xlabel('Time')
plt.ylabel('Hydrogen Concentration')
plt.legend()
plt.show()