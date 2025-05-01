# Kubernetes 모니터링 스택 설치 및 실행 가이드

## 1. Helm 레포지토리 추가
```bash
# Grafana 차트 레포지토리 추가
helm repo add grafana https://grafana.github.io/helm-charts

# Prometheus 차트 레포지토리 추가
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# 레포지토리 업데이트
helm repo update
```

## 2. 모니터링 스택 설치 (namespace: observability)
```bash
# Prometheus 스택 설치
helm install prometheus prometheus-community/kube-prometheus-stack -n observability -f values.yaml

# Loki 설치
helm install loki grafana/loki -n observability -f values.yaml

# Promtail 설치
helm install promtail grafana/promtail -n observability -f values.yaml

# Grafana 설치
helm install grafana grafana/grafana -n observability -f values.yaml

# Mimir 설치 (선택사항)
helm install mimir grafana/mimir-distributed -n observability -f values.yaml

# Tempo 설치
helm install tempo grafana/tempo -n observability -f values.yaml
```

## 3. 포트 포워딩 설정
```bash
# Grafana 대시보드 접속 (http://localhost:3000)
kubectl port-forward -n observability svc/grafana 3000:80

# Prometheus 대시보드 접속 (http://localhost:9090)
kubectl port-forward prometheus-kube-prometheus-prometheus-0 9090:9090 -n observability

# Loki 접속 (http://localhost:3100)
kubectl port-forward -n observability svc/loki 3100:3100

kubectl port-forward svc/tempo -n observability 3100:3100
```

## 4. 테스트 로그 생성 (선택사항)
```bash
# 테스트용 로그 생성 파드 실행
kubectl run log-generator -n observability --image=busybox --restart=Never -- sh -c "while true; do echo 'Test log from Promtail - $(date)'; sleep 1; done"
```

## 참고사항
- 각 컴포넌트 설치 시 사용되는 `values.yaml` 파일은 필요에 따라 커스터마이징하여 사용하세요.
- 모든 컴포넌트는 `observability` 네임스페이스에 설치됩니다.
- 포트 포워딩 후 로컬 브라우저에서 각 서비스에 접근할 수 있습니다.