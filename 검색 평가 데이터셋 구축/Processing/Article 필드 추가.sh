#!/bin/bash

# 사용법: ./add_article_field.sh input.json [output.json]
# output.json을 지정하지 않으면 원본 파일을 수정합니다.

if [ $# -eq 0 ]; then
    echo "사용법: $0 <input.json> [output.json]"
    echo "예시: $0 data.json"
    echo "예시: $0 data.json modified_data.json"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-$INPUT_FILE}"

# 입력 파일 존재 확인
if [ ! -f "$INPUT_FILE" ]; then
    echo "오류: 파일 '$INPUT_FILE'을 찾을 수 없습니다."
    exit 1
fi

# jq가 설치되어 있는지 확인
if ! command -v jq &> /dev/null; then
    echo "오류: jq가 설치되어 있지 않습니다."
    echo "Ubuntu/Debian: sudo apt-get install jq"
    echo "CentOS/RHEL: sudo yum install jq"
    echo "macOS: brew install jq"
    exit 1
fi

# 백업 파일 생성 (원본 파일을 수정하는 경우)
if [ "$INPUT_FILE" = "$OUTPUT_FILE" ]; then
    BACKUP_FILE="${INPUT_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$INPUT_FILE" "$BACKUP_FILE"
    echo "백업 파일 생성: $BACKUP_FILE"
fi

# JSON 파일 처리
echo "처리 중: $INPUT_FILE"

# jq를 사용하여 output 객체에 article 필드 추가
jq '
def add_article_to_output:
    if type == "object" then
        if has("output") and (.output | type == "object") then
            .output |= (. + {"article": ""})
        else
            .
        end |
        map_values(add_article_to_output)
    elif type == "array" then
        map(add_article_to_output)
    else
        .
    end;

add_article_to_output
' "$INPUT_FILE" > "$OUTPUT_FILE"

# 결과 확인
if [ $? -eq 0 ]; then
    echo "성공적으로 처리되었습니다: $OUTPUT_FILE"
    
    # 처리된 항목 개수 확인
    MODIFIED_COUNT=$(jq '[.. | objects | select(has("output") and (.output | type == "object"))] | length' "$OUTPUT_FILE")
    echo "수정된 output 객체 개수: $MODIFIED_COUNT"
    
    # 샘플 출력 (첫 번째 output 객체)
    echo ""
    echo "샘플 결과:"
    jq '[.. | objects | select(has("output") and (.output | type == "object"))] | .[0].output' "$OUTPUT_FILE" 2>/dev/null || echo "처리된 데이터가 없습니다."
else
    echo "오류: JSON 처리 중 문제가 발생했습니다."
    exit 1
fi
