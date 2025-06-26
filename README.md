# Korean Grammar RAG MVP

> 한국어 어문 규범 기반 생성(RAG) 모델 - 최소 기능 제품(MVP)

## 🎯 프로젝트 개요

국립국어원 2025년 인공지능의 한국어 능력 평가 경진대회를 위한 한국어 어문 규범 RAG 모델입니다. 베이스라인 성능(Final Score 42.19%)을 개선하여 상위권 달성을 목표로 합니다.

### 주요 특징
- 📊 **체계적 모듈화**: 기능별 독립적 모듈 설계
- 🚀 **점진적 개선**: MVP → 고도화 단계별 발전
- 🔧 **확장 가능**: 플러그인 아키텍처로 새로운 기능 추가 용이
- 📈 **성능 추적**: 실시간 성능 모니터링 및 비교

## 📁 프로젝트 구조

```
korean_grammar_rag_mvp/
├── config/                 # 설정 파일
├── data/                   # 데이터 디렉토리
├── src/                    # 소스 코드
│   ├── data_processor/     # 데이터 처리
│   ├── model/              # 모델 관리
│   ├── prompts/            # 프롬프트 관리
│   ├── knowledge/          # 지식 관리
│   ├── evaluation/         # 평가 시스템
│   └── pipeline/           # 실행 파이프라인
├── scripts/                # 실행 스크립트
├── tests/                  # 테스트 코드
└── outputs/                # 출력 결과
```

## 📊 성능 목표

### MVP 목표 (1주일)
| 메트릭 | 베이스라인 | MVP 목표 | 개선률 |
|--------|------------|----------|--------|
| Final Score | 42.19% | 45-47% | 5-12% |
| Exact Match | 34.5% | 38-40% | 10-15% |
| ROUGE-1 | 26.0% | 28-30% | 8-15% |

## 🔧 설정 관리

### 모델 설정 (config/model_config.yaml)
```yaml
models:
  qwen3_8b:
    model_path: "Qwen/Qwen3-8B"
    device: "cuda:0"
    max_length: 512
    temperature: 0.7
    
  hyperclova:
    model_path: "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B"
    device: "cuda:0"
    max_length: 512
    temperature: 0.3
```

### 프롬프트 설정 (config/prompt_config.yaml)
```yaml
prompts:
  selection_prompt:
    system: "당신은 한국어 어문 규범 전문가입니다."
    template: "다음 문제를 해결하세요: {question}"
    few_shot_count: 3
    
  correction_prompt:
    system: "당신은 한국어 어문 규범 전문가입니다."
    template: "다음 문장을 교정하세요: {question}"
    few_shot_count: 3
```

## 🚀 점진적 개선 로드맵

### Week 1: MVP 완성
- [ ] 기본 파이프라인 구축
- [ ] 베이스라인 재현
- [ ] 간단한 프롬프트 개선
- [ ] 기본 지식베이스 구축
