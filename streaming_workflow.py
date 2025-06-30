import streamlit as st
from news_workflow import NewsAnalysisWorkflow
import time
from typing import Generator, Dict, Any
import json

class StreamingWorkflow:
    def __init__(self):
        self.workflow = NewsAnalysisWorkflow()
        self.steps = [
            {
                "name": "decide_publishers",
                "title": "🎯 언론사 선택",
                "description": "키워드를 분석하여 최적의 언론사를 선택합니다",
                "progress": 15
            },
            {
                "name": "collect_articles", 
                "title": "📰 기사 수집",
                "description": "선택된 언론사에서 관련 기사를 수집합니다",
                "progress": 35
            },
            {
                "name": "analyze_articles",
                "title": "🔍 기사 분석", 
                "description": "각 기사의 요약, 어조, 감정을 분석합니다",
                "progress": 60
            },
            {
                "name": "compare_analysis",
                "title": "📊 비교 분석",
                "description": "언론사 간 입장 차이를 비교 분석합니다", 
                "progress": 80
            },
            {
                "name": "generate_report",
                "title": "📄 보고서 생성",
                "description": "종합 분석 보고서를 작성합니다",
                "progress": 95
            },
            {
                "name": "suggest_usage",
                "title": "💡 활용 방안 제안",
                "description": "분석 결과 활용 방안을 제안합니다",
                "progress": 100
            }
        ]

    def run_streaming_analysis(self, keyword: str) -> Generator[Dict[str, Any], None, None]:
        """
        단계별 실시간 피드백을 제공하는 스트리밍 분석
        """
        
        # 초기 상태 설정
        state = {
            "keyword": keyword,
            "selected_publishers": [],
            "raw_articles": {},
            "analyzed_articles": {},
            "comparison_analysis": {},
            "final_report": "",
            "usage_suggestions": []
        }
        
        yield {
            "type": "start",
            "message": f"🚀 '{keyword}' 키워드 분석을 시작합니다!",
            "progress": 0,
            "state": state
        }
        
        time.sleep(1)
        
        # 각 단계별 실행
        for i, step in enumerate(self.steps):
            # 단계 시작 알림
            yield {
                "type": "step_start",
                "step": step["name"],
                "message": f"📋 {step['title']}: {step['description']}",
                "progress": step["progress"] - 5,
                "state": state
            }
            
            time.sleep(0.5)
            
            # 단계 실행 중 알림
            yield {
                "type": "step_running", 
                "step": step["name"],
                "message": f"⚙️ {step['title']} 실행 중...",
                "progress": step["progress"] - 2,
                "state": state
            }
            
            # 실제 단계 실행
            try:
                if step["name"] == "decide_publishers":
                    state = self.workflow.nodes.decide_publishers(state)
                    result_msg = f"✅ 선택된 언론사: {', '.join(state['selected_publishers'])}"
                    
                elif step["name"] == "collect_articles":
                    state = self.workflow.nodes.collect_articles(state)
                    total_articles = sum(len(articles) for articles in state['raw_articles'].values())
                    result_msg = f"✅ 총 {total_articles}개 기사 수집 완료"
                    
                elif step["name"] == "analyze_articles":
                    state = self.workflow.nodes.analyze_articles(state)
                    analyzed_count = sum(len(articles) for articles in state['analyzed_articles'].values())
                    result_msg = f"✅ {analyzed_count}개 기사 분석 완료"
                    
                elif step["name"] == "compare_analysis":
                    state = self.workflow.nodes.compare_analysis(state)
                    comparison_keys = len(state['comparison_analysis'])
                    result_msg = f"✅ {comparison_keys}개 관점에서 비교 분석 완료"
                    
                elif step["name"] == "generate_report":
                    state = self.workflow.nodes.generate_report(state)
                    report_length = len(state['final_report'])
                    result_msg = f"✅ {report_length:,}자 분량의 보고서 생성 완료"
                    
                elif step["name"] == "suggest_usage":
                    state = self.workflow.nodes.suggest_usage(state)
                    suggestion_count = len(state['usage_suggestions'])
                    result_msg = f"✅ {suggestion_count}개 활용 방안 제안 완료"
                
                # 단계 완료 알림
                yield {
                    "type": "step_complete",
                    "step": step["name"], 
                    "message": result_msg,
                    "progress": step["progress"],
                    "state": state,
                    "step_data": self._get_step_data(step["name"], state)
                }
                
            except Exception as e:
                yield {
                    "type": "step_error",
                    "step": step["name"],
                    "message": f"❌ {step['title']} 중 오류 발생: {str(e)}",
                    "progress": step["progress"],
                    "state": state
                }
            
            time.sleep(1)
        
        # 최종 완료
        yield {
            "type": "complete",
            "message": "🎉 모든 분석이 완료되었습니다!",
            "progress": 100,
            "state": state
        }

    def _get_step_data(self, step_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """각 단계별 결과 데이터 추출"""
        
        if step_name == "decide_publishers":
            return {
                "selected_publishers": state.get("selected_publishers", []),
                "total_count": len(state.get("selected_publishers", []))
            }
            
        elif step_name == "collect_articles":
            raw_articles = state.get("raw_articles", {})
            return {
                "articles_by_publisher": {
                    pub: len(articles) for pub, articles in raw_articles.items()
                },
                "total_articles": sum(len(articles) for articles in raw_articles.values()),
                "data_sources": self._get_data_sources(raw_articles)
            }
            
        elif step_name == "analyze_articles":
            analyzed_articles = state.get("analyzed_articles", {})
            return {
                "analyzed_count": sum(len(articles) for articles in analyzed_articles.values()),
                "sentiment_distribution": self._get_sentiment_distribution(analyzed_articles)
            }
            
        elif step_name == "compare_analysis":
            return {
                "comparison_analysis": state.get("comparison_analysis", {}),
                "analysis_points": len(state.get("comparison_analysis", {}))
            }
            
        elif step_name == "generate_report":
            report = state.get("final_report", "")
            return {
                "report_length": len(report),
                "report_preview": report[:200] + "..." if len(report) > 200 else report
            }
            
        elif step_name == "suggest_usage":
            return {
                "usage_suggestions": state.get("usage_suggestions", []),
                "suggestion_count": len(state.get("usage_suggestions", []))
            }
        
        return {}

    def _get_data_sources(self, raw_articles: Dict[str, Any]) -> Dict[str, int]:
        """데이터 소스별 통계"""
        sources = {}
        for articles in raw_articles.values():
            for article in articles:
                source = article.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
        return sources

    def _get_sentiment_distribution(self, analyzed_articles: Dict[str, Any]) -> Dict[str, int]:
        """감정 분포 통계"""
        sentiments = {}
        for articles in analyzed_articles.values():
            for article in articles:
                sentiment = article.get('sentiment', '중립적')
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        return sentiments 