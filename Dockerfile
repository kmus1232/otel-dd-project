# Dockerfile
FROM python:3.12-slim

# Git 정보를 빌드 인자로 받음
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA

# 환경변수로 설정
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# ddtrace-run을 사용하여 uvicorn 실행 (APM 자동 적용)
CMD ["ddtrace-run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]