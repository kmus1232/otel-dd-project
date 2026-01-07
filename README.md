# FastAPI + Datadog APM 데모 애플리케이션

Datadog APM과 OpenTelemetry를 연동한 FastAPI 데모 앱입니다.

## 사전 요구사항

- Docker & Docker Compose
- Datadog 계정 및 API Key

## 실행 방법

1. `.env` 파일 생성
```bash
cp .env.example .env
# .env 파일에 Datadog API 키 입력
```

2. 컨테이너 실행
```bash
docker-compose up --build
```

## API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 기본 헬스체크 (0.1~0.5초 랜덤 지연) |
| `/error` | GET | 에러 트래킹 테스트 (50% 확률로 에러 발생) |
| `/otel-payment/{order_id}` | GET | OpenTelemetry 커스텀 스팬 테스트 |

## 테스트 예시

```bash
# 기본 요청
curl http://localhost:8000/

# 에러 테스트
curl http://localhost:8000/error

# OTel 결제 로직 테스트
curl http://localhost:8000/otel-payment/ORDER-123
```

## Datadog 설정

### 환경 변수

| 변수 | 값 | 설명 |
|------|-----|------|
| `DD_SERVICE` | my-fastapi-service | Datadog에 표시될 서비스 이름 |
| `DD_ENV` | dev | 환경 (prod, dev, stg) |
| `DD_VERSION` | 1.0.0 | 애플리케이션 버전 |
| `DD_TRACE_OTEL_ENABLED` | true | OpenTelemetry 연동 활성화 |

### Datadog에서 확인

1. APM > Services에서 `my-fastapi-service` 확인
2. 환경: `dev`, 버전: `1.0.0`으로 필터링 가능
3. `/otel-payment` 호출 시 커스텀 스팬 확인 가능:
   - `business.payment_processing`
   - `business.validate_card`

## 주의사항

⚠️ `.env` 파일에 Datadog API 키를 설정해야 합니다.  
`.env` 파일은 `.gitignore`에 포함되어 있어 git에 올라가지 않습니다.

## 프로젝트 구조

```
.
├── main.py              # FastAPI 애플리케이션
├── Dockerfile           # 컨테이너 빌드 설정
├── docker-compose.yaml  # 멀티 컨테이너 구성
├── requirements.txt     # Python 의존성
├── .env.example         # 환경변수 템플릿
├── .gitignore           # Git 제외 파일 목록
└── README.md            # 이 문서
```
