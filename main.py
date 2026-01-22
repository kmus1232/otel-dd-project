# main.py
from fastapi import FastAPI
import uvicorn
import random
import time

from opentelemetry import trace
from ddtrace import tracer as dd_tracer  # Datadog 네이티브 tracer

otel_tracer = trace.get_tracer(__name__)

app = FastAPI()

# ---------------------------------------------------------
# OpenTelemetry API로 계측한 비즈니스 로직
# ---------------------------------------------------------

# 1. 데코레이터 방식 - 함수에 span 자동 생성
@otel_tracer.start_as_current_span("otel.decorator_test")
def otel_decorator_test():
    span = trace.get_current_span()  # 현재 span 가져오기
    span.set_attribute("test", "true")
    time.sleep(0.1)

# 데코레이터 함수 호출 엔드포인트
@app.get("/otel-decorator")
def otel_decorator_endpoint():
    otel_decorator_test()  # 호출 시 자동으로 span 생성
    return {"result": "Decorator test completed"}

# 2. with 문 방식 - 중첩 span 예시
def process_payment_logic(order_id: str, amount: int):
    with otel_tracer.start_as_current_span("business.payment_processing") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("payment.amount", amount)
        span.set_attribute("payment.method", "credit_card")
        time.sleep(0.2)

        # 하위 span 생성 (부모-자식 관계)
        with otel_tracer.start_as_current_span("business.validate_card") as child_span:
            time.sleep(0.1)
            child_span.set_attribute("validation.status", "ok")

        return f"Order {order_id} processed"

# with 문 방식 호출 엔드포인트
@app.get("/otel-payment/{order_id}")
def otel_endpoint(order_id: str):
    result = process_payment_logic(order_id, random.randint(1000, 50000))
    return {"result": result}


# ---------------------------------------------------------
# Datadog 자동 계측 영역
# ---------------------------------------------------------

@app.get("/")
def read_root():
    time.sleep(random.uniform(0.1, 0.5))
    return {"Hello": "Datadog APM"}

@app.get("/error")
def trigger_error():
    if random.choice([True, False]):
        raise ValueError("Random error triggered for Datadog!")
    return {"status": "safe"}


# ---------------------------------------------------------
# Datadog 네이티브 API (ddtrace) 계측 예시
# ---------------------------------------------------------

# 1. 데코레이터 방식 - 비즈니스 로직 커스텀 계측
@dd_tracer.wrap(name="business.calculate_total")
def calculate_total(items: list):
    span = dd_tracer.current_span()
    if span:
        span.set_tag("items.count", len(items))
    time.sleep(0.03)
    return sum(item.get("price", 0) for item in items)

# 2. 데코레이터 함수 호출 예시
# 호출 시 Span 구조:
#   └─ fastapi.request (자동 계측)
#       └─ business.calculate_total (데코레이터로 생성된 자식 span)
@app.get("/ddtrace-checkout")
def ddtrace_checkout_endpoint():
    items = [{"name": "item1", "price": 1000}, {"name": "item2", "price": 2000}]
    total = calculate_total(items)
    return {"total": total}

# 3. service 파라미터로 커스텀 서비스명 지정
@dd_tracer.wrap(service="my-sandwich-making-svc", resource="make_sandwich")
def make_sandwich(sandwich_type: str):
    """이 함수는 "my-sandwich-making-svc"라는 별도 서비스로 표시됩니다"""
    span = dd_tracer.current_span()
    if span:
        span.set_tag("sandwich.type", sandwich_type)
        span.set_tag("sandwich.status", "preparing")
    time.sleep(0.15)
    return f"{sandwich_type} sandwich ready!"

@app.get("/ddtrace-sandwich/{sandwich_type}")
def ddtrace_sandwich_endpoint(sandwich_type: str):
    result = make_sandwich(sandwich_type)
    return {"result": result, "service": "my-sandwich-making-svc"}

# 4. with 문 방식 - 태그/메트릭 활용 예시
@app.get("/ddtrace-order/{order_id}")
def ddtrace_order_endpoint(order_id: str):
    with dd_tracer.trace("business.process_order") as span:
        span.set_tag("order.id", order_id)
        span.set_tag("order.status", "processing")
        span.set_tag("payment.method", "credit_card")
        
        amount = random.randint(1000, 50000)
        span.set_metric("order.amount", amount)
        span.set_metric("order.item_count", 3)
        
        time.sleep(0.1)
        span.set_tag("order.status", "completed")
    return {"order_id": order_id, "amount": amount, "status": "completed"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
