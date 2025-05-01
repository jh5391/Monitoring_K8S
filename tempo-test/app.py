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