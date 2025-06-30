# 실시간 한국 언론사 미디어 프레이밍 분석기

**LangGraph 기반 실시간 추적 & 단계별 피드백 시스템**

네이버 뉴스 API와 OpenAI GPT를 활용하여 한국 주요 언론사들의 보도 프레이밍 차이를 실시간으로 분석하는 Streamlit 웹 애플리케이션입니다.

## ⚡ 주요 기능

- **실시간 단계별 추적**: 6단계 워크플로우 실시간 모니터링
- **지능형 언론사 선택**: AI가 키워드에 최적화된 언론사 자동 선택
- **하이브리드 기사 수집**: 네이버 API + RSS 피드 결합 수집
- **심층 AI 분석**: OpenAI GPT 기반 요약, 감정, 프레이밍 분석
- **실시간 비교 분석**: 언론사별 입장 차이 즉시 비교
- **종합 보고서 생성**: 마크다운 형식의 상세 분석 보고서

## 🎯 실시간 워크플로우

1. **🎯 언론사 선택** - AI가 키워드 분석하여 최적 언론사 선택
2. **📰 기사 수집** - 하이브리드 방식으로 관련 기사 수집  
3. **🔍 기사 분석** - 각 기사의 요약, 어조, 감정 분석
4. **📊 비교 분석** - 언론사간 입장 차이 비교
5. **📄 보고서 생성** - 종합 분석 보고서 작성
6. **💡 활용 방안 제안** - 분석 결과 활용법 제안

## 📋 분석 대상 언론사

- **신문**: 조선일보, 동아일보, 중앙일보, 한겨레, 경향신문
- **방송**: SBS, MBC, KBS

## 🚀 Streamlit Cloud 배포

### 1. 리포지토리 준비
```bash
git clone <this-repository>
cd test_v01
```

### 2. Streamlit Cloud에서 배포
1. **https://share.streamlit.io** 접속
2. **New app** 클릭
3. **GitHub 리포지토리 연결**
4. **Main file path**: `streamlit_app.py`
5. **Deploy!** 클릭

### 3. API 키 설정 (중요!)
배포 후 Streamlit Cloud 대시보드에서:

1. **앱 선택 → Settings → Secrets**
2. **다음 내용 입력:**
```toml
NAVER_CLIENT_ID = "your_naver_client_id"
NAVER_CLIENT_SECRET = "your_naver_client_secret"
OPENAI_API_KEY = "your_openai_api_key"
```
3. **Save** → 앱 자동 재시작

## 🛠️ 로컬 개발 설정

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 로컬 Secrets 설정
프로젝트 루트에 `.streamlit` 폴더를 생성하고 `secrets.toml` 파일을 만드세요:

```toml
# .streamlit/secrets.toml (로컬 개발용)
[default]
NAVER_CLIENT_ID = "your_naver_client_id"
NAVER_CLIENT_SECRET = "your_naver_client_secret"
OPENAI_API_KEY = "your_openai_api_key"
```

### 3. 로컬 실행
```bash
streamlit run streamlit_app.py
```

## 📚 API 키 발급 방법

### 🔍 네이버 검색 API
1. [네이버 개발자 센터](https://developers.naver.com/apps/#/register) 접속
2. **애플리케이션 등록** 클릭
3. **검색 API** 선택 후 등록
4. **Client ID**와 **Client Secret** 확인

### 🤖 OpenAI API  
1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. **Create new secret key** 클릭
3. API 키 복사 (다시 볼 수 없으니 안전하게 보관)
4. 사용량에 따라 요금 부과 (약 $0.002/1K tokens)

## 📁 프로젝트 구조

```
test_v01/
├── streamlit_app.py           # 메인 Streamlit 애플리케이션
├── streaming_workflow.py      # 실시간 스트리밍 워크플로우
├── news_workflow.py           # LangGraph 기반 뉴스 분석 워크플로우
├── workflow_nodes.py          # 워크플로우 노드들 정의
├── enhanced_news_fetcher.py   # 하이브리드 뉴스 수집기
├── news_fetcher.py           # 네이버 뉴스 API 연동
├── news_analyzer.py          # OpenAI 기반 분석 모듈
├── report_generator.py       # 보고서 생성 모듈
├── requirements.txt          # 패키지 의존성
├── config_example.py         # API 설정 예시
└── README.md                # 프로젝트 문서
```

## 💡 사용 방법

1. 웹 브라우저에서 Streamlit 앱에 접속
2. 분석하고 싶은 키워드 입력 (예: "대통령", "경제정책", "교육개혁")
3. "⚡ 실시간 분석 시작" 버튼 클릭
4. **실시간 진행 상황 모니터링**:
   - 진행률 바로 단계별 진행 상황 확인
   - 각 단계 완료시 즉시 중간 결과 표시
   - 사이드바에서 상세 정보 실시간 업데이트
5. 최종 결과를 3개 탭에서 확인:
   - **📰 상세 기사**: 언론사별 기사 상세 분석
   - **📄 최종 보고서**: 마크다운 형식 종합 보고서  
   - **💡 활용 방안**: AI 제안 활용법

## 🔍 분석 내용

각 기사에 대해 다음과 같은 분석을 수행합니다:

- **요약**: 3줄 이내 핵심 내용 요약
- **어조 분석**: 기사의 전반적 논조
- **감정 분석**: 긍정적/중립적/부정적 감정 분류
- **주요 논점**: 기사가 강조하는 핵심 주장
- **키워드 추출**: 주요 키워드 자동 추출

## 📊 출력 결과

- 실시간 단계별 진행 상황
- 언론사별 감정 분포 통계
- 기사별 상세 분석 결과
- 언론사간 프레이밍 차이점 비교
- 다운로드 가능한 마크다운 보고서
- JSON 형식 전체 분석 데이터

## ⚠️ 제한사항

- API 호출 제한으로 각 언론사당 최대 3개 기사까지 분석
- 네이버 뉴스 API와 RSS 피드의 검색 결과에 의존
- OpenAI API 사용료 발생 가능

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Workflow**: LangGraph, LangChain
- **APIs**: Naver News API, OpenAI GPT API
- **Data Processing**: Pandas, feedparser
- **Language**: Python 3.8+

## 🔒 보안 설정

- **Streamlit Cloud**: 웹 인터페이스에서 안전한 secrets 관리
- **로컬 개발**: `.streamlit/secrets.toml` 사용
- **Git 보안**: API 키는 절대 리포지토리에 커밋하지 않음
- **자동 보호**: `.gitignore`로 민감한 파일 자동 제외

## 🌐 라이브 데모

**Streamlit Cloud**: [여기에 배포된 앱 URL 입력]

배포 후 위 링크에서 바로 체험해보세요!