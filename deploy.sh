#!/bin/bash

# Git 정보 자동 추출
export DD_GIT_REPOSITORY_URL=$(git config --get remote.origin.url)
export DD_GIT_COMMIT_SHA=$(git rev-parse HEAD)

echo "📦 Git Info:"
echo "  Repository: $DD_GIT_REPOSITORY_URL"
echo "  Commit: $DD_GIT_COMMIT_SHA"

# 기존 컨테이너 정리 후 새로 빌드 & 실행
docker compose down
docker compose build
docker compose up -d

echo "✅ Done! Containers are running."
