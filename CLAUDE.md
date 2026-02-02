# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

RFP Auto는 LLM 기반 멀티 에이전트 시스템으로 한글(HWP) 문서를 자동으로 분석하고 채웁니다. 복잡한 표 구조, 병합된 셀, 다양한 레이아웃을 지능적으로 처리합니다.

### 핵심 목표
- **지능형 문서 처리**: 에이전트가 상황을 판단하고 적절히 대응
- **복잡한 구조 지원**: 병합 셀, 다중 표, 비정형 레이아웃
- **높은 정확도**: 90%+ 목표
- **확장 가능한 아키텍처**: 새로운 에이전트 추가 용이

---

## 멀티 에이전트 아키텍처

### 전체 구조

```
👤 User (사용자)
   ↕️ 대화
🧠 Supervisor Agent (조율자)
   ├─→ 📋 Planner Agent (계획 수립)
   ├─→ 📂 Analyzer Agent (문서 분석)
   ├─→ 🤖 Mapper Agent (데이터 매핑)
   └─→ ✍️ Writer Agent (문서 작성)
```

### 워크플로우 예시

#### 간단한 경우 (표준 워크플로우)
```
👤: "이 문서 채워줘"
   ↓
🧠 Supervisor: "표준 워크플로우 시작"
   ↓
📂 Analyzer → "3개 표, 단순 구조"
   ↓
🤖 Mapper → "50개 셀 매핑 완료"
   ↓
✍️ Writer → "50개 셀 작성 완료"
   ↓
🧠 Supervisor → 👤: "✅ 완료!"
```

#### 복잡한 경우 (Plan 먼저)
```
👤: "복잡한 RFP 문서 처리해줘"
   ↓
🧠 Supervisor: "복잡해 보임, 계획 수립 필요"
   ↓
📋 Planner → "5단계 계획 수립"
   1. 문서 구조 상세 분석
   2. 표별 타입 분류
   3. 병합 셀 처리 전략
   4. 데이터 매핑
   5. 단계별 검증하며 작성
   ↓
🧠 Supervisor: "계획 승인, 실행"
   ↓
📂 Analyzer (상세 모드) → "5개 표, 병합 셀 다수, 비정형"
   ↓
🤖 Mapper → "표별 전략 적용하여 매핑"
   ↓
✍️ Writer (단계별) → "검증하며 작성"
   ↓
🧠 Supervisor → 👤: "✅ 완료! 보고서 첨부"
```

---

## 에이전트 상세 설명

### 1. 🧠 Supervisor Agent (조율자)

**역할**: 전체 작업 조율 및 의사 결정

**책임**:
- 사용자 요청 해석
- 작업 복잡도 판단
- 적절한 서브 에이전트 선택 및 호출
- 에러 발생 시 복구 전략 결정
- 결과 통합 및 사용자 응답

**의사 결정 예시**:
```
IF 문서가 복잡함:
    → Planner Agent 먼저 호출
ELSE:
    → 바로 Analyzer Agent 호출

IF 매핑 실패율 > 20%:
    → Mapper에게 재시도 지시 (다른 프롬프트)

IF 특정 표 처리 실패:
    → Analyzer에게 해당 표 재분석 요청

IF 사용자 확인 필요:
    → 사용자에게 질문 후 계속
```

**상태 추적**:
```python
{
    "phase": "mapping",  # planning, analyzing, mapping, writing
    "progress": 60,      # 진행률
    "structure": {...},  # 분석된 문서 구조
    "fill_plan": {...},  # 매핑 계획
    "result": {...},     # 작성 결과
    "errors": [],        # 발생한 에러들
}
```

### 2. 📋 Planner Agent (계획 수립)

**역할**: 복잡한 작업에 대한 실행 계획 수립

**활성화 조건**:
- 문서에 5개 이상의 표
- 병합 셀이 전체의 30% 이상
- 비정형 레이아웃 감지
- 사용자가 명시적으로 "계획 먼저" 요청
- 이전 시도가 실패한 경우

**출력 예시**:
```
계획서:
1. 문서 구조 분석
   - 각 표의 타입 식별
   - 병합 셀 패턴 파악
   - 데이터 입력 영역 식별

2. 표별 처리 전략
   - 표 0 (회사정보): 라벨-값 매핑 방식
   - 표 1 (경력사항): 반복 구조 처리
   - 표 2 (예산): 수식 계산 필요

3. 데이터 매핑 전략
   - 명확한 매핑: 즉시 처리
   - 애매한 매핑: 신뢰도 0.7 미만 → 사용자 확인

4. 작성 순서
   - 단순 표부터 (0, 2)
   - 복잡한 표 나중에 (1)

5. 검증 체크포인트
   - 각 표 완료 시 검증
   - 전체 완료 후 최종 검증
```

**Tools**:
- `analyze_complexity(doc_structure)`: 복잡도 평가
- `identify_challenges(doc_structure)`: 난관 식별
- `create_strategy(challenges)`: 전략 수립

### 3. 📂 Analyzer Agent (문서 분석)

**역할**: HWP 문서 구조 파악 (읽기 전용)

**분석 모드**:
- **간단 모드**: 기본 구조만 (표 개수, 행/열)
- **상세 모드**: 병합 셀, 표 타입, 레이아웃 패턴

**출력 구조**:
```
{
    "document": {
        "pages": 5,
        "total_tables": 3,
        "complexity": "medium"
    },
    "tables": [
        {
            "index": 0,
            "type": "company_info",
            "position": {"page": 1, "top": 100},
            "structure": {
                "rows": 7,
                "cols": 4,
                "total_cells": 28,
                "merged_cells_count": 3
            },
            "cells": {
                "A1": {"content": "회사명", "is_label": true},
                "B1": {"content": "", "is_data": true},
                "B2:D2": {"content": "", "is_merged": true, "master": "B2"}
            },
            "patterns": {
                "label_columns": ["A", "C"],
                "data_columns": ["B", "D"],
                "layout_type": "label-value-pairs"
            }
        },
        ...
    ]
}
```

**Tools**:
- `inspect_document(doc_path)`: 문서 기본 정보
- `extract_table_structure(table_index, detail_level)`: 표 구조 추출
- `detect_merged_cells(table_index)`: 병합 셀 감지
- `classify_table_type(table_structure)`: 표 타입 분류
- `identify_layout_pattern(table_structure)`: 레이아웃 패턴 인식

**병합 셀 감지 알고리즘**:
```
논리적 위치로 이동 → 실제 위치 확인
IF 논리적 ≠ 실제:
    → 병합됨
    → 경계 탐색으로 범위 파악
```

### 4. 🤖 Mapper Agent (데이터 매핑)

**역할**: LLM을 활용하여 "어디에 무엇을" 결정

**입력**:
- 분석된 문서 구조 (Analyzer 결과)
- 채울 데이터 (구조화된 딕셔너리 또는 자유 텍스트)
- 매핑 전략 (Planner가 제공한 경우)

**출력**:
```
{
    "mappings": [
        {
            "table_index": 0,
            "cell": "B1",
            "content": "(주)에스티이노베이션",
            "source_field": "회사명",
            "confidence": 0.98,
            "reasoning": "라벨 'A1:회사명'과 정확히 매칭"
        },
        {
            "table_index": 0,
            "cell": "B2",
            "content": "AI 자동화 시스템",
            "source_field": "사업분야",
            "confidence": 0.85,
            "reasoning": "병합 셀, 사업분야 내용 적합"
        }
    ],
    "statistics": {
        "total": 50,
        "high_confidence": 45,  # > 0.9
        "medium_confidence": 4, # 0.7-0.9
        "low_confidence": 1,    # < 0.7
        "unmapped_data": ["홈페이지"]  # 매핑 못 한 데이터
    },
    "warnings": [
        "경력사항 데이터가 부족합니다. 3개 필요, 2개만 제공됨"
    ]
}
```

**LLM 프롬프트 전략**:
```
System: 당신은 HWP 문서 매핑 전문가입니다.

표 구조:
- 표 0: 회사정보 (라벨-값 쌍)
  A1: "회사명" → B1: (빈칸)
  A2: "사업분야" → B2:D2(병합): (빈칸)

데이터:
- 회사명: "(주)에스티이노베이션"
- 사업분야: "AI 기반 자동화"

규칙:
1. 병합 셀은 마스터 셀에만 작성
2. 라벨과 데이터의 의미적 연결
3. 신뢰도 0.7 미만은 경고

JSON으로 매핑 결과 반환.
```

**Tools**:
- `call_llm_for_mapping(structure, data, strategy)`: LLM 매핑 요청
- `validate_mappings(mappings, structure)`: 매핑 유효성 검증
- `calculate_confidence(mapping, context)`: 신뢰도 계산
- `find_alternative_mappings(failed_mapping)`: 대안 찾기

**검증 체크**:
- 셀 주소가 존재하는가?
- 병합 셀의 마스터 셀인가?
- 데이터 타입이 적절한가? (숫자 칸에 텍스트?)
- 길이 제한 초과하지 않는가?

### 5. ✍️ Writer Agent (문서 작성)

**역할**: 실제 HWP 문서에 데이터 쓰기

**작성 모드**:
- **일괄 모드**: 모든 매핑 한 번에 처리 (빠름, 검증 나중)
- **단계별 모드**: 표별로 처리하며 검증 (느림, 안전)
- **신중 모드**: 셀 하나씩 검증 (매우 느림, 최대 안전)

**실행 흐름**:
```
FOR EACH mapping:
    1. 해당 표로 이동 (table_index)
    2. 목표 셀로 이동 (cell address)
       - 최적 경로 계산 (UP/DOWN/LEFT/RIGHT 조합)
       - 병합 셀 고려
    3. 텍스트 삽입
    4. 검증 (선택적)
       - 셀 내용 다시 읽기
       - 삽입한 내용과 비교
    5. 결과 기록
```

**출력**:
```
{
    "summary": {
        "total": 50,
        "success": 48,
        "failed": 2,
        "skipped": 0
    },
    "details": [
        {
            "mapping_id": "table0_B1",
            "status": "success",
            "cell": "B1",
            "content": "(주)에스티이노베이션",
            "verified": true
        },
        {
            "mapping_id": "table1_C5",
            "status": "failed",
            "cell": "C5",
            "error": "NavigationError: 셀 C5로 이동 실패",
            "retry_count": 3
        }
    ],
    "failed_mappings": [
        {/* 재시도 가능한 매핑 정보 */}
    ]
}
```

**Tools**:
- `navigate_to_table(hwp, table_index)`: 특정 표로 이동
- `navigate_to_cell(hwp, cell, table_structure)`: 특정 셀로 이동
- `insert_text(hwp, text)`: 텍스트 삽입
- `verify_insertion(hwp, expected_text)`: 삽입 검증
- `batch_write(hwp, mappings, mode)`: 여러 셀 처리
- `retry_failed(hwp, failed_mappings)`: 실패한 작업 재시도

**에러 복구**:
```
IF 네비게이션 실패:
    1. A1으로 리셋 후 재시도
    2. 여전히 실패 → Analyzer에게 해당 표 재분석 요청
    3. 재분석 후 재시도

IF 텍스트 삽입 실패:
    1. 3번까지 재시도
    2. 실패 목록에 추가 → Supervisor에게 보고

IF 검증 실패 (내용 불일치):
    1. 다시 삽입 시도
    2. 여전히 불일치 → 경고 발생
```

---

## 에이전트 간 통신

### 데이터 흐름

```
Supervisor
    ↓ (문서 경로)
Analyzer
    ↓ (문서 구조)
Mapper
    ↓ (매핑 계획)
Writer
    ↓ (작성 결과)
Supervisor
    ↓ (최종 결과)
User
```

### 메시지 형식

모든 에이전트는 표준 메시지 형식 사용:
```
{
    "agent": "Analyzer",
    "status": "success" | "failed" | "warning",
    "data": {/* 에이전트별 출력 */},
    "metadata": {
        "execution_time": 2.5,  # 초
        "timestamp": "2026-02-02T15:30:00",
        "version": "1.0"
    },
    "errors": [],
    "warnings": []
}
```

### Supervisor의 조율 로직

```
FUNCTION supervise(user_request, doc_path, data):
    state = initialize_state()

    # 1. 복잡도 판단
    IF requires_planning(user_request, doc_path):
        plan = Planner.create_plan(doc_path)
        state.plan = plan

    # 2. 분석
    IF state.has_plan:
        analysis = Analyzer.analyze(doc_path, detail="high", strategy=plan.analysis_strategy)
    ELSE:
        analysis = Analyzer.analyze(doc_path, detail="basic")

    state.structure = analysis

    # 3. 매핑
    mapping = Mapper.map(state.structure, data, strategy=state.plan?.mapping_strategy)

    IF mapping.low_confidence_count > threshold:
        # 사용자 확인 필요
        confirmed = ask_user(mapping.low_confidence_items)
        mapping = update_with_user_input(mapping, confirmed)

    state.fill_plan = mapping

    # 4. 작성
    result = Writer.write(doc_path, state.fill_plan, mode=select_mode(state))

    IF result.failed > 0:
        # 재시도
        retry_result = Writer.retry(result.failed_mappings)
        result = merge_results(result, retry_result)

    # 5. 최종 보고
    RETURN format_final_result(state, result)
```

---

## Tools 아키텍처

각 에이전트는 전용 Tools만 접근:

### Planner Tools
- 읽기 전용: `inspect_document`, `analyze_complexity`
- 전략 수립: `create_strategy`, `estimate_difficulty`

### Analyzer Tools
- HWP 읽기: `extract_table_structure`, `detect_merged_cells`
- 분류: `classify_table_type`, `identify_pattern`

### Mapper Tools
- LLM 호출: `call_llm_for_mapping`
- 검증: `validate_mappings`, `calculate_confidence`

### Writer Tools
- HWP 쓰기: `navigate_to_cell`, `insert_text`
- 검증: `verify_insertion`, `retry_failed`

### Supervisor Tools
- 에이전트 호출: `call_agent(agent_name, params)`
- 사용자 상호작용: `ask_user(question)`, `show_progress(status)`

---

## 실행 환경

### 필수 요구사항
- Windows OS (pywin32)
- Python 3.13+
- HWP 설치
- OpenAI API 키

### 환경 설정
```bash
# 가상환경 활성화
.venv\Scripts\activate

# 환경 변수
set OPENAI_API_KEY=your_key
```

### 디렉토리 구조
```
rfp_auto/
├── agents/              # 에이전트 구현
│   ├── supervisor.py    # Supervisor Agent
│   ├── planner.py       # Planner Agent
│   ├── analyzer.py      # Analyzer Agent
│   ├── mapper.py        # Mapper Agent
│   └── writer.py        # Writer Agent
├── tools/               # Tools 구현
│   ├── hwp_tools.py     # HWP COM 조작
│   ├── llm_tools.py     # LLM 호출
│   └── validation.py    # 검증
├── core/                # 공통 기능
│   ├── state.py         # 상태 관리
│   ├── messages.py      # 메시지 형식
│   └── exceptions.py    # 예외 정의
├── models/              # 데이터 모델
│   ├── document.py      # 문서 구조
│   ├── mapping.py       # 매핑 계획
│   └── result.py        # 실행 결과
└── main.py              # 진입점
```

---

## 사용 예시

### 간단한 사용
```python
from agents.supervisor import SupervisorAgent

supervisor = SupervisorAgent()

result = supervisor.process(
    user_request="이 문서 채워줘",
    doc_path="FRAME/제안서.hwpx",
    data={
        "회사명": "(주)에스티이노베이션",
        "대표자": "권민수",
        ...
    }
)

print(result.summary)
# → "✅ 완료! 50개 셀 채웠습니다 (성공 48, 실패 2)"
```

### 복잡한 문서 (Plan 먼저)
```python
result = supervisor.process(
    user_request="복잡한 RFP 문서 처리해줘",
    doc_path="sample/복잡한_제안서.hwp",
    data=large_dataset,
    options={
        "force_planning": True,  # 계획 강제
        "detail_level": "high",  # 상세 분석
        "write_mode": "step_by_step"  # 단계별 작성
    }
)
```

### 에이전트별 독립 사용
```python
# 분석만
from agents.analyzer import AnalyzerAgent

analyzer = AnalyzerAgent()
structure = analyzer.analyze("test.hwpx", detail="high")

# 매핑만
from agents.mapper import MapperAgent

mapper = MapperAgent()
mappings = mapper.map(structure, data)
```

---

## 성능 및 확장성

### 예상 성능
- **간단한 문서** (3개 표, 50셀): ~15초
  - 분석: 3초
  - 매핑 (LLM): 5초
  - 작성: 5초
  - 검증: 2초

- **복잡한 문서** (10개 표, 200셀, Plan 포함): ~60초
  - 계획: 10초
  - 분석: 15초
  - 매핑: 20초
  - 작성: 15초

### 확장 방법

**새 에이전트 추가**:
```python
# agents/validator.py
class ValidatorAgent:
    """문서 검증 전담 에이전트"""

    def validate(self, doc_path, expected_data):
        # 문서 전체 검증 로직
        pass

# supervisor.py에 통합
class SupervisorAgent:
    def __init__(self):
        ...
        self.validator = ValidatorAgent()  # 추가
```

**새 Tool 추가**:
```python
# tools/advanced_hwp_tools.py
@tool
def extract_images(hwp) -> list:
    """문서의 이미지 추출"""
    pass

# Analyzer에 추가
class AnalyzerAgent:
    def __init__(self):
        self.tools = [..., extract_images]  # 추가
```

---

## 문제 해결

### 일반적인 시나리오

**시나리오 1: 매핑 정확도 낮음**
```
문제: Mapper가 잘못된 셀에 매핑
해결:
1. Analyzer에게 더 상세한 분석 요청
2. Mapper에게 다른 프롬프트 전략 지시
3. 사용자에게 애매한 매핑 확인 요청
```

**시나리오 2: 특정 표 작성 실패**
```
문제: Writer가 표 2 작성 실패
해결:
1. Analyzer에게 표 2만 재분석 요청
2. 병합 셀 패턴 재확인
3. 다른 네비게이션 전략 시도
4. 실패 보고 및 수동 개입 요청
```

**시나리오 3: 복잡한 비정형 문서**
```
문제: 표준 워크플로우로 처리 불가
해결:
1. Planner Agent 활성화
2. 문서별 커스텀 전략 수립
3. 단계별 검증하며 진행
4. 필요시 사용자와 대화형 진행
```

---

## 마이그레이션

### 기존 코드 활용
```python
# 기존 utils.py의 함수들을 Tools로 래핑
from utils import hwp_open, count_tables, table_extract

# tools/hwp_tools.py
@tool
def inspect_document_legacy(doc_path):
    hwp = hwp_open(doc_path, view=False)
    table_count = count_tables(hwp)
    return {"tables_count": table_count}
```

### 점진적 전환
1. Supervisor 먼저 구현
2. Analyzer Agent 구현 (기존 utils 재사용)
3. Mapper Agent 구현
4. Writer Agent 구현
5. Planner Agent 추가 (선택적)

---

## 핵심 설계 원칙

1. **에이전트 자율성**: 각 에이전트는 독립적으로 판단하고 행동
2. **명확한 책임**: 에이전트별 역할이 겹치지 않음
3. **유연한 조율**: Supervisor가 상황에 맞게 전략 변경
4. **단계적 검증**: 각 단계마다 결과 확인
5. **에러 복구**: 실패 시 자동 재시도 및 대안 모색
6. **사용자 중심**: 필요시 사용자와 대화하며 진행

---

## 참고

### 기존 파일
- [utils.py](utils.py): 기존 HWP 조작 함수 (Tools로 재사용 가능)
- [config.py](config.py): 설정 및 프롬프트 템플릿
- [main.py](main.py): 기존 워크플로우 (참고용)

### HWP COM API
- [HWP Actions](https://help.hancom.com/hoffice100/en-US/Hwp/hwpbase/action(hwp).htm)
- [표 조작](https://help.hancom.com/hoffice100/en-US/Hwp/table/tableattribute/table(cellattribute).htm)

### 멀티 에이전트 패턴
- Supervisor Pattern: 중앙 조율자가 서브 에이전트 관리
- Hierarchical Task Network: 복잡한 작업을 계층적으로 분해
- Plan-Execute-Verify: 계획 → 실행 → 검증 사이클
