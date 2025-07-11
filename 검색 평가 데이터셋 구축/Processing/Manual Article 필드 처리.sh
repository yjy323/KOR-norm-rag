#!/bin/bash

# 사용법: ./script.sh input.json output.json
# 또는: ./script.sh input.json (입력 파일을 직접 수정)

if [ $# -eq 0 ]; then
    echo "사용법: $0 <입력파일> [출력파일]"
    echo "출력파일을 지정하지 않으면 입력파일을 직접 수정합니다."
    exit 1
fi

input_file="$1"
output_file="${2:-$input_file}"

# 입력 파일이 존재하는지 확인
if [ ! -f "$input_file" ]; then
    echo "오류: 입력 파일 '$input_file'이 존재하지 않습니다."
    exit 1
fi

# jq가 설치되어 있는지 확인
if ! command -v jq &> /dev/null; then
    echo "오류: jq가 설치되어 있지 않습니다. 다음 명령어로 설치하세요:"
    echo "Ubuntu/Debian: sudo apt-get install jq"
    echo "macOS: brew install jq"
    echo "CentOS/RHEL: sudo yum install jq"
    exit 1
fi

# 임시 파일 생성
temp_file=$(mktemp)

# JSON 처리: manual_article이 있는 객체에서 article을 덮어쓰고 code 제거
jq '
    map(
        if .output.manual_article then
            .output.article = .output.manual_article |
            del(.output.manual_article) |
            del(.output.code)
        else
            .
        end
    )
' "$input_file" > "$temp_file"

# jq 실행 결과 확인
if [ $? -eq 0 ]; then
    # 성공적으로 처리된 경우 결과를 출력 파일로 이동
    mv "$temp_file" "$output_file"
    echo "처리 완료: $output_file"
else
    # 오류 발생 시 임시 파일 삭제
    rm -f "$temp_file"
    echo "오류: JSON 처리 중 문제가 발생했습니다."
    exit 1
fi
