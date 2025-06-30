import openai
import streamlit as st
from typing import Dict, List, Any, Tuple

class NewsAnalyzer:
    def __init__(self):
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            self.client = openai.OpenAI(api_key=api_key)
        except KeyError:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다. Streamlit secrets를 확인해주세요.")
    
    def analyze_article(self, title: str, description: str) -> Dict[str, Any]:
        """
        기사 제목과 요약을 분석하여 요약, 감정, 프레이밍을 반환합니다.
        """
        try:
            # 프롬프트 구성
            prompt = f"""
다음 뉴스 기사를 분석해주세요:

제목: {title}
내용: {description}

다음 형식으로 분석 결과를 제공해주세요:

1. 요약 (3문장 이하로 핵심 내용 요약)
2. 감정 분석 (긍정적/중립적/부정적 중 하나)
3. 프레이밍 분석 (이 기사가 취하고 있는 주요 관점이나 입장을 간단히 설명)

응답 형식:
요약: [3문장 이하 요약]
감정: [긍정적/중립적/부정적]
프레이밍: [주요 관점이나 입장 설명]
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 뉴스 기사 분석 전문가입니다. 한국어로 정확하고 객관적인 분석을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis(analysis_text)
            
        except Exception as e:
            print(f"분석 중 오류 발생: {e}")
            return {
                'summary': '분석을 수행할 수 없습니다.',
                'sentiment': '중립적',
                'framing': '분석 불가'
            }
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        GPT 응답을 파싱하여 구조화된 데이터로 변환합니다.
        """
        lines = analysis_text.strip().split('\n')
        result = {
            'summary': '',
            'sentiment': '중립적',
            'framing': ''
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('요약:'):
                result['summary'] = line.replace('요약:', '').strip()
            elif line.startswith('감정:'):
                sentiment = line.replace('감정:', '').strip()
                if '긍정' in sentiment:
                    result['sentiment'] = '긍정적'
                elif '부정' in sentiment:
                    result['sentiment'] = '부정적'
                else:
                    result['sentiment'] = '중립적'
            elif line.startswith('프레이밍:'):
                result['framing'] = line.replace('프레이밍:', '').strip()
        
        return result
    
    def analyze_articles_batch(self, articles_by_publisher: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        언론사별 기사들을 일괄 분석합니다.
        """
        analyzed_articles = {}
        
        for publisher, articles in articles_by_publisher.items():
            print(f"{publisher} 기사 분석 중...")
            analyzed_articles[publisher] = []
            
            for i, article in enumerate(articles[:5]):  # 각 언론사당 최대 5개 기사만 분석
                print(f"  {i+1}/{min(len(articles), 5)} 기사 분석 중...")
                
                analysis = self.analyze_article(article['title'], article['description'])
                
                analyzed_article = article.copy()
                analyzed_article.update(analysis)
                analyzed_articles[publisher].append(analyzed_article)
        
        return analyzed_articles
    
    def get_sentiment_distribution(self, analyzed_articles: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, int]]:
        """
        언론사별 감정 분포를 계산합니다.
        """
        sentiment_dist = {}
        
        for publisher, articles in analyzed_articles.items():
            sentiment_count = {'긍정적': 0, '중립적': 0, '부정적': 0}
            
            for article in articles:
                sentiment = article.get('sentiment', '중립적')
                if sentiment in sentiment_count:
                    sentiment_count[sentiment] += 1
            
            sentiment_dist[publisher] = sentiment_count
        
        return sentiment_dist 