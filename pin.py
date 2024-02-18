import Adafruit_DHT,requests

# 센서는 Adafruit_DHT.DHT11, Adafruit_DHT.DHT22 또는 Adafruit_DHT.AM2302로 설정되어야 합니다.
sensor = Adafruit_DHT.DHT22
# 라즈베리 파이에 DHT 센서가 GPIO23에 연결되어 있다고 가정합니다.
pin = 23

# 센서 값을 읽어옵니다. read_retry 메서드를 사용하면 센서 값을 가져올 때 최대 15번 재시도하며 (재시도 사이에 2초 대기), 센서 값을 얻을 때까지 재시도합니다.
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

# 때때로 센서 값을 읽어올 수 없는 경우가 있습니다.
# 이런 경우 결과값은 null이 될 수 있습니다.
# 이 경우에는 다시 시도해야 합니다!
if humidity is not None and temperature is not None:
    data = {
        'temperature': temperature,
        'humidity': humidity
    }
    # 데이터를 서버로 전송
    url = 'http://your_server_ip:5000/receive_data'  # 서버의 주소와 포트를 수정해야 함
    response = requests.post(url, json=data)
    print(response.text)  # 서버로부터 받은 응답 출력
else:
    print('Failed to get reading. Try again!')
