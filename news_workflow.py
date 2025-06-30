from langgraph.graph import StateGraph, END
from workflow_nodes import NewsWorkflowNodes, WorkflowState
from typing import Dict, Any

class NewsAnalysisWorkflow:
    def __init__(self):
        self.nodes = NewsWorkflowNodes()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """LangGraph 워크플로우 구성"""
        
        # StateGraph 생성
        workflow = StateGraph(WorkflowState)
        
        # 노드 추가
        workflow.add_node("decide_publishers", self.nodes.decide_publishers)
        workflow.add_node("collect_articles", self.nodes.collect_articles)
        workflow.add_node("analyze_articles", self.nodes.analyze_articles)
        workflow.add_node("compare_analysis", self.nodes.compare_analysis)
        workflow.add_node("generate_report", self.nodes.generate_report)
        workflow.add_node("suggest_usage", self.nodes.suggest_usage)
        
        # 엣지 정의 (노드 간 연결)
        workflow.set_entry_point("decide_publishers")
        workflow.add_edge("decide_publishers", "collect_articles")
        workflow.add_edge("collect_articles", "analyze_articles")
        workflow.add_edge("analyze_articles", "compare_analysis")
        workflow.add_edge("compare_analysis", "generate_report")
        workflow.add_edge("generate_report", "suggest_usage")
        workflow.add_edge("suggest_usage", END)
        
        return workflow.compile()

    def run_analysis(self, keyword: str) -> Dict[str, Any]:
        """
        전체 뉴스 분석 워크플로우 실행
        """
        print(f"🚀 '{keyword}' 키워드 분석 시작")
        print("=" * 50)
        
        # 초기 상태 설정
        initial_state = {
            "keyword": keyword,
            "selected_publishers": [],
            "raw_articles": {},
            "analyzed_articles": {},
            "comparison_analysis": {},
            "final_report": "",
            "usage_suggestions": []
        }
        
        try:
            # 워크플로우 실행
            final_state = self.workflow.invoke(initial_state)
            
            print("✅ 분석 완료!")
            print("=" * 50)
            
            return final_state
            
        except Exception as e:
            print(f"❌ 워크플로우 실행 중 오류: {e}")
            return initial_state

    def get_workflow_status(self) -> str:
        """워크플로우 상태 정보 반환"""
        return """
        📋 뉴스 분석 워크플로우 단계:
        
        1️⃣ 언론사 결정 (decide_publishers)
           - 키워드 분석을 통한 관련 언론사 선택
           
        2️⃣ 기사 수집 (collect_articles)  
           - 선택된 언론사별 기사 수집
           
        3️⃣ 기사 분석 (analyze_articles)
           - 요약, 어조, 감정, 논점 분석
           
        4️⃣ 비교 분석 (compare_analysis)
           - 언론사 간 입장 차이 분석
           
        5️⃣ 보고서 생성 (generate_report)
           - 종합 분석 보고서 작성
           
        6️⃣ 활용 방안 제안 (suggest_usage)
           - 분석 결과 활용 방안 제시
        """

# 워크플로우 실행을 위한 헬퍼 함수
def run_news_analysis(keyword: str) -> Dict[str, Any]:
    """
    뉴스 분석 워크플로우를 실행하는 메인 함수
    """
    workflow = NewsAnalysisWorkflow()
    return workflow.run_analysis(keyword)

if __name__ == "__main__":
    # 테스트 실행
    keyword = "대통령"
    result = run_news_analysis(keyword)
    
    if result.get("final_report"):
        print("\n" + "="*60)
        print("📄 최종 보고서")
        print("="*60)
        print(result["final_report"])
        
        print("\n" + "="*60)
        print("💡 활용 방안")
        print("="*60)
        for i, suggestion in enumerate(result.get("usage_suggestions", []), 1):
            print(f"{i}. {suggestion}")
    else:
        print("❌ 분석 결과를 생성할 수 없습니다.") 