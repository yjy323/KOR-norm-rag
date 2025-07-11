#!/bin/bash

# 사용법: ./extract_unknown_articles.sh input.json

if [ $# -eq 0 ]; then
    echo "사용법: $0 <JSON_FILE>"
    echo "예시: $0 data.json"
    exit 1
fi

JSON_FILE="$1"

if [ ! -f "$JSON_FILE" ]; then
    echo "오류: 파일 '$JSON_FILE'을 찾을 수 없습니다."
    exit 1
fi

# jq를 사용하여 output.article이 정확히 "Unknown Article"인 객체만 추출
jq '.[] | select(.output.article == "Unknown Article")' "$JSON_FILE"
