import requests
import streamlit as st
import os
from typing import List, Dict, Any
import urllib.parse

class NewsAPI:
    def __init__(self):
        # 안전한 API 키 가져오기
        try:
            # Streamlit Cloud 환경
            if hasattr(st, 'secrets') and len(st.secrets) > 0:
                self.client_id = st.secrets.get("NAVER_CLIENT_ID", "")
                self.client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
            else:
                # 로컬 환경 (환경변수)
                self.client_id = os.getenv("NAVER_CLIENT_ID", "")
                self.client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
        except Exception:
            # 예외 발생시 빈 문자열
            self.client_id = ""
            self.client_secret = ""
            
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # 대상 언론사 목록
        self.target_publishers = ['조선일보', '동아일보', '한겨레', '경향신문']
        
    def search_news(self, keyword: str, display: int = 100) -> List[Dict[str, Any]]:
        """
        네이버 뉴스 API를 사용하여 키워드 관련 뉴스를 검색합니다.
        """
        if not self.client_id or not self.client_secret:
            print("⚠️ 네이버 API 크리덴셜이 설정되지 않았습니다.")
            return []
        
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': keyword,
            'display': display,
            'start': 1,
            'sort': 'date'  # 최신순 정렬
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return []
    
    def filter_by_publishers(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        지정된 언론사의 기사만 필터링하여 언론사별로 그룹화합니다.
        """
        filtered_articles = {publisher: [] for publisher in self.target_publishers}
        
        for article in articles:
            # HTML 태그 제거를 위한 간단한 처리
            title = self._clean_html_tags(article.get('title', ''))
            description = self._clean_html_tags(article.get('description', ''))
            
            # 각 언론사 이름이 기사 제목이나 링크에 포함되어 있는지 확인
            for publisher in self.target_publishers:
                if publisher in title or publisher in article.get('originallink', '') or publisher in article.get('link', ''):
                    article_data = {
                        'title': title,
                        'link': article.get('originallink', article.get('link', '')),
                        'description': description,
                        'pubDate': article.get('pubDate', ''),
                        'publisher': publisher
                    }
                    filtered_articles[publisher].append(article_data)
                    break
        
        return filtered_articles
    
    def _clean_html_tags(self, text: str) -> str:
        """
        HTML 태그와 특수 문자를 제거합니다.
        """
        import re
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        # &quot; 등의 HTML 엔티티 디코딩
        text = text.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return text.strip()
    
    def get_news_by_keyword(self, keyword: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        키워드로 뉴스를 검색하고 대상 언론사별로 필터링된 결과를 반환합니다.
        """
        print(f"'{keyword}' 키워드로 뉴스를 검색 중...")
        articles = self.search_news(keyword)
        
        if not articles:
            print("검색된 기사가 없습니다.")
            return {publisher: [] for publisher in self.target_publishers}
        
        print(f"총 {len(articles)}개의 기사를 찾았습니다.")
        filtered_articles = self.filter_by_publishers(articles)
        
        # 각 언론사별 기사 수 출력
        for publisher, articles_list in filtered_articles.items():
            print(f"{publisher}: {len(articles_list)}개 기사")
        
        return filtered_articles 