import requests
import feedparser
from bs4 import BeautifulSoup
import streamlit as st
from typing import List, Dict, Any
import time
import re
from urllib.parse import urljoin, urlparse

class EnhancedNewsAPI:
    def __init__(self):
        try:
            self.naver_client_id = st.secrets["NAVER_CLIENT_ID"]
            self.naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
        except KeyError:
            self.naver_client_id = None
            self.naver_client_secret = None
        
        # 언론사별 RSS 피드와 웹사이트 정보
        self.media_sources = {
            '조선일보': {
                'rss': 'https://www.chosun.com/arc/outboundfeeds/rss/',
                'website': 'https://www.chosun.com',
                'search_url': 'https://www.chosun.com/search/?query={keyword}',
                'keywords': ['조선일보', 'chosun', '조선']
            },
            '동아일보': {
                'rss': 'https://rss.donga.com/total.xml',
                'website': 'https://www.donga.com',
                'search_url': 'https://www.donga.com/news/search?query={keyword}',
                'keywords': ['동아일보', 'donga', '동아']
            },
            '중앙일보': {
                'rss': 'https://rss.joins.com/joins_news_list.xml',
                'website': 'https://www.joongang.co.kr',
                'search_url': 'https://www.joongang.co.kr/search/{keyword}',
                'keywords': ['중앙일보', 'joongang', 'joins', '중앙']
            },
            '한겨레': {
                'rss': 'http://feeds.hani.co.kr/rss/newsstand/',
                'website': 'https://www.hani.co.kr',
                'search_url': 'https://www.hani.co.kr/arti/SEARCH/{keyword}',
                'keywords': ['한겨레', 'hani', '경향']
            },
            '경향신문': {
                'rss': 'http://rss.khan.co.kr/rss.xml',
                'website': 'https://www.khan.co.kr',
                'search_url': 'https://www.khan.co.kr/search/{keyword}',
                'keywords': ['경향신문', 'khan', '경향']
            },
            'SBS': {
                'rss': 'https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01',
                'website': 'https://news.sbs.co.kr',
                'search_url': 'https://news.sbs.co.kr/news/search/main.do?query={keyword}',
                'keywords': ['SBS', 'sbs']
            },
            'MBC': {
                'rss': 'https://imnews.imbc.com/rss/news/news_00.xml',
                'website': 'https://imnews.imbc.com',
                'search_url': 'https://imnews.imbc.com/search/{keyword}',
                'keywords': ['MBC', 'mbc', 'imbc']
            },
            'KBS': {
                'rss': 'http://world.kbs.co.kr/rss/rss_news.htm',
                'website': 'https://news.kbs.co.kr',
                'search_url': 'https://news.kbs.co.kr/search/{keyword}',
                'keywords': ['KBS', 'kbs']
            }
        }

    def collect_articles_hybrid(self, keyword: str, publishers: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        네이버 API + RSS + 웹 스크래핑을 결합한 하이브리드 기사 수집
        """
        all_articles = {}
        
        print(f"🔍 '{keyword}' 키워드로 하이브리드 기사 수집 시작")
        
        # 1. 네이버 API로 기본 데이터 수집
        naver_articles = self._get_naver_articles(keyword)
        naver_filtered = self._filter_naver_articles(naver_articles, publishers)
        
        # 2. RSS 피드에서 추가 수집
        for publisher in publishers:
            print(f"📰 {publisher} 기사 수집 중...")
            
            articles = []
            
            # 네이버 API 결과 추가
            if publisher in naver_filtered:
                articles.extend(naver_filtered[publisher])
            
            # RSS 피드에서 추가 수집
            rss_articles = self._get_rss_articles(publisher, keyword)
            articles.extend(rss_articles)
            
            # 중복 제거 및 최대 3개 선택
            unique_articles = self._remove_duplicates(articles)
            all_articles[publisher] = unique_articles[:3]
            
            print(f"  -> {len(all_articles[publisher])}개 기사 수집 완료")
            
            # API 호출 제한을 위한 딜레이
            time.sleep(1)
        
        return all_articles

    def _get_naver_articles(self, keyword: str) -> List[Dict[str, Any]]:
        """네이버 뉴스 API에서 기사 수집"""
        if not self.naver_client_id or not self.naver_client_secret:
            print("⚠️ 네이버 API 키가 없어 RSS 피드만 사용합니다.")
            return []
        
        headers = {
            'X-Naver-Client-Id': self.naver_client_id,
            'X-Naver-Client-Secret': self.naver_client_secret
        }
        
        params = {
            'query': keyword,
            'display': 100,  # 더 많은 기사 요청
            'start': 1,
            'sort': 'date'
        }
        
        try:
            response = requests.get(
                "https://openapi.naver.com/v1/search/news.json",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                articles = response.json().get('items', [])
                print(f"📊 네이버 API: {len(articles)}개 기사 수집")
                return articles
            else:
                print(f"❌ 네이버 API 오류: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 네이버 API 호출 실패: {e}")
            return []

    def _filter_naver_articles(self, articles: List[Dict[str, Any]], publishers: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """네이버 API 결과를 언론사별로 필터링 (개선된 매칭)"""
        filtered = {pub: [] for pub in publishers}
        
        for article in articles:
            title = self._clean_html(article.get('title', ''))
            description = self._clean_html(article.get('description', ''))
            link = article.get('originallink', article.get('link', ''))
            
            # 각 언론사의 키워드로 매칭 시도
            for publisher in publishers:
                if publisher in self.media_sources:
                    keywords = self.media_sources[publisher]['keywords']
                    
                    # 제목, 설명, 링크에서 언론사 키워드 검색
                    if any(keyword.lower() in title.lower() or 
                           keyword.lower() in description.lower() or 
                           keyword.lower() in link.lower() 
                           for keyword in keywords):
                        
                        filtered[publisher].append({
                            'title': title,
                            'description': description,
                            'link': link,
                            'pubDate': article.get('pubDate', ''),
                            'publisher': publisher,
                            'source': 'naver_api'
                        })
                        break
        
        return filtered

    def _get_rss_articles(self, publisher: str, keyword: str) -> List[Dict[str, Any]]:
        """RSS 피드에서 기사 수집"""
        if publisher not in self.media_sources:
            return []
        
        rss_url = self.media_sources[publisher]['rss']
        articles = []
        
        try:
            # RSS 피드 파싱
            response = requests.get(rss_url, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:20]:  # 최근 20개 항목만 확인
                    title = entry.get('title', '')
                    description = entry.get('description', '') or entry.get('summary', '')
                    link = entry.get('link', '')
                    pub_date = entry.get('published', '')
                    
                    # 키워드가 제목이나 설명에 포함된 경우만 선택
                    if (keyword.lower() in title.lower() or 
                        keyword.lower() in description.lower()):
                        
                        articles.append({
                            'title': self._clean_html(title),
                            'description': self._clean_html(description)[:300] + '...',
                            'link': link,
                            'pubDate': pub_date,
                            'publisher': publisher,
                            'source': 'rss_feed'
                        })
                
                print(f"  📡 RSS 피드: {len(articles)}개 관련 기사 발견")
                
        except Exception as e:
            print(f"  ❌ RSS 피드 오류 ({publisher}): {e}")
        
        return articles

    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 기사 제거"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article['title'].lower().strip()
            # 제목의 첫 30자로 중복 판단
            title_key = title[:30]
            
            if title_key not in seen_titles and len(title) > 10:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles

    def _clean_html(self, text: str) -> str:
        """HTML 태그 및 특수 문자 제거"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        # HTML 엔티티 디코딩
        text = text.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        text = text.replace('&nbsp;', ' ').replace('&#39;', "'")
        
        return text.strip()

    def get_sample_articles(self, publishers: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        키워드 없이 각 언론사의 최신 기사 샘플 수집 (테스트용)
        """
        sample_articles = {}
        
        for publisher in publishers:
            if publisher not in self.media_sources:
                continue
                
            print(f"📰 {publisher} 최신 기사 샘플 수집 중...")
            
            try:
                rss_url = self.media_sources[publisher]['rss']
                response = requests.get(rss_url, timeout=10)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    articles = []
                    
                    for entry in feed.entries[:3]:  # 최신 3개만
                        articles.append({
                            'title': self._clean_html(entry.get('title', '')),
                            'description': self._clean_html(entry.get('description', '') or entry.get('summary', ''))[:200] + '...',
                            'link': entry.get('link', ''),
                            'pubDate': entry.get('published', ''),
                            'publisher': publisher,
                            'source': 'rss_sample'
                        })
                    
                    sample_articles[publisher] = articles
                    print(f"  ✅ {len(articles)}개 샘플 기사 수집")
                    
            except Exception as e:
                print(f"  ❌ {publisher} 샘플 수집 실패: {e}")
                sample_articles[publisher] = []
            
            time.sleep(1)  # 요청 간격 조절
        
        return sample_articles

# 기존 NewsWorkflowNodes에서 사용할 수 있도록 헬퍼 함수 제공
def get_enhanced_news_api():
    """EnhancedNewsAPI 인스턴스 반환"""
    return EnhancedNewsAPI() 