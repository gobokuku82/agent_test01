from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import requests
import streamlit as st
import os
import json
from enhanced_news_fetcher import EnhancedNewsAPI

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
        # 안전한 API 키 가져오기
        try:
            # Streamlit Cloud 환경
            if hasattr(st, 'secrets') and len(st.secrets) > 0:
                api_key = st.secrets.get("OPENAI_API_KEY", "")
            else:
                # 로컬 환경 (환경변수)
                api_key = os.getenv("OPENAI_API_KEY", "")
                
            if api_key:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    api_key=api_key
                )
            else:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
                
        except Exception as e:
            print(f"LLM 초기화 실패: {e}")
            self.llm = None
            
        self.enhanced_news_api = EnhancedNewsAPI()
        self.all_publishers = ['조선일보', '동아일보', '중앙일보', '한겨레', '경향신문', 'SBS', 'MBC', 'KBS']

    def decide_publishers(self, state: WorkflowState) -> WorkflowState:
        """
        1단계: 키워드를 분석하여 관련 언론사를 결정
        """
        keyword = state["keyword"]
        
        if not self.llm:
            # LLM이 없으면 기본 언론사 선택
            selected_publishers = ['조선일보', '동아일보', '한겨레', '경향신문']
            print(f"기본 언론사 선택: {selected_publishers}")
            state["selected_publishers"] = selected_publishers
            return state
        
        # LLM을 사용하여 키워드에 적합한 언론사 선택
        prompt = f"""
        다음 키워드와 관련된 뉴스를 분석하기 위해 가장 적합한 한국 언론사들을 선택해주세요.

        키워드: "{keyword}"

        선택 가능한 언론사: {', '.join(self.all_publishers)}

        다음 기준을 고려하여 4-6개 언론사를 선택해주세요:
        1. 해당 주제에 대한 보도 빈도
        2. 정치적 성향의 다양성 (보수, 진보, 중도)
        3. 매체 유형의 다양성 (신문, 방송)

        응답 형식: ["언론사1", "언론사2", "언론사3", ...]
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="당신은 한국 언론 분석 전문가입니다."),
                HumanMessage(content=prompt)
            ])
            
            # LLM 응답에서 언론사 목록 추출
            content = response.content
            # JSON 형태로 파싱 시도
            try:
                if '[' in content and ']' in content:
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    publishers_str = content[start:end]
                    selected_publishers = json.loads(publishers_str)
                else:
                    # fallback: 기본 언론사 선택
                    selected_publishers = ['조선일보', '동아일보', '한겨레', '경향신문']
            except:
                selected_publishers = ['조선일보', '동아일보', '한겨레', '경향신문']
                
        except Exception as e:
            print(f"언론사 선택 중 오류: {e}")
            # 기본값 사용
            selected_publishers = ['조선일보', '동아일보', '한겨레', '경향신문']
        
        print(f"선택된 언론사: {selected_publishers}")
        state["selected_publishers"] = selected_publishers
        return state

    def collect_articles(self, state: WorkflowState) -> WorkflowState:
        """
        2단계: 개선된 하이브리드 방식으로 기사 수집
        """
        keyword = state["keyword"]
        publishers = state["selected_publishers"]
        
        print(f"🚀 하이브리드 기사 수집 시작: {keyword}")
        
        try:
            # 개선된 하이브리드 수집 방식 사용
            raw_articles = self.enhanced_news_api.collect_articles_hybrid(keyword, publishers)
            
            # 수집 결과 출력
            total_collected = sum(len(articles) for articles in raw_articles.values())
            print(f"📊 총 {total_collected}개 기사 수집 완료")
            
            for publisher, articles in raw_articles.items():
                sources = {}
                for article in articles:
                    source = article.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
                
                source_info = ", ".join([f"{k}:{v}" for k, v in sources.items()])
                print(f"  {publisher}: {len(articles)}개 ({source_info})")
            
            # 만약 수집된 기사가 너무 적다면 샘플 기사로 보완
            if total_collected < 5:
                print("🔄 수집된 기사가 부족하여 최신 샘플 기사로 보완합니다...")
                sample_articles = self.enhanced_news_api.get_sample_articles(publishers)
                
                for publisher in publishers:
                    if len(raw_articles.get(publisher, [])) == 0 and sample_articles.get(publisher):
                        raw_articles[publisher] = sample_articles[publisher][:2]  # 최대 2개
                        print(f"  {publisher}: 샘플 기사 {len(raw_articles[publisher])}개 추가")
            
        except Exception as e:
            print(f"기사 수집 중 오류: {e}")
            # 빈 결과로 초기화
            raw_articles = {pub: [] for pub in publishers}
        
        state["raw_articles"] = raw_articles
        return state

    def analyze_articles(self, state: WorkflowState) -> WorkflowState:
        """
        3-4단계: 기사 요약 및 어조/감정/논점 분석
        """
        raw_articles = state["raw_articles"]
        analyzed_articles = {}
        
        for publisher, articles in raw_articles.items():
            print(f"{publisher} 기사 분석 중...")
            analyzed_articles[publisher] = []
            
            for article in articles:
                analysis_prompt = f"""
다음 뉴스 기사를 분석해주세요:

제목: {article['title']}
내용: {article['description']}
출처: {article.get('source', 'unknown')}

다음 형식으로 정확히 분석해주세요:

요약: [3줄 이내로 핵심 내용 요약]
어조: [객관적/비판적/옹호적/중립적 중 하나]
감정: [긍정적/중립적/부정적 중 하나]
주요논점: [이 기사가 강조하는 핵심 주장이나 관점]
키워드: [기사의 핵심 키워드 3-5개를 쉼표로 구분]
"""
                
                try:
                    response = self.llm.invoke([
                        SystemMessage(content="당신은 뉴스 분석 전문가입니다. 정확하고 객관적으로 분석해주세요."),
                        HumanMessage(content=analysis_prompt)
                    ])
                    
                    analysis = self._parse_article_analysis(response.content)
                    
                    analyzed_article = article.copy()
                    analyzed_article.update(analysis)
                    analyzed_articles[publisher].append(analyzed_article)
                    
                except Exception as e:
                    print(f"기사 분석 오류: {e}")
                    # 기본값으로 저장
                    analyzed_article = article.copy()
                    analyzed_article.update({
                        'summary': '분석 불가',
                        'tone': '중립적',
                        'sentiment': '중립적',
                        'main_argument': '분석 불가',
                        'keywords': []
                    })
                    analyzed_articles[publisher].append(analyzed_article)
        
        state["analyzed_articles"] = analyzed_articles
        return state

    def compare_analysis(self, state: WorkflowState) -> WorkflowState:
        """
        5단계: 언론사별 입장 차이 및 강조점 비교 분석
        """
        analyzed_articles = state["analyzed_articles"]
        keyword = state["keyword"]
        
        # 언론사별 요약 정보 생성
        publisher_summaries = {}
        for publisher, articles in analyzed_articles.items():
            if articles:
                summaries = [art.get('summary', '') for art in articles]
                tones = [art.get('tone', '') for art in articles]
                sentiments = [art.get('sentiment', '') for art in articles]
                arguments = [art.get('main_argument', '') for art in articles]
                
                publisher_summaries[publisher] = {
                    'article_count': len(articles),
                    'summaries': summaries,
                    'dominant_tone': max(set(tones), key=tones.count) if tones else '중립적',
                    'dominant_sentiment': max(set(sentiments), key=sentiments.count) if sentiments else '중립적',
                    'main_arguments': arguments
                }
        
        # LLM을 사용한 비교 분석
        comparison_prompt = f"""
키워드 "{keyword}"에 대한 언론사별 보도 분석 결과를 비교 분석해주세요.

{json.dumps(publisher_summaries, ensure_ascii=False, indent=2)}

다음 관점에서 비교 분석해주세요:
1. 전체적인 보도 톤의 차이
2. 강조하는 논점의 차이
3. 감정적 접근의 차이
4. 각 언론사의 특징적 관점

응답 형식:
보도톤_차이: [언론사별 보도 톤 비교]
논점_차이: [언론사별 주요 논점 차이]
감정_차이: [언론사별 감정적 접근 차이]
특징적_관점: [각 언론사의 독특한 시각]
종합_분석: [전체적인 언론사 간 차이점 종합]
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="당신은 미디어 프레이밍 분석 전문가입니다."),
                HumanMessage(content=comparison_prompt)
            ])
            
            comparison_analysis = self._parse_comparison_analysis(response.content)
            
        except Exception as e:
            print(f"비교 분석 오류: {e}")
            comparison_analysis = {
                'tone_differences': '분석 불가',
                'argument_differences': '분석 불가',
                'emotional_differences': '분석 불가',
                'unique_perspectives': '분석 불가',
                'overall_analysis': '분석 불가'
            }
        
        state["comparison_analysis"] = comparison_analysis
        return state

    def generate_report(self, state: WorkflowState) -> WorkflowState:
        """
        6단계: 비교 분석 결과를 표/보고서 형태로 정리
        """
        keyword = state["keyword"]
        analyzed_articles = state["analyzed_articles"]
        comparison_analysis = state["comparison_analysis"]
        
        # 보고서 생성
        report = f"""# "{keyword}" 언론사 보도 비교 분석 보고서 (하이브리드 수집)

## 📊 분석 개요
- 분석 키워드: {keyword}
- 분석 언론사: {', '.join(state['selected_publishers'])}
- 분석 기사 수: {sum(len(articles) for articles in analyzed_articles.values())}개
- 데이터 소스: 네이버 API + RSS 피드

## 📰 언론사별 보도 현황

"""
        
        # 언론사별 상세 정보
        for publisher, articles in analyzed_articles.items():
            if articles:
                report += f"### {publisher}\n"
                report += f"- 기사 수: {len(articles)}개\n"
                
                # 데이터 소스 정보
                sources = {}
                for article in articles:
                    source = article.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
                
                source_list = ", ".join([f"{k}({v}개)" for k, v in sources.items()])
                report += f"- 데이터 소스: {source_list}\n"
                
                # 감정 분포
                sentiments = [art.get('sentiment', '중립적') for art in articles]
                sentiment_count = {s: sentiments.count(s) for s in set(sentiments)}
                report += f"- 감정 분포: {sentiment_count}\n"
                
                # 주요 기사 제목
                report += "- 주요 기사:\n"
                for i, article in enumerate(articles[:2], 1):
                    report += f"  {i}. {article['title']}\n"
                
                report += "\n"
        
        # 비교 분석 결과
        report += "## 🔍 언론사 간 비교 분석\n\n"
        report += f"**보도 톤 차이:**\n{comparison_analysis.get('tone_differences', 'N/A')}\n\n"
        report += f"**논점 차이:**\n{comparison_analysis.get('argument_differences', 'N/A')}\n\n"
        report += f"**감정적 접근 차이:**\n{comparison_analysis.get('emotional_differences', 'N/A')}\n\n"
        report += f"**특징적 관점:**\n{comparison_analysis.get('unique_perspectives', 'N/A')}\n\n"
        report += f"**종합 분석:**\n{comparison_analysis.get('overall_analysis', 'N/A')}\n\n"
        
        # 데이터 수집 방법론 추가
        report += "## 📋 수집 방법론\n"
        report += "- **하이브리드 수집**: 네이버 뉴스 API + 언론사별 RSS 피드\n"
        report += "- **중복 제거**: 제목 기반 중복 기사 자동 제거\n"
        report += "- **키워드 필터링**: 관련성 높은 기사만 선별\n"
        report += "- **실시간 수집**: 최신 뉴스 우선 수집\n\n"
        
        state["final_report"] = report
        return state

    def suggest_usage(self, state: WorkflowState) -> WorkflowState:
        """
        7단계: 분석 결과 활용 방안 제안
        """
        keyword = state["keyword"]
        comparison_analysis = state["comparison_analysis"]
        
        usage_prompt = f"""
키워드 "{keyword}"에 대한 언론사별 보도 분석이 완료되었습니다.

비교 분석 결과:
{json.dumps(comparison_analysis, ensure_ascii=False, indent=2)}

이 분석 결과를 사용자가 어떤 목적으로 활용할 수 있을지 구체적이고 실용적인 제안을 해주세요.

다음 영역별로 활용 방안을 제안해주세요:
1. 미디어 리터러시 향상
2. 연구/학술 목적
3. 비즈니스/마케팅
4. 정책/의사결정
5. 교육 목적

각 영역별로 2-3개의 구체적인 활용 방안을 제시해주세요.
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="당신은 데이터 활용 컨설턴트입니다."),
                HumanMessage(content=usage_prompt)
            ])
            
            usage_suggestions = self._parse_usage_suggestions(response.content)
            
        except Exception as e:
            print(f"활용 방안 생성 오류: {e}")
            usage_suggestions = [
                "미디어 리터러시: 서로 다른 관점의 뉴스를 비교하여 균형잡힌 시각 형성",
                "연구 목적: 언론사별 프레이밍 패턴 분석을 위한 기초 데이터",
                "교육 목적: 미디어 편향성에 대한 교육 자료"
            ]
        
        state["usage_suggestions"] = usage_suggestions
        return state

    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return text.strip()

    def _parse_article_analysis(self, content: str) -> Dict[str, Any]:
        """기사 분석 결과 파싱"""
        lines = content.strip().split('\n')
        result = {
            'summary': '',
            'tone': '중립적',
            'sentiment': '중립적',
            'main_argument': '',
            'keywords': []
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('요약:'):
                result['summary'] = line.replace('요약:', '').strip()
            elif line.startswith('어조:'):
                result['tone'] = line.replace('어조:', '').strip()
            elif line.startswith('감정:'):
                result['sentiment'] = line.replace('감정:', '').strip()
            elif line.startswith('주요논점:'):
                result['main_argument'] = line.replace('주요논점:', '').strip()
            elif line.startswith('키워드:'):
                keywords_str = line.replace('키워드:', '').strip()
                result['keywords'] = [k.strip() for k in keywords_str.split(',')]
        
        return result

    def _parse_comparison_analysis(self, content: str) -> Dict[str, str]:
        """비교 분석 결과 파싱"""
        lines = content.strip().split('\n')
        result = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('보도톤_차이:'):
                result['tone_differences'] = line.replace('보도톤_차이:', '').strip()
            elif line.startswith('논점_차이:'):
                result['argument_differences'] = line.replace('논점_차이:', '').strip()
            elif line.startswith('감정_차이:'):
                result['emotional_differences'] = line.replace('감정_차이:', '').strip()
            elif line.startswith('특징적_관점:'):
                result['unique_perspectives'] = line.replace('특징적_관점:', '').strip()
            elif line.startswith('종합_분석:'):
                result['overall_analysis'] = line.replace('종합_분석:', '').strip()
        
        return result

    def _parse_usage_suggestions(self, content: str) -> List[str]:
        """활용 방안 제안 파싱"""
        lines = content.strip().split('\n')
        suggestions = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                suggestions.append(line.lstrip('-•* '))
            elif ': ' in line and not line.startswith('#'):
                suggestions.append(line)
        
        return suggestions[:10]  # 최대 10개 제안 