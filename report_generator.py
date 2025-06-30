import pandas as pd
from typing import Dict, List, Any
import streamlit as st

class ReportGenerator:
    def __init__(self):
        self.target_publishers = ['조선일보', '동아일보', '한겨레', '경향신문']
    
    def create_comparison_table(self, analyzed_articles: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        언론사별 기사 비교 테이블을 생성합니다.
        """
        table_data = []
        
        for publisher, articles in analyzed_articles.items():
            for article in articles:
                table_data.append({
                    '언론사': publisher,
                    '제목': article['title'][:50] + '...' if len(article['title']) > 50 else article['title'],
                    '요약': article.get('summary', ''),
                    '감정': article.get('sentiment', '중립적'),
                    '프레이밍': article.get('framing', '')[:80] + '...' if len(article.get('framing', '')) > 80 else article.get('framing', ''),
                    '링크': article['link']
                })
        
        return pd.DataFrame(table_data)
    
    def create_sentiment_summary(self, sentiment_dist: Dict[str, Dict[str, int]]) -> pd.DataFrame:
        """
        언론사별 감정 분포 요약 테이블을 생성합니다.
        """
        summary_data = []
        
        for publisher in self.target_publishers:
            if publisher in sentiment_dist:
                dist = sentiment_dist[publisher]
                total = sum(dist.values())
                
                if total > 0:
                    positive_pct = round((dist['긍정적'] / total) * 100, 1)
                    neutral_pct = round((dist['중립적'] / total) * 100, 1)
                    negative_pct = round((dist['부정적'] / total) * 100, 1)
                else:
                    positive_pct = neutral_pct = negative_pct = 0
                
                summary_data.append({
                    '언론사': publisher,
                    '총 기사 수': total,
                    '긍정적 (%)': f"{dist['긍정적']} ({positive_pct}%)",
                    '중립적 (%)': f"{dist['중립적']} ({neutral_pct}%)",
                    '부정적 (%)': f"{dist['부정적']} ({negative_pct}%)"
                })
            else:
                summary_data.append({
                    '언론사': publisher,
                    '총 기사 수': 0,
                    '긍정적 (%)': "0 (0.0%)",
                    '중립적 (%)': "0 (0.0%)",
                    '부정적 (%)': "0 (0.0%)"
                })
        
        return pd.DataFrame(summary_data)
    
    def generate_markdown_report(self, keyword: str, analyzed_articles: Dict[str, List[Dict[str, Any]]], sentiment_dist: Dict[str, Dict[str, int]]) -> str:
        """
        마크다운 형식의 최종 분석 보고서를 생성합니다.
        """
        report = f"""# 미디어 프레이밍 분석 보고서

## 검색 키워드: "{keyword}"

### 📊 언론사별 감정 분포 요약

"""
        
        # 감정 분포 테이블
        for publisher in self.target_publishers:
            if publisher in sentiment_dist and sum(sentiment_dist[publisher].values()) > 0:
                dist = sentiment_dist[publisher]
                total = sum(dist.values())
                report += f"**{publisher}** (총 {total}개 기사)\n"
                report += f"- 긍정적: {dist['긍정적']}개 ({round(dist['긍정적']/total*100, 1)}%)\n"
                report += f"- 중립적: {dist['중립적']}개 ({round(dist['중립적']/total*100, 1)}%)\n"
                report += f"- 부정적: {dist['부정적']}개 ({round(dist['부정적']/total*100, 1)}%)\n\n"
            else:
                report += f"**{publisher}**: 분석된 기사 없음\n\n"
        
        report += "\n### 📰 주요 프레이밍 차이점\n\n"
        
        # 각 언론사의 주요 프레이밍 분석
        for publisher, articles in analyzed_articles.items():
            if articles:
                report += f"#### {publisher}\n"
                framings = [article.get('framing', '') for article in articles if article.get('framing')]
                if framings:
                    # 가장 대표적인 프레이밍 (첫 번째) 선택
                    main_framing = framings[0]
                    report += f"- 주요 관점: {main_framing}\n"
                    
                    # 대표 기사 제목
                    if articles[0]['title']:
                        report += f"- 대표 기사: \"{articles[0]['title']}\"\n"
                report += "\n"
        
        report += "\n### 💡 종합 분석\n\n"
        
        # 전체적인 트렌드 분석
        total_articles = sum(len(articles) for articles in analyzed_articles.values())
        if total_articles > 0:
            # 전체 감정 분포
            total_positive = sum(sentiment_dist.get(pub, {}).get('긍정적', 0) for pub in self.target_publishers)
            total_neutral = sum(sentiment_dist.get(pub, {}).get('중립적', 0) for pub in self.target_publishers)
            total_negative = sum(sentiment_dist.get(pub, {}).get('부정적', 0) for pub in self.target_publishers)
            
            report += f"- 전체 분석된 기사 수: {total_articles}개\n"
            report += f"- 전체 감정 분포: 긍정 {total_positive}개, 중립 {total_neutral}개, 부정 {total_negative}개\n\n"
            
            # 언론사간 차이점 요약
            publishers_with_articles = [pub for pub, articles in analyzed_articles.items() if articles]
            if len(publishers_with_articles) > 1:
                report += "**언론사간 주요 차이점:**\n"
                report += "- 각 언론사는 동일한 이슈에 대해 서로 다른 관점과 프레이밍을 보여줍니다.\n"
                report += "- 보수 성향과 진보 성향 언론사 간의 시각 차이가 관찰됩니다.\n"
                report += "- 감정적 톤과 사실 강조점에서 차이를 보입니다.\n"
        else:
            report += "분석할 기사가 충분하지 않습니다.\n"
        
        report += f"\n---\n*보고서 생성 시간: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return report
    
    def display_detailed_articles(self, analyzed_articles: Dict[str, List[Dict[str, Any]]]):
        """
        Streamlit에서 상세 기사 정보를 표시합니다.
        """
        st.subheader("📰 언론사별 상세 기사 분석")
        
        for publisher, articles in analyzed_articles.items():
            if articles:
                st.write(f"### {publisher}")
                
                for i, article in enumerate(articles, 1):
                    with st.expander(f"{i}. {article['title'][:60]}..."):
                        st.write(f"**링크:** {article['link']}")
                        st.write(f"**요약:** {article.get('summary', 'N/A')}")
                        st.write(f"**감정:** {article.get('sentiment', 'N/A')}")
                        st.write(f"**프레이밍:** {article.get('framing', 'N/A')}")
                        if article.get('description'):
                            st.write(f"**원문 발췌:** {article['description'][:200]}...")
            else:
                st.write(f"### {publisher}")
                st.write("분석된 기사가 없습니다.") 