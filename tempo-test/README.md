# Tempo 테스트 애플리케이션

이 프로젝트는 Grafana Tempo로 트레이스를 전송하는 간단한 Flask 애플리케이션입니다.

## 사전 요구사항

- Docker
- Kubernetes (Kind 클러스터 권장)
- Python 3.9 이상
- Grafana Tempo가 설치된 Kubernetes 클러스터

## 프로젝트 구조

```
tempo-test/
├── app.py              # Flask 애플리케이션 코드
├── requirements.txt    # Python 패키지 의존성
├── Dockerfile         # Docker 이미지 빌드 파일
└── deployment.yaml    # Kubernetes 배포 매니페스트
```

## 설정 방법

1. 필요한 파일 생성

requirements.txt:
```python
flask==2.0.1
werkzeug==2.0.1
opentelemetry-api==1.19.0
opentelemetry-sdk==1.19.0
opentelemetry-exporter-otlp-proto-grpc==1.19.0
```

app.py:
```python
from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

# 트레이서 설정
provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# OTLP 익스포터 설정 (Tempo)
otlp_exporter = OTLPSpanExporter(endpoint="tempo.observability:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

app = Flask(__name__)

@app.route('/')
def hello():
    with tracer.start_as_current_span("hello-operation") as span:
        time.sleep(0.1)  # 인위적인 지연 추가
        span.set_attribute("custom.attribute", "test-value")
        return "Hello from Tempo Test App!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

deployment.yaml:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tempo-test-app
  namespace: observability
  labels:
    app: tempo-test-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tempo-test-app
  template:
    metadata:
      labels:
        app: tempo-test-app
    spec:
      containers:
      - name: tempo-test-app
        image: tempo-test-app:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: tempo-test-app
  namespace: observability
spec:
  selector:
    app: tempo-test-app
  ports:
  - port: 80
    targetPort: 5000
  type: ClusterIP
```

## 배포 단계

1. Kind 클러스터 컨텍스트로 전환:
```bash
kubectl config use-context kind-observability
```

2. Docker 이미지 빌드:
```bash
docker build -t tempo-test-app:latest .
```

3. 이미지를 Kind 클러스터에 로드:
```bash
kind load docker-image tempo-test-app:latest --name observability
```

4. Kubernetes에 배포:
```bash
kubectl apply -f deployment.yaml
```

5. 파드 상태 확인:
```bash
kubectl get pods -n observability
```

## 테스트 방법

1. 서비스 포트 포워딩:
```bash
kubectl port-forward svc/tempo-test-app -n observability 8080:80
```

2. 애플리케이션 테스트:
- 브라우저에서 http://localhost:8080 접속
- 또는 curl 명령어 사용:
```bash
curl http://localhost:8080
```

## 트레이스 확인

1. Grafana에 접속
2. Explore 메뉴로 이동
3. 데이터 소스로 Tempo 선택
4. Search 탭에서 다음 정보로 트레이스 검색:
   - 서비스 이름: `tempo-test-app`
   - 오퍼레이션 이름: `hello-operation`
   - 커스텀 속성: `custom.attribute: test-value`

## 문제 해결

파드가 시작되지 않는 경우:
1. 파드 로그 확인:
```bash
kubectl logs -n observability -l app=tempo-test-app
```

2. 파드 상태 자세히 확인:
```bash
kubectl describe pod -n observability -l app=tempo-test-app
``` 