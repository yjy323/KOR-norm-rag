#!/bin/bash

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 사용법 출력
usage() {
    echo "사용법: $0 <규칙제목파일.txt> <JSON파일.json>"
    echo "예시: $0 규칙제목.txt data.json"
    exit 1
}

# 파라미터 확인
if [ $# -ne 2 ]; then
    usage
fi

RULES_FILE="$1"
JSON_FILE="$2"

# 파일 존재 확인
if [ ! -f "$RULES_FILE" ]; then
    echo -e "${RED}❌ 규칙 제목 파일을 찾을 수 없습니다: $RULES_FILE${NC}"
    exit 1
fi

if [ ! -f "$JSON_FILE" ]; then
    echo -e "${RED}❌ JSON 파일을 찾을 수 없습니다: $JSON_FILE${NC}"
    exit 1
fi

# jq 설치 확인
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq가 설치되지 않았습니다. 다음 명령어로 설치해주세요:${NC}"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  macOS: brew install jq"
    echo "  CentOS/RHEL: sudo yum install jq"
    exit 1
fi

echo -e "${BLUE}📋 규칙 검색 및 누락 확인 시작${NC}"
echo "=================================================="
echo "규칙 파일: $RULES_FILE"
echo "JSON 파일: $JSON_FILE"
echo ""

# 임시 파일들
TEMP_RULES=$(mktemp)
FOUND_RULES=$(mktemp)
MISSING_RULES=$(mktemp)

# 정리 함수
cleanup() {
    rm -f "$TEMP_RULES" "$FOUND_RULES" "$MISSING_RULES"
}
trap cleanup EXIT

# 규칙 제목만 추출 (번호와 점 제거)
grep -E "^[ ]*[0-9]+\." "$RULES_FILE" | sed 's/^[ ]*[0-9]*\. *//' > "$TEMP_RULES"

total_rules=$(wc -l < "$TEMP_RULES")
found_count=0
missing_count=0

echo -e "${YELLOW}🔍 JSON 파일에서 규칙 검색 중...${NC}"
echo ""

# 각 규칙을 JSON에서 검색
while IFS= read -r rule; do
    if [ -z "$rule" ]; then
        continue
    fi
    
    # JSON에서 해당 규칙 검색 (대소문자 구분 없이)
    # 규칙 제목이 JSON의 어느 필드에든 포함되어 있는지 확인
    if jq -r 'recurse | if type == "string" then . else empty end' "$JSON_FILE" | grep -i -F "$rule" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 발견됨: $rule${NC}"
        echo "$rule" >> "$FOUND_RULES"
        ((found_count++))
    else
        echo -e "${RED}❌ 누락됨: $rule${NC}"
        echo "$rule" >> "$MISSING_RULES"
        ((missing_count++))
    fi
done < "$TEMP_RULES"

echo ""
echo "=================================================="
echo -e "${BLUE}📊 검색 결과 요약${NC}"
echo "=================================================="
echo -e "전체 규칙 수: ${BLUE}$total_rules${NC}"
echo -e "발견된 규칙: ${GREEN}$found_count${NC}"
echo -e "누락된 규칙: ${RED}$missing_count${NC}"

# 누락된 규칙이 있는 경우 상세 출력
if [ $missing_count -gt 0 ]; then
    echo ""
    echo -e "${RED}🚨 JSON 파일에서 발견되지 않은 규칙들:${NC}"
    echo "=================================================="
    
    counter=1
    while IFS= read -r missing_rule; do
        if [ -n "$missing_rule" ]; then
            printf "%3d. %s\n" "$counter" "$missing_rule"
            ((counter++))
        fi
    done < "$MISSING_RULES"
    
    # 누락된 규칙을 파일로 저장
    missing_output_file="missing_rules_$(date +%Y%m%d_%H%M%S).txt"
    {
        echo "JSON 파일에서 발견되지 않은 규칙들"
        echo "생성일시: $(date)"
        echo "JSON 파일: $JSON_FILE"
        echo "=================================================="
        echo ""
        counter=1
        while IFS= read -r missing_rule; do
            if [ -n "$missing_rule" ]; then
                printf "%3d. %s\n" "$counter" "$missing_rule"
                ((counter++))
            fi
        done < "$MISSING_RULES"
        echo ""
        echo "총 $missing_count개의 규칙이 누락되었습니다."
    } > "$missing_output_file"
    
    echo ""
    echo -e "${YELLOW}💾 누락된 규칙 목록이 저장되었습니다: $missing_output_file${NC}"
    
    # 통계 정보
    coverage=$(echo "scale=2; $found_count * 100 / $total_rules" | bc -l)
    echo -e "${YELLOW}📈 규칙 커버리지: ${coverage}%${NC}"
    
    exit 1
else
    echo ""
    echo -e "${GREEN}🎉 모든 규칙이 JSON 파일에서 발견되었습니다!${NC}"
    echo -e "${GREEN}📈 규칙 커버리지: 100%${NC}"
    exit 0
fi
