#!/bin/bash

# 사용법: ./split_json.sh <input.json> <title> [chunk_size] [output_dir]
# 예시: ./split_json.sh data.json mydata 20 output_folder

# 기본값 설정
DEFAULT_CHUNK_SIZE=20
DEFAULT_OUTPUT_DIR="split_json_output"

# 인자 확인
if [ $# -lt 2 ]; then
    echo "사용법: $0 <input.json> <title> [chunk_size] [output_dir]"
    echo "예시: $0 data.json mydata 20 output_folder"
    echo "  - input.json: 입력 JSON 파일"
    echo "  - title: 출력 파일명 접두사"
    echo "  - chunk_size: 파일당 아이템 개수 (기본값: 20)"
    echo "  - output_dir: 출력 디렉토리 (기본값: split_json_output)"
    exit 1
fi

INPUT_FILE="$1"
TITLE="$2"
CHUNK_SIZE="${3:-$DEFAULT_CHUNK_SIZE}"
OUTPUT_DIR="${4:-$DEFAULT_OUTPUT_DIR}"

# 입력 파일 존재 확인
if [ ! -f "$INPUT_FILE" ]; then
    echo "오류: 파일 '$INPUT_FILE'을 찾을 수 없습니다."
    exit 1
fi

# jq 설치 확인
if ! command -v jq &> /dev/null; then
    echo "오류: jq가 설치되어 있지 않습니다."
    echo "설치 방법:"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  CentOS/RHEL: sudo yum install jq"
    echo "  macOS: brew install jq"
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# JSON 파일이 배열인지 확인
if ! jq -e 'type == "array"' "$INPUT_FILE" > /dev/null 2>&1; then
    echo "오류: JSON 파일이 배열 형태가 아닙니다."
    echo "JSON 파일은 다음과 같은 형태여야 합니다: [item1, item2, item3, ...]"
    exit 1
fi

# 전체 아이템 개수 확인
TOTAL_ITEMS=$(jq 'length' "$INPUT_FILE")
echo "총 아이템 개수: $TOTAL_ITEMS"

# 필요한 파일 개수 계산
TOTAL_FILES=$(( (TOTAL_ITEMS + CHUNK_SIZE - 1) / CHUNK_SIZE ))
echo "생성될 파일 개수: $TOTAL_FILES"
echo "파일당 아이템 개수: $CHUNK_SIZE"
echo "출력 디렉토리: $OUTPUT_DIR"

# 파일 분할 시작
echo ""
echo "파일 분할 시작..."

for (( i=0; i<TOTAL_FILES; i++ )); do
    START_INDEX=$((i * CHUNK_SIZE))
    END_INDEX=$((START_INDEX + CHUNK_SIZE - 1))
    
    # 파일 번호 (1부터 시작하도록 +1)
    FILE_NUMBER=$((i + 1))
    
    # 파일명 생성 (제로 패딩 적용)
    if [ $TOTAL_FILES -lt 10 ]; then
        OUTPUT_FILE="${OUTPUT_DIR}/${TITLE}_${FILE_NUMBER}.json"
    elif [ $TOTAL_FILES -lt 100 ]; then
        OUTPUT_FILE="${OUTPUT_DIR}/${TITLE}_$(printf "%02d" $FILE_NUMBER).json"
    else
        OUTPUT_FILE="${OUTPUT_DIR}/${TITLE}_$(printf "%03d" $FILE_NUMBER).json"
    fi
    
    # JSON 슬라이스 생성 및 저장
    jq ".[$START_INDEX:$((END_INDEX + 1))]" "$INPUT_FILE" > "$OUTPUT_FILE"
    
    # 실제 저장된 아이템 개수 확인
    ACTUAL_ITEMS=$(jq 'length' "$OUTPUT_FILE")
    
    echo "생성됨: $OUTPUT_FILE (아이템 $ACTUAL_ITEMS개)"
done

echo ""
echo "분할 완료!"
echo "총 $TOTAL_FILES개의 파일이 '$OUTPUT_DIR' 디렉토리에 생성되었습니다."

# 결과 요약
echo ""
echo "=== 결과 요약 ==="
echo "원본 파일: $INPUT_FILE"
echo "총 아이템: $TOTAL_ITEMS개"
echo "파일당 아이템: $CHUNK_SIZE개"
echo "생성된 파일: $TOTAL_FILES개"
echo "출력 디렉토리: $OUTPUT_DIR"

# 생성된 파일 목록 표시
echo ""
echo "생성된 파일 목록:"
ls -la "$OUTPUT_DIR"/${TITLE}_*.json

# 검증: 전체 아이템 개수 확인
echo ""
echo "=== 검증 ==="
VERIFICATION_COUNT=0
for file in "$OUTPUT_DIR"/${TITLE}_*.json; do
    if [ -f "$file" ]; then
        COUNT=$(jq 'length' "$file")
        VERIFICATION_COUNT=$((VERIFICATION_COUNT + COUNT))
    fi
done

if [ $VERIFICATION_COUNT -eq $TOTAL_ITEMS ]; then
    echo "✓ 검증 성공: 모든 아이템이 올바르게 분할되었습니다."
else
    echo "✗ 검증 실패: 원본($TOTAL_ITEMS) vs 분할된 파일들의 합($VERIFICATION_COUNT)"
fi
