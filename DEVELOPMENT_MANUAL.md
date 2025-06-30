# 한국 언론사 미디어 프레이밍 분석기 - 개발 매뉴얼

## 📋 목차
1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [LangGraph 워크플로우](#3-langgraph-워크플로우)
4. [모듈별 상세 분석](#4-모듈별-상세-분석)
5. [데이터 플로우](#5-데이터-플로우)
6. [상태 관리](#6-상태-관리)
7. [실시간 스트리밍](#7-실시간-스트리밍)
8. [API 연동](#8-api-연동)
9. [배포 가이드](#9-배포-가이드)
10. [테스트 방법](#10-테스트-방법)
11. [확장 방법](#11-확장-방법)
12. [트러블슈팅](#12-트러블슈팅)

---

## 1. 프로젝트 개요

### 1.1 핵심 목표
- **실시간 미디어 프레이밍 분석**: 한국 주요 언론사들의 동일 이슈에 대한 보도 관점 차이 분석
- **LangGraph 기반 워크플로우**: 6단계 자동화된 분석 파이프라인
- **실시간 추적**: 각 단계별 진행 상황과 결과를 실시간으로 사용자에게 제공

### 1.2 기술 스택
- **Frontend**: Streamlit (웹 인터페이스)
- **Workflow Engine**: LangGraph (상태 기반 워크플로우)
- **LLM Framework**: LangChain + OpenAI GPT
- **Data Collection**: 네이버 뉴스 API + RSS 피드
- **Real-time Processing**: Python Generator + Streamlit 실시간 UI
- **State Management**: TypedDict 기반 상태 관리

### 1.3 프로젝트 구조
```
test_v01/
├── streamlit_app.py           # 메인 웹 인터페이스
├── streaming_workflow.py      # 실시간 스트리밍 워크플로우
├── news_workflow.py           # LangGraph 기반 뉴스 분석 워크플로우
├── workflow_nodes.py          # 6개 워크플로우 노드 구현
├── enhanced_news_fetcher.py   # 하이브리드 뉴스 수집기
├── news_fetcher.py           # 네이버 뉴스 API (레거시)
├── news_analyzer.py          # OpenAI 기반 분석 (레거시)
├── report_generator.py       # 보고서 생성 (레거시)
├── requirements.txt          # 패키지 의존성
├── config_example.py         # API 설정 예시
├── secrets_example.toml      # Secrets 설정 예시
├── deployment_guide.md       # 배포 가이드
└── README.md                # 프로젝트 문서
```

---

## 2. 시스템 아키텍처

### 2.1 레이어별 구조

#### 📱 Frontend Layer
- **streamlit_app.py**: 메인 웹 인터페이스
  - 사용자 입력 처리
  - 실시간 UI 업데이트
  - 결과 시각화
  - API 키 관리

#### ⚡ Streaming Layer  
- **streaming_workflow.py**: 실시간 워크플로우 관리
  - Generator 기반 단계별 스트리밍
  - 진행 상황 실시간 업데이트
  - 중간 결과 즉시 표시

#### 🧠 LangGraph Core
- **news_workflow.py**: StateGraph 정의
- **workflow_nodes.py**: 6개 노드 구현
- **WorkflowState**: TypedDict 기반 상태 관리

#### 📊 Data Collection
- **enhanced_news_fetcher.py**: 하이브리드 데이터 수집
- **네이버 API + RSS 피드**: 다중 소스 데이터 수집

#### 🔍 Analysis
- **OpenAI GPT**: LLM 기반 분석
- **LangChain**: LLM 연동 프레임워크

### 2.2 데이터 흐름
1. **사용자 키워드 입력** → Streamlit 인터페이스
2. **실시간 워크플로우 시작** → StreamingWorkflow
3. **LangGraph 실행** → NewsAnalysisWorkflow  
4. **6단계 순차 실행** → WorkflowNodes
5. **실시간 결과 반환** → Generator 스트리밍
6. **UI 업데이트** → Streamlit 실시간 표시

---

## 3. LangGraph 워크플로우

### 3.1 워크플로우 구조 (StateGraph)

```python
# news_workflow.py의 핵심 구조
workflow = StateGraph(WorkflowState)

# 노드 추가
workflow.add_node("decide_publishers", self.nodes.decide_publishers)
workflow.add_node("collect_articles", self.nodes.collect_articles)
workflow.add_node("analyze_articles", self.nodes.analyze_articles)
workflow.add_node("compare_analysis", self.nodes.compare_analysis)
workflow.add_node("generate_report", self.nodes.generate_report)
workflow.add_node("suggest_usage", self.nodes.suggest_usage)

# 엣지 정의 (선형 워크플로우)
workflow.set_entry_point("decide_publishers")
workflow.add_edge("decide_publishers", "collect_articles")
workflow.add_edge("collect_articles", "analyze_articles")
workflow.add_edge("analyze_articles", "compare_analysis")
workflow.add_edge("compare_analysis", "generate_report")
workflow.add_edge("generate_report", "suggest_usage")
workflow.add_edge("suggest_usage", END)
```

### 3.2 각 노드별 역할

#### 🎯 Node 1: decide_publishers
- **입력**: keyword
- **처리**: LLM을 사용하여 키워드에 최적화된 언론사 선택
- **출력**: selected_publishers (List[str])
- **LLM 프롬프트**: 키워드 분석 → 정치적 성향 다양성 고려 → 4-6개 언론사 선택

#### 📰 Node 2: collect_articles  
- **입력**: keyword + selected_publishers
- **처리**: 하이브리드 방식으로 기사 수집
  - 네이버 뉴스 API 호출
  - 언론사별 RSS 피드 수집
  - 중복 제거 및 필터링
- **출력**: raw_articles (Dict[str, List[Dict]])

#### 🔍 Node 3: analyze_articles
- **입력**: raw_articles
- **처리**: 각 기사별 LLM 분석
  - 요약 (3줄 이내)
  - 어조 분석 (객관적/비판적/옹호적/중립적)
  - 감정 분석 (긍정적/중립적/부정적)
  - 주요 논점 추출
  - 키워드 추출
- **출력**: analyzed_articles (Dict[str, List[Dict]])

#### 📊 Node 4: compare_analysis
- **입력**: analyzed_articles  
- **처리**: 언론사간 비교 분석
  - 감정 분포 비교
  - 프레이밍 차이점 분석
  - 어조 비교
  - 논점 차이 분석
- **출력**: comparison_analysis (Dict[str, Any])

#### 📄 Node 5: generate_report
- **입력**: 모든 이전 결과
- **처리**: 종합 분석 보고서 생성
  - 마크다운 형식 보고서
  - 감정 분포 요약
  - 프레이밍 차이점 정리
  - 종합 분석 결과
- **출력**: final_report (str)

#### 💡 Node 6: suggest_usage
- **입력**: final_report
- **처리**: 분석 결과 활용 방안 제안
  - 학술 연구 활용법
  - 미디어 리터러시 교육
  - 정책 결정 참고 자료
- **출력**: usage_suggestions (List[str])

---

## 4. 모듈별 상세 분석

### 4.1 workflow_nodes.py

#### 클래스 구조
```python
class WorkflowState(TypedDict):
    keyword: str
    selected_publishers: List[str]
    raw_articles: Dict[str, List[Dict[str, Any]]]
    analyzed_articles: Dict[str, List[Dict[str, Any]]]
    comparison_analysis: Dict[str, Any]
    final_report: str
    usage_suggestions: List[str]

class NewsWorkflowNodes:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        self.enhanced_news_api = EnhancedNewsAPI()
        self.all_publishers = ['조선일보', '동아일보', '중앙일보', 
                              '한겨레', '경향신문', 'SBS', 'MBC', 'KBS']
```

#### 핵심 메서드 분석

**decide_publishers 메서드**:
```python
def decide_publishers(self, state: WorkflowState) -> WorkflowState:
    # 1. 키워드 분석을 위한 프롬프트 구성
    # 2. LLM 호출하여 최적 언론사 선택
    # 3. JSON 파싱하여 언론사 목록 추출
    # 4. 상태 업데이트
```

**collect_articles 메서드**:
```python
def collect_articles(self, state: WorkflowState) -> WorkflowState:
    # 1. enhanced_news_api.collect_articles_hybrid() 호출
    # 2. 하이브리드 수집 (네이버 API + RSS)
    # 3. 언론사별 필터링 및 중복 제거
    # 4. 최대 3개 기사로 제한
    # 5. 상태 업데이트
```

### 4.2 enhanced_news_fetcher.py

#### 하이브리드 수집 전략
```python
class EnhancedNewsAPI:
    def __init__(self):
        # 언론사별 RSS 피드와 키워드 매핑
        self.media_sources = {
            '조선일보': {
                'rss': 'https://www.chosun.com/arc/outboundfeeds/rss/',
                'keywords': ['조선일보', 'chosun', '조선']
            },
            # ... 기타 언론사
        }
```

#### 수집 프로세스
1. **네이버 API 호출**: 기본 뉴스 데이터 수집
2. **RSS 피드 수집**: 언론사별 최신 기사 수집
3. **언론사별 필터링**: 키워드 매칭으로 분류
4. **중복 제거**: 제목 유사도 기반 중복 제거
5. **품질 검증**: 최소 길이 및 내용 검증

### 4.3 streaming_workflow.py

#### 실시간 스트리밍 구조
```python
class StreamingWorkflow:
    def run_streaming_analysis(self, keyword: str) -> Generator[Dict[str, Any], None, None]:
        # 상태 초기화
        state = {...}
        
        # 각 단계별 스트리밍
        for step in self.steps:
            # 단계 시작 알림
            yield {"type": "step_start", "step": step["name"], ...}
            
            # 실제 워크플로우 노드 실행
            if step["name"] == "decide_publishers":
                state = self.workflow.nodes.decide_publishers(state)
            
            # 단계 완료 알림 (결과 포함)
            yield {
                "type": "step_complete",
                "step": step["name"],
                "state": state,
                "step_data": self._get_step_data(step["name"], state)
            }
```

#### 스트리밍 데이터 형식
```python
{
    "type": "step_complete",
    "step": "collect_articles", 
    "message": "✅ 총 10개 기사 수집 완료",
    "progress": 35,
    "state": {...},
    "step_data": {
        "articles_by_publisher": {"조선일보": 3, "한겨레": 2},
        "total_articles": 10,
        "data_sources": {"naver_api": 6, "rss": 4}
    }
}
```

### 4.4 streamlit_app.py

#### 실시간 UI 업데이트
```python
def run_streaming_analysis(keyword, workflow_status, step_details):
    # 1. 진행 상황 컨테이너 생성
    main_progress = st.progress(0)
    status_container = st.container()
    results_container = st.container()
    
    # 2. 스트리밍 워크플로우 실행
    for update in streaming_workflow.run_streaming_analysis(keyword):
        # 3. 실시간 UI 업데이트
        main_progress.progress(update["progress"])
        status_text.markdown(f"### {update['message']}")
        
        # 4. 단계별 결과 즉시 표시
        if update["type"] == "step_complete":
            display_step_result(container, step_name, step_data, state)
```

---

## 5. 데이터 플로우

### 5.1 상태 변화 추적

#### 초기 상태
```python
initial_state = {
    "keyword": "사용자입력키워드",
    "selected_publishers": [],
    "raw_articles": {},
    "analyzed_articles": {},
    "comparison_analysis": {},
    "final_report": "",
    "usage_suggestions": []
}
```

#### 단계별 상태 변화

**Step 1 후 상태**:
```python
{
    "keyword": "대통령",
    "selected_publishers": ["조선일보", "동아일보", "한겨레", "경향신문"],
    "raw_articles": {},
    # ... 나머지는 동일
}
```

**Step 2 후 상태**:
```python
{
    "keyword": "대통령",
    "selected_publishers": ["조선일보", "동아일보", "한겨레", "경향신문"],
    "raw_articles": {
        "조선일보": [
            {
                "title": "대통령 발언 관련 기사",
                "description": "기사 내용...",
                "link": "https://...",
                "source": "naver_api"
            }
        ],
        "한겨레": [...]
    },
    # ... 나머지
}
```

### 5.2 데이터 변환 과정

#### 원시 기사 → 분석된 기사
```python
# 입력 (raw_articles)
{
    "title": "대통령, 새로운 정책 발표",
    "description": "대통령이 오늘 청와대에서..."
}

# LLM 분석 후 (analyzed_articles)  
{
    "title": "대통령, 새로운 정책 발표",
    "description": "대통령이 오늘 청와대에서...",
    "summary": "대통령이 새로운 경제정책을 발표했다. 주요 내용은...",
    "tone": "중립적",
    "sentiment": "긍정적", 
    "main_argument": "정부의 적극적인 경제정책 추진",
    "keywords": ["대통령", "정책", "경제", "발표"]
}
```

---

## 6. 상태 관리

### 6.1 TypedDict 기반 상태 정의

```python
from typing import TypedDict, List, Dict, Any

class WorkflowState(TypedDict):
    keyword: str                                    # 사용자 입력 키워드
    selected_publishers: List[str]                  # 선택된 언론사 목록
    raw_articles: Dict[str, List[Dict[str, Any]]]   # 언론사별 원시 기사
    analyzed_articles: Dict[str, List[Dict[str, Any]]]  # 언론사별 분석된 기사
    comparison_analysis: Dict[str, Any]             # 언론사간 비교 분석
    final_report: str                               # 최종 보고서
    usage_suggestions: List[str]                    # 활용 방안 제안
```

### 6.2 상태 불변성 관리

#### LangGraph의 상태 관리 원칙
- 각 노드는 새로운 상태 객체를 반환
- 이전 상태는 변경하지 않음 (불변성)
- 상태 업데이트는 딕셔너리 병합 방식

```python
def decide_publishers(self, state: WorkflowState) -> WorkflowState:
    # 기존 상태 복사
    new_state = state.copy()
    
    # 새로운 필드 업데이트
    new_state["selected_publishers"] = selected_publishers
    
    # 새로운 상태 반환
    return new_state
```

### 6.3 상태 검증

#### 상태 유효성 검사
```python
def validate_state(state: WorkflowState) -> bool:
    required_fields = ["keyword", "selected_publishers", "raw_articles"]
    return all(field in state for field in required_fields)
```

---

## 7. 실시간 스트리밍

### 7.1 Generator 기반 스트리밍

#### 스트리밍 워크플로우 구조
```python
def run_streaming_analysis(self, keyword: str) -> Generator[Dict[str, Any], None, None]:
    # 상태 초기화
    state = {...}
    
    # 각 단계별 스트리밍
    for step in self.steps:
        # 단계 시작 알림
        yield {"type": "step_start", "step": step["name"], ...}
        
        # 실제 워크플로우 노드 실행
        if step["name"] == "decide_publishers":
            state = self.workflow.nodes.decide_publishers(state)
        
        # 단계 완료 알림 (결과 포함)
        yield {
            "type": "step_complete",
            "step": step["name"],
            "state": state,
            "step_data": self._get_step_data(step["name"], state)
        }
```

### 7.2 실시간 UI 업데이트

#### Streamlit 실시간 컴포넌트
```python
# 진행률 바
main_progress = st.progress(0)

# 상태 텍스트
status_text = st.empty()

# 결과 컨테이너  
results_container = st.container()

# 스트리밍 처리
for update in streaming_workflow.run_streaming_analysis(keyword):
    # 진행률 업데이트
    main_progress.progress(update["progress"])
    
    # 상태 메시지 업데이트
    status_text.markdown(f"### {update['message']}")
    
    # 단계별 결과 즉시 표시
    if update["type"] == "step_complete":
        with results_container:
            display_step_result(update["step"], update["step_data"])
```

### 7.3 스트리밍 이벤트 타입

#### 이벤트 타입별 처리
```python
EVENT_TYPES = {
    "start": "분석 시작",
    "step_start": "단계 시작", 
    "step_running": "단계 실행 중",
    "step_complete": "단계 완료",
    "step_error": "단계 오류",
    "complete": "전체 완료"
}
```

---

## 8. API 연동

### 8.1 OpenAI API 연동

#### LangChain 기반 LLM 설정
```python
from langchain_openai import ChatOpenAI

class NewsWorkflowNodes:
    def __init__(self):
        # API 키 안전한 가져오기
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,      # 일관된 결과를 위한 낮은 temperature
            api_key=api_key
        )
```

#### 프롬프트 엔지니어링
```python
def analyze_article_prompt(title: str, description: str) -> str:
    return f"""
다음 뉴스 기사를 분석해주세요:

제목: {title}
내용: {description}

다음 형식으로 정확히 분석해주세요:

요약: [3줄 이내로 핵심 내용 요약]
어조: [객관적/비판적/옹호적/중립적 중 하나]
감정: [긍정적/중립적/부정적 중 하나]  
주요논점: [이 기사가 강조하는 핵심 주장이나 관점]
키워드: [기사의 핵심 키워드 3-5개를 쉼표로 구분]
"""
```

### 8.2 네이버 뉴스 API 연동

#### API 호출 구조
```python
def _get_naver_articles(self, keyword: str) -> List[Dict[str, Any]]:
    headers = {
        'X-Naver-Client-Id': self.naver_client_id,
        'X-Naver-Client-Secret': self.naver_client_secret
    }
    
    params = {
        'query': keyword,
        'display': 100,
        'start': 1,
        'sort': 'date'
    }
    
    response = requests.get(
        "https://openapi.naver.com/v1/search/news.json",
        headers=headers,
        params=params,
        timeout=10
    )
```

#### API 응답 처리
```python
def _filter_naver_articles(self, articles: List[Dict], publishers: List[str]) -> Dict[str, List[Dict]]:
    filtered = {pub: [] for pub in publishers}
    
    for article in articles:
        # HTML 태그 제거
        title = self._clean_html(article.get('title', ''))
        
        # 언론사별 키워드 매칭
        for publisher in publishers:
            keywords = self.media_sources[publisher]['keywords']
            if any(keyword.lower() in title.lower() for keyword in keywords):
                filtered[publisher].append({
                    'title': title,
                    'description': self._clean_html(article.get('description', '')),
                    'link': article.get('originallink', ''),
                    'source': 'naver_api'
                })
                break
    
    return filtered
```

### 8.3 RSS 피드 연동

#### RSS 파싱
```python
import feedparser

def _get_rss_articles(self, publisher: str, keyword: str) -> List[Dict[str, Any]]:
    rss_url = self.media_sources[publisher]['rss']
    
    response = requests.get(rss_url, timeout=10)
    feed = feedparser.parse(response.content)
    
    articles = []
    for entry in feed.entries[:10]:  # 최대 10개만
        if keyword.lower() in entry.title.lower() or keyword.lower() in entry.summary.lower():
            articles.append({
                'title': entry.title,
                'description': entry.summary,
                'link': entry.link,
                'pubDate': entry.published if hasattr(entry, 'published') else '',
                'source': 'rss'
            })
    
    return articles
```

---

## 9. 배포 가이드

### 9.1 Streamlit Cloud 배포

#### 1단계: 리포지토리 준비
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

#### 2단계: Streamlit Cloud 설정
1. https://share.streamlit.io 접속
2. New app 클릭
3. GitHub 리포지토리 연결
4. Main file path: `streamlit_app.py`
5. Deploy 클릭

#### 3단계: Secrets 설정
App Settings → Secrets에서:
```toml
NAVER_CLIENT_ID = "실제_클라이언트_ID"
NAVER_CLIENT_SECRET = "실제_시크릿"
OPENAI_API_KEY = "실제_OpenAI_키"
```

### 9.2 로컬 개발 환경

#### 환경 설정
```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Secrets 설정
mkdir .streamlit
echo '[default]
NAVER_CLIENT_ID = "your_id"
NAVER_CLIENT_SECRET = "your_secret"  
OPENAI_API_KEY = "your_key"' > .streamlit/secrets.toml

# 4. 실행
streamlit run streamlit_app.py
```

### 9.3 환경변수 기반 설정

#### 시스템 환경변수
```bash
export NAVER_CLIENT_ID="your_client_id"
export NAVER_CLIENT_SECRET="your_client_secret"
export OPENAI_API_KEY="your_openai_key"
```

#### 코드에서 환경 감지
```python
def get_api_keys():
    try:
        # Streamlit Cloud 환경
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            return (
                st.secrets.get("NAVER_CLIENT_ID", ""),
                st.secrets.get("NAVER_CLIENT_SECRET", ""), 
                st.secrets.get("OPENAI_API_KEY", "")
            )
        else:
            # 로컬 환경
            return (
                os.getenv("NAVER_CLIENT_ID", ""),
                os.getenv("NAVER_CLIENT_SECRET", ""),
                os.getenv("OPENAI_API_KEY", "")
            )
    except Exception:
        return "", "", ""
```

---

## 10. 테스트 방법

### 10.1 단위 테스트

#### 워크플로우 노드 테스트
```python
# test_workflow_nodes.py 생성 예시
import unittest
from workflow_nodes import NewsWorkflowNodes, WorkflowState

class TestWorkflowNodes(unittest.TestCase):
    def setUp(self):
        self.nodes = NewsWorkflowNodes()
        self.test_state = {
            "keyword": "테스트",
            "selected_publishers": [],
            "raw_articles": {},
            "analyzed_articles": {},
            "comparison_analysis": {},
            "final_report": "",
            "usage_suggestions": []
        }
    
    def test_decide_publishers(self):
        result = self.nodes.decide_publishers(self.test_state)
        self.assertIn("selected_publishers", result)
        self.assertIsInstance(result["selected_publishers"], list)
        
    def test_collect_articles(self):
        # 언론사가 선택된 상태로 테스트
        self.test_state["selected_publishers"] = ["조선일보", "한겨레"]
        result = self.nodes.collect_articles(self.test_state)
        self.assertIn("raw_articles", result)
```

#### 실행 방법
```bash
python -m pytest test_workflow_nodes.py -v
```

### 10.2 통합 테스트

#### 전체 워크플로우 테스트
```python
def test_full_workflow():
    from news_workflow import run_news_analysis
    
    # 간단한 키워드로 테스트
    result = run_news_analysis("경제")
    
    # 결과 검증
    assert "final_report" in result
    assert "usage_suggestions" in result
    assert len(result["selected_publishers"]) > 0
```

### 10.3 API 연동 테스트

#### Mock을 사용한 API 테스트
```python
from unittest.mock import patch, MagicMock

@patch('enhanced_news_fetcher.requests.get')
def test_naver_api(mock_get):
    # Mock 응답 설정
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'items': [{'title': '테스트 기사', 'description': '내용'}]
    }
    mock_get.return_value = mock_response
    
    # 테스트 실행
    api = EnhancedNewsAPI()
    articles = api._get_naver_articles("테스트")
    
    # 검증
    assert len(articles) > 0
```

---

## 11. 확장 방법

### 11.1 새로운 언론사 추가

#### enhanced_news_fetcher.py 수정
```python
# media_sources에 새로운 언론사 추가
self.media_sources['새로운언론사'] = {
    'rss': 'https://새로운언론사.com/rss.xml',
    'website': 'https://새로운언론사.com',
    'search_url': 'https://새로운언론사.com/search/{keyword}',
    'keywords': ['새로운언론사', 'new_media', '새로운']
}
```

#### workflow_nodes.py 수정
```python
# all_publishers 목록에 추가
self.all_publishers = ['조선일보', '동아일보', '중앙일보', 
                      '한겨레', '경향신문', 'SBS', 'MBC', 'KBS', '새로운언론사']
```

### 11.2 새로운 분석 기능 추가

#### 감정 분석 고도화
```python
def enhanced_sentiment_analysis(self, text: str) -> Dict[str, float]:
    """감정 점수를 0-1 사이 실수로 반환"""
    prompt = f"""
    다음 텍스트의 감정을 0-1 사이 점수로 분석해주세요:
    텍스트: {text}
    
    응답 형식:
    긍정적: 0.7
    중립적: 0.2  
    부정적: 0.1
    """
    # LLM 호출 및 파싱 로직
```

#### 새로운 워크플로우 노드 추가
```python
def sentiment_visualization(self, state: WorkflowState) -> WorkflowState:
    """감정 분석 시각화 데이터 생성"""
    analyzed_articles = state["analyzed_articles"]
    
    # 시각화용 데이터 생성
    viz_data = {}
    for publisher, articles in analyzed_articles.items():
        sentiments = [article['sentiment'] for article in articles]
        viz_data[publisher] = {
            'positive_count': sentiments.count('긍정적'),
            'neutral_count': sentiments.count('중립적'),
            'negative_count': sentiments.count('부정적')
        }
    
    state["visualization_data"] = viz_data
    return state
```

### 11.3 다른 LLM 모델 연동

#### Anthropic Claude 연동
```python
from langchain_anthropic import ChatAnthropic

class MultiLLMWorkflowNodes(NewsWorkflowNodes):
    def __init__(self):
        super().__init__()
        self.claude = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    def analyze_with_multiple_llms(self, text: str):
        # OpenAI 분석
        openai_result = self.llm.invoke([HumanMessage(content=text)])
        
        # Claude 분석
        claude_result = self.claude.invoke([HumanMessage(content=text)])
        
        # 결과 비교 및 통합
        return self.combine_llm_results(openai_result, claude_result)
```

### 11.4 실시간 알림 기능

#### Slack/Discord 연동
```python
import requests

def send_analysis_notification(keyword: str, results: Dict):
    """분석 완료시 Slack으로 알림 전송"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    message = {
        "text": f"🔍 '{keyword}' 키워드 분석 완료!",
        "attachments": [
            {
                "fields": [
                    {"title": "분석된 기사 수", "value": str(total_articles), "short": True},
                    {"title": "언론사 수", "value": str(len(results["selected_publishers"])), "short": True}
                ]
            }
        ]
    }
    
    requests.post(webhook_url, json=message)
```

---

## 12. 트러블슈팅

### 12.1 일반적인 문제

#### API 키 관련 오류
```
Error: OpenAI API key not found
```
**해결책**:
1. Streamlit Cloud Secrets 확인
2. 로컬 .streamlit/secrets.toml 확인
3. 환경변수 설정 확인

#### 네이버 API 할당량 초과
```
Error: Quota exceeded for Naver API
```
**해결책**:
1. API 사용량 확인 (developers.naver.com)
2. RSS 피드만 사용하는 모드로 전환
3. API 키 업그레이드

#### LangGraph 상태 관리 오류
```
Error: StateGraph validation failed
```
**해결책**:
1. WorkflowState TypedDict 확인
2. 노드 반환값 타입 검증
3. 상태 필드명 일치 여부 확인

### 12.2 성능 최적화

#### LLM 호출 최적화
```python
# 배치 처리로 API 호출 횟수 줄이기
def analyze_articles_batch(self, articles: List[Dict]) -> List[Dict]:
    batch_prompt = "\n\n---\n\n".join([
        f"기사 {i+1}:\n제목: {article['title']}\n내용: {article['description']}"
        for i, article in enumerate(articles)
    ])
    
    # 한 번의 API 호출로 여러 기사 분석
    response = self.llm.invoke([HumanMessage(content=batch_prompt)])
    
    # 응답 파싱하여 개별 기사 결과로 분리
    return self.parse_batch_response(response.content, len(articles))
```

#### 캐싱 구현
```python
import streamlit as st

@st.cache_data(ttl=3600)  # 1시간 캐시
def cached_article_analysis(title: str, description: str) -> Dict:
    """분석 결과 캐싱으로 중복 API 호출 방지"""
    return analyze_article(title, description)
```

### 12.3 에러 핸들링

#### 견고한 에러 처리
```python
def robust_llm_call(self, prompt: str, max_retries: int = 3) -> str:
    """재시도 로직이 있는 안전한 LLM 호출"""
    for attempt in range(max_retries):
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            if attempt == max_retries - 1:
                return f"분석 실패: {str(e)}"
            time.sleep(2 ** attempt)  # 지수 백오프
    
    return "분석 실패: 최대 재시도 횟수 초과"
```

#### 부분 실패 처리
```python
def partial_failure_handling(self, state: WorkflowState) -> WorkflowState:
    """일부 언론사에서 수집 실패시에도 계속 진행"""
    successful_publishers = []
    failed_publishers = []
    
    for publisher in state["selected_publishers"]:
        try:
            articles = self.collect_from_publisher(publisher, state["keyword"])
            if articles:
                state["raw_articles"][publisher] = articles
                successful_publishers.append(publisher)
            else:
                failed_publishers.append(publisher)
        except Exception as e:
            failed_publishers.append(publisher)
            print(f"❌ {publisher} 수집 실패: {e}")
    
    # 실패한 언론사는 제외하고 계속 진행
    state["selected_publishers"] = successful_publishers
    
    if failed_publishers:
        print(f"⚠️ 수집 실패한 언론사: {', '.join(failed_publishers)}")
    
    return state
```

### 12.4 모니터링 및 로깅

#### 상세 로깅
```python
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_workflow_progress(self, step_name: str, state: WorkflowState):
    """워크플로우 진행 상황 로깅"""
    logger.info(f"Step {step_name} started for keyword: {state['keyword']}")
    logger.info(f"Current publishers: {state['selected_publishers']}")
    logger.info(f"Articles collected: {sum(len(articles) for articles in state['raw_articles'].values())}")
```

---

## 📞 개발 지원

### 문의 및 기여
- **Issues**: GitHub Issues에서 버그 리포트 및 기능 요청
- **Pull Requests**: 코드 기여는 PR로 제출
- **Documentation**: 추가 문서는 docs/ 폴더에 작성

### 라이센스
이 프로젝트는 MIT 라이센스를 따릅니다.

---

*이 매뉴얼은 프로젝트의 지속적인 발전과 함께 업데이트됩니다.* 