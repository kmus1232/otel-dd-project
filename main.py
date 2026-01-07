# main.py
from fastapi import FastAPI
import uvicorn
import random
import time

from opentelemetry import trace

otel_tracer = trace.get_tracer(__name__)

app = FastAPI()

# ---------------------------------------------------------
# [NEW] OpenTelemetry API로 계측한 새로운 비즈니스 로직
# ---------------------------------------------------------

def process_payment_logic(order_id: str, amount: int):
    # 'start_as_current_span'을 사용해 OTel Span 생성
    with otel_tracer.start_as_current_span("business.payment_processing") as span:
        # 1. OTel 스타일 Attribute 추가 (Datadog Tag로 변환됨)
        span.set_attribute("order.id", order_id)
        span.set_attribute("payment.amount", amount)
        span.set_attribute("payment.method", "credit_card")
        
        time.sleep(0.2) # 작업 시뮬레이션

        # 2. 하위 Span 생성 (Nested Span)
        with otel_tracer.start_as_current_span("business.validate_card") as child_span:
            time.sleep(0.1)
            child_span.set_attribute("validation.status", "ok")

        return f"Order {order_id} processed"

# [NEW] OTel 로직을 호출하는 새로운 엔드포인트
@app.get("/otel-payment/{order_id}")
def otel_endpoint(order_id: str):
    # 여기서 호출하면 FastAPI의 자동 계측 Span 아래에 OTel Span이 자식으로 붙습니다.
    result = process_payment_logic(order_id, random.randint(1000, 50000))
    return {"result": result}


# ---------------------------------------------------------
# [EXISTING] 기존 코드 (Datadog 자동 계측 영역)
# ---------------------------------------------------------

@app.get("/")
def read_root():
    # 처리 시간 시뮬레이션
    time.sleep(random.uniform(0.1, 0.5))
    return {"Hello": "Datadog APM"}

@app.get("/error")
def trigger_error():
    # 에러 트래킹 테스트용
    if random.choice([True, False]):
        raise ValueError("Random error triggered for Datadog!")
    return {"status": "safe"}




if __name__ == "__main__":
    # 호스트 0.0.0.0 설정 중요
    uvicorn.run(app, host="0.0.0.0", port=8000)