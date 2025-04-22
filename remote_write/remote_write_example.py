import time
from prometheus_client import Counter, generate_latest, CollectorRegistry
from prometheus_client.core import Timestamp
import requests
import snappy  # Prometheus remote_write는 snappy 압축 사용

# Mimir remote_write 엔드포인트
REMOTE_WRITE_URL = "http://localhost:9009/api/v1/push"  # Kind에서는 서비스 URL로 변경 필요

# 메트릭 정의
registry = CollectorRegistry()
REQUESTS = Counter('example_requests_total', 'Total number of example requests', registry=registry)

def send_to_remote_write():
    # 메트릭 증가
    REQUESTS.inc()

    # Prometheus 메트릭을 Protobuf 형식으로 변환
    data = generate_latest(registry)

    # Snappy로 압축
    compressed_data = snappy.compress(data)

    # remote_write 요청 보내기
    headers = {
        "Content-Encoding": "snappy",
        "Content-Type": "application/x-protobuf",
        "X-Prometheus-Remote-Write-Version": "0.1.0"
    }
    response = requests.post(REMOTE_WRITE_URL, data=compressed_data, headers=headers)

    # 응답 확인
    if response.status_code == 200:
        print("Successfully sent metrics to remote_write")
    else:
        print(f"Failed to send metrics: {response.status_code} - {response.text}")

def main():
    print(f"Sending metrics to {REMOTE_WRITE_URL}")
    while True:
        send_to_remote_write()
        time.sleep(5)  # 5초마다 전송

if __name__ == "__main__":
    main()
