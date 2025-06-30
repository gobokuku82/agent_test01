# 📘 한국 언론사 미디어 프레이밍 분석기 - 개발 가이드

> **LangGraph + MCP 기반 업무자동화 시스템**  
> 실시간 단계별 추적 & 피드백 제공

## 🎯 프로젝트 개요

### 핵심 기능
- 키워드 기반 한국 언론사 기사 자동 수집
- OpenAI GPT 기반 실시간 분석 (요약, 감정, 프레이밍)  
- 언론사간 보도 관점 차이 비교
- LangGraph 워크플로우로 6단계 자동화
- 실시간 진행 상황 추적 및 중간 결과 표시

### 분석 대상 언론사
- **보수**: 조선일보, 동아일보, 중앙일보
- **진보**: 한겨레, 경향신문  
- **방송**: SBS, MBC, KBS

## 🏗️ 시스템 아키텍처

### 레이어 구조
```
📱 Frontend (Streamlit)
    ↓
⚡ Streaming Layer (실시간 추적)
    ↓  
🧠 LangGraph Core (6단계 워크플로우)
    ↓
📊 Data Collection (하이브리드 수집)
    ↓
🌐 External APIs (네이버, OpenAI, RSS)
```

### 핵심 파일 구조
```
streamlit_app.py          # 웹 인터페이스 + 실시간 UI
streaming_workflow.py     # Generator 기반 스트리밍  
news_workflow.py          # LangGraph StateGraph 정의
workflow_nodes.py         # 6개 노드 구현
enhanced_news_fetcher.py  # 하이브리드 데이터 수집
```

## 🔄 LangGraph 워크플로우

### 6단계 자동화 파이프라인

1. **🎯 decide_publishers**: AI가 키워드 분석하여 최적 언론사 선택
2. **📰 collect_articles**: 네이버 API + RSS 하이브리드 수집
3. **🔍 analyze_articles**: 각 기사별 요약, 감정, 어조, 논점 분석  
4. **📊 compare_analysis**: 언론사간 입장 차이 비교
5. **📄 generate_report**: 마크다운 종합 보고서 생성
6. **💡 suggest_usage**: 분석 결과 활용 방안 제안

### StateGraph 정의 코드
```python
# news_workflow.py
workflow = StateGraph(WorkflowState)

# 6개 노드 추가
workflow.add_node("decide_publishers", self.nodes.decide_publishers)
workflow.add_node("collect_articles", self.nodes.collect_articles)
workflow.add_node("analyze_articles", self.nodes.analyze_articles)
workflow.add_node("compare_analysis", self.nodes.compare_analysis)
workflow.add_node("generate_report", self.nodes.generate_report)
workflow.add_node("suggest_usage", self.nodes.suggest_usage)

# 선형 엣지 연결
workflow.set_entry_point("decide_publishers")
workflow.add_edge("decide_publishers", "collect_articles")
workflow.add_edge("collect_articles", "analyze_articles")
workflow.add_edge("analyze_articles", "compare_analysis")
workflow.add_edge("compare_analysis", "generate_report")
workflow.add_edge("generate_report", "suggest_usage")
workflow.add_edge("suggest_usage", END)
```

## 📊 상태 관리 (WorkflowState)

### TypedDict 기반 상태 정의
```python
class WorkflowState(TypedDict):
    keyword: str                                    # 사용자 입력 키워드
    selected_publishers: List[str]                  # 선택된 언론사
    raw_articles: Dict[str, List[Dict[str, Any]]]   # 수집된 원시 기사
    analyzed_articles: Dict[str, List[Dict[str, Any]]]  # 분석된 기사
    comparison_analysis: Dict[str, Any]             # 비교 분석 결과
    final_report: str                               # 최종 보고서
    usage_suggestions: List[str]                    # 활용 방안
```

### 상태 변화 예시
```python
# 초기 상태
{"keyword": "대통령", "selected_publishers": [], ...}

# Step 1 후
{"keyword": "대통령", "selected_publishers": ["조선일보", "한겨레"], ...}

# Step 2 후  
{"keyword": "대통령", "selected_publishers": [...], 
 "raw_articles": {"조선일보": [{"title": "...", "description": "..."}], ...}}
```

## ⚡ 실시간 스트리밍 시스템

### Generator 기반 스트리밍 구조
```python
# streaming_workflow.py
def run_streaming_analysis(self, keyword: str) -> Generator[Dict[str, Any], None, None]:
    state = {...}  # 초기 상태
    
    # 각 단계별 스트리밍
    for step in self.steps:
        # 단계 시작 알림
        yield {"type": "step_start", "step": step["name"], "progress": step["progress"]-5}
        
        # 실제 워크플로우 노드 실행  
        state = self.workflow.nodes.method_name(state)
        
        # 단계 완료 알림 (결과 포함)
        yield {
            "type": "step_complete", 
            "step": step["name"],
            "state": state,
            "step_data": self._get_step_data(step["name"], state)
        }
```

### 실시간 UI 업데이트 (Streamlit)
```python
# streamlit_app.py
def run_streaming_analysis(keyword, workflow_status, step_details):
    main_progress = st.progress(0)
    status_container = st.container()
    
    # 스트리밍 실행
    for update in streaming_workflow.run_streaming_analysis(keyword):
        # 진행률 업데이트
        main_progress.progress(update["progress"])
        
        # 상태 메시지 업데이트
        status_text.markdown(f"### {update['message']}")
        
        # 단계별 결과 즉시 표시
        if update["type"] == "step_complete":
            display_step_result(update["step"], update["step_data"])
```

## 📊 하이브리드 데이터 수집

### 다중 소스 수집 전략
```python
# enhanced_news_fetcher.py
class EnhancedNewsAPI:
    def collect_articles_hybrid(self, keyword: str, publishers: List[str]):
        all_articles = {}
        
        # 1. 네이버 API 기본 수집
        naver_articles = self._get_naver_articles(keyword)
        naver_filtered = self._filter_naver_articles(naver_articles, publishers)
        
        # 2. 언론사별 RSS 피드 수집
        for publisher in publishers:
            articles = []
            
            # 네이버 결과 추가
            if publisher in naver_filtered:
                articles.extend(naver_filtered[publisher])
            
            # RSS 피드에서 추가 수집  
            rss_articles = self._get_rss_articles(publisher, keyword)
            articles.extend(rss_articles)
            
            # 중복 제거 후 최대 3개 선택
            all_articles[publisher] = self._remove_duplicates(articles)[:3]
        
        return all_articles
```

### 언론사별 RSS 매핑
```python
self.media_sources = {
    '조선일보': {
        'rss': 'https://www.chosun.com/arc/outboundfeeds/rss/',
        'keywords': ['조선일보', 'chosun', '조선']
    },
    '한겨레': {
        'rss': 'http://feeds.hani.co.kr/rss/newsstand/',
        'keywords': ['한겨레', 'hani']
    },
    # ... 기타 언론사
}
```

## 🔌 API 연동 구조

### OpenAI GPT 연동 (LangChain)
```python
# workflow_nodes.py
class NewsWorkflowNodes:
    def __init__(self):
        # 안전한 API 키 가져오기
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,  # 일관된 결과
            api_key=api_key
        )
    
    def analyze_article(self, title: str, description: str):
        prompt = f"""
        다음 뉴스 기사를 분석해주세요:
        제목: {title}
        내용: {description}
        
        형식:
        요약: [3줄 이내 요약]
        어조: [객관적/비판적/옹호적/중립적]
        감정: [긍정적/중립적/부정적]
        주요논점: [핵심 주장]
        키워드: [핵심 키워드 3-5개]
        """
        
        response = self.llm.invoke([
            SystemMessage(content="뉴스 분석 전문가"),
            HumanMessage(content=prompt)
        ])
        
        return self._parse_analysis(response.content)
```

### 네이버 뉴스 API 연동
```python
def _get_naver_articles(self, keyword: str) -> List[Dict]:
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
    
    return response.json().get('items', [])
```

## 🚀 배포 가이드

### Streamlit Cloud 배포 (권장)

#### 1단계: 리포지토리 준비
```bash
git add .
git commit -m "프로젝트 완성"
git push origin main
```

#### 2단계: Streamlit Cloud 설정
1. **https://share.streamlit.io** 접속
2. **New app** 클릭
3. **GitHub 리포지토리 연결**
4. **Main file path**: `streamlit_app.py`
5. **Deploy** 클릭

#### 3단계: Secrets 설정 (중요!)
App Settings → Secrets에서:
```toml
NAVER_CLIENT_ID = "실제_네이버_클라이언트_ID"
NAVER_CLIENT_SECRET = "실제_네이버_시크릿"
OPENAI_API_KEY = "실제_OpenAI_API_키"
```

### 로컬 개발 환경
```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Secrets 설정
mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
[default]
NAVER_CLIENT_ID = "your_naver_id"
NAVER_CLIENT_SECRET = "your_naver_secret"
OPENAI_API_KEY = "your_openai_key"
EOF

# 4. 실행
streamlit run streamlit_app.py
```

## 🧪 테스트 방법

### 기본 테스트 폴더 생성
```bash
mkdir tests
cd tests
```

### 단위 테스트 생성
```python
# tests/test_workflow_nodes.py
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
        self.assertTrue(len(result["selected_publishers"]) > 0)
    
    def test_collect_articles(self):
        self.test_state["selected_publishers"] = ["조선일보", "한겨레"]
        result = self.nodes.collect_articles(self.test_state)
        self.assertIn("raw_articles", result)
        self.assertIsInstance(result["raw_articles"], dict)

# 실행: python -m pytest tests/test_workflow_nodes.py -v
```

### 통합 테스트
```python
# tests/test_integration.py
def test_full_workflow():
    from news_workflow import run_news_analysis
    
    result = run_news_analysis("경제")
    
    # 결과 검증
    assert "final_report" in result
    assert "usage_suggestions" in result
    assert len(result["selected_publishers"]) > 0
    print("✅ 전체 워크플로우 테스트 통과")

# 실행: python tests/test_integration.py
```

## 🔧 확장 방법

### 새로운 언론사 추가

#### enhanced_news_fetcher.py 수정
```python
# media_sources에 새 언론사 추가
self.media_sources['새로운언론사'] = {
    'rss': 'https://새로운언론사.com/rss.xml',
    'website': 'https://새로운언론사.com',
    'keywords': ['새로운언론사', 'newmedia', '새로운']
}
```

#### workflow_nodes.py 수정
```python
# all_publishers 목록에 추가
self.all_publishers = [
    '조선일보', '동아일보', '중앙일보', 
    '한겨레', '경향신문', 'SBS', 'MBC', 'KBS', 
    '새로운언론사'  # 추가
]
```

### 새로운 분석 기능 추가

#### 감정 분석 고도화
```python
def enhanced_sentiment_analysis(self, text: str) -> Dict[str, float]:
    """감정을 0-1 사이 점수로 반환"""
    prompt = f"""
    텍스트의 감정을 0-1 점수로 분석:
    {text}
    
    형식:
    긍정적: 0.7
    중립적: 0.2
    부정적: 0.1
    """
    # LLM 호출 및 파싱
```

#### 새로운 워크플로우 노드 추가
```python
def keyword_trend_analysis(self, state: WorkflowState) -> WorkflowState:
    """키워드 트렌드 분석 노드"""
    keyword = state["keyword"]
    
    # 트렌드 분석 로직
    trend_data = self.analyze_keyword_trends(keyword)
    
    state["trend_analysis"] = trend_data
    return state

# StateGraph에 노드 추가
workflow.add_node("keyword_trend", self.nodes.keyword_trend_analysis)
workflow.add_edge("suggest_usage", "keyword_trend")
workflow.add_edge("keyword_trend", END)
```

### 다른 LLM 모델 연동
```python
from langchain_anthropic import ChatAnthropic

class MultiLLMNodes(NewsWorkflowNodes):
    def __init__(self):
        super().__init__()
        self.claude = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    def compare_llm_analysis(self, text: str):
        # OpenAI와 Claude 결과 비교
        openai_result = self.llm.invoke([HumanMessage(content=text)])
        claude_result = self.claude.invoke([HumanMessage(content=text)])
        
        return {
            "openai": openai_result.content,
            "claude": claude_result.content,
            "comparison": self.compare_results(openai_result, claude_result)
        }
```

## 🛠️ 트러블슈팅

### 일반적인 문제

#### API 키 오류
```
Error: OpenAI API key not found
```
**해결책**:
1. Streamlit Cloud Secrets 확인
2. 로컬 .streamlit/secrets.toml 확인  
3. 환경변수 `export OPENAI_API_KEY="키"` 설정

#### 네이버 API 할당량 초과
```
Error: Quota exceeded
```
**해결책**:
1. [네이버 개발자센터](https://developers.naver.com) API 사용량 확인
2. RSS 전용 모드로 전환
3. API 키 업그레이드

#### LangGraph 상태 오류
```
Error: StateGraph validation failed
```
**해결책**:
1. WorkflowState TypedDict 필드 확인
2. 노드 반환값 타입 검증
3. 상태 필드명 일치 여부 확인

### 성능 최적화

#### LLM 호출 최적화
```python
@st.cache_data(ttl=3600)  # 1시간 캐시
def cached_analysis(title: str, description: str):
    """중복 분석 방지 캐싱"""
    return analyze_article(title, description)
```

#### 배치 처리
```python
def analyze_articles_batch(self, articles: List[Dict]) -> List[Dict]:
    """여러 기사를 한번에 분석"""
    batch_prompt = "\n---\n".join([
        f"기사 {i+1}: {article['title']}\n{article['description']}"
        for i, article in enumerate(articles)
    ])
    
    response = self.llm.invoke([HumanMessage(content=batch_prompt)])
    return self.parse_batch_response(response.content)
```

### 에러 핸들링
```python
def robust_workflow_execution(self, state: WorkflowState) -> WorkflowState:
    """견고한 워크플로우 실행"""
    try:
        return self.execute_step(state)
    except Exception as e:
        # 부분 실패 처리
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Step failed: {str(e)}")
        
        # 기본값으로 계속 진행
        return self.set_default_values(state)
```

## 📞 개발 지원

### 문의 및 기여
- **Issues**: GitHub Issues에서 버그 리포트
- **Pull Requests**: 코드 기여는 PR로 제출
- **Documentation**: docs/ 폴더에 추가 문서 작성

### 라이센스
MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🎉 축하합니다! 이제 전체 시스템을 이해하고 확장할 수 있습니다.**

*이 가이드는 프로젝트 발전과 함께 지속적으로 업데이트됩니다.* 