# Prometheus Remote Write 테스트 애플리케이션

이 프로젝트는 Prometheus 메트릭을 생성하고 Remote Write 프로토콜을 통해 Mimir로 전송하는 예제 애플리케이션입니다.

## 사전 요구사항

- Docker
- Kubernetes (Kind 클러스터 권장)
- Python 3.9 이상
- Mimir가 설치된 Kubernetes 클러스터

## 프로젝트 구조

```
remote_write/
├── remote_write_example.py    # 메트릭 생성 및 전송 코드
├── Dockerfile                # Docker 이미지 빌드 파일
└── remote-write-example-pod.yaml  # Kubernetes 배포 매니페스트
```

## 애플리케이션 설명

이 애플리케이션은 다음과 같은 기능을 수행합니다:

1. `example_requests_total` 카운터 메트릭을 생성
2. 5초마다 메트릭 값을 증가시키고 Mimir로 전송
3. Prometheus Remote Write 프로토콜을 사용하여 메트릭 전송
   - Snappy 압축 사용
   - Protobuf 형식으로 데이터 인코딩

## 파일 설명

### remote_write_example.py

```python
import time
from prometheus_client import Counter, generate_latest, CollectorRegistry
from prometheus_client.core import Timestamp
import requests
import snappy

# 메트릭 정의 및 Remote Write 로직
REQUESTS = Counter('example_requests_total', 'Total number of example requests', registry=registry)
# 5초마다 메트릭을 증가시키고 Mimir로 전송
```

### Dockerfile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY remote_write_example.py .
RUN pip install prometheus_client requests python-snappy
CMD ["python", "remote_write_example.py"]
```

### remote-write-example-pod.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: remote-write-example
  namespace: observability
spec:
  containers:
  - name: remote-write-example
    image: remote-write-example:latest
    imagePullPolicy: Never
    env:
    - name: REMOTE_WRITE_URL
      value: "http://mimir-nginx.observability.svc.cluster.local:80/api/v1/push"
```

## 배포 단계

1. Kind 클러스터 컨텍스트로 전환:
```bash
kubectl config use-context kind-observability
```

2. Docker 이미지 빌드:
```bash
docker build -t remote-write-example:latest .
```

3. 이미지를 Kind 클러스터에 로드:
```bash
kind load docker-image remote-write-example:latest --name observability
```

4. Kubernetes에 배포:
```bash
kubectl apply -f remote-write-example-pod.yaml
```

5. 파드 상태 확인:
```bash
kubectl get pods -n observability
```

## 메트릭 확인

1. Grafana에 접속
2. Explore 메뉴로 이동
3. 데이터 소스로 Mimir 선택
4. 다음 PromQL 쿼리로 메트릭 확인:
```
example_requests_total
```

## 문제 해결

파드가 시작되지 않는 경우:
1. 파드 로그 확인:
```bash
kubectl logs -n observability remote-write-example
```

2. 파드 상태 자세히 확인:
```bash
kubectl describe pod -n observability remote-write-example
```

3. Mimir 연결 문제 해결:
   - Mimir 서비스가 올바르게 실행 중인지 확인
   - Remote Write URL이 올바른지 확인
   - 네트워크 정책이 Remote Write 트래픽을 허용하는지 확인

## 주의사항

1. Remote Write URL은 클러스터 내부 서비스 주소를 사용합니다:
   - `http://mimir-nginx.observability.svc.cluster.local:80/api/v1/push`
   - 환경에 따라 URL을 적절히 수정해야 할 수 있습니다.

2. 메트릭 전송 간격:
   - 기본적으로 5초마다 메트릭을 전송합니다.
   - 필요에 따라 `remote_write_example.py`의 `time.sleep(5)` 값을 조정할 수 있습니다. 