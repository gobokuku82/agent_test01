import unittest
import sys
import os

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_nodes import NewsWorkflowNodes, WorkflowState
from unittest.mock import patch, MagicMock

class TestWorkflowNodes(unittest.TestCase):
    def setUp(self):
        """테스트 환경 설정"""
        # Mock LLM으로 테스트 (API 키 없어도 됨)
        with patch('workflow_nodes.ChatOpenAI') as mock_llm:
            mock_llm.return_value = MagicMock()
            self.nodes = NewsWorkflowNodes()
        
        self.test_state = {
            "keyword": "테스트키워드",
            "selected_publishers": [],
            "raw_articles": {},
            "analyzed_articles": {},
            "comparison_analysis": {},
            "final_report": "",
            "usage_suggestions": []
        }
    
    def test_decide_publishers_basic(self):
        """언론사 선택 기본 테스트"""
        result = self.nodes.decide_publishers(self.test_state)
        
        # 기본 검증
        self.assertIn("selected_publishers", result)
        self.assertIsInstance(result["selected_publishers"], list)
        self.assertTrue(len(result["selected_publishers"]) > 0)
        self.assertEqual(result["keyword"], "테스트키워드")
        
        print("✅ 언론사 선택 기본 테스트 통과")
    
    def test_collect_articles_with_publishers(self):
        """기사 수집 테스트 (언론사 선택 후)"""
        # 언론사가 선택된 상태로 설정
        self.test_state["selected_publishers"] = ["조선일보", "한겨레"]
        
        # Mock enhanced_news_api
        with patch.object(self.nodes, 'enhanced_news_api') as mock_api:
            mock_api.collect_articles_hybrid.return_value = {
                "조선일보": [
                    {
                        "title": "테스트 기사 1",
                        "description": "테스트 내용 1",
                        "link": "http://test1.com",
                        "source": "test"
                    }
                ],
                "한겨레": [
                    {
                        "title": "테스트 기사 2", 
                        "description": "테스트 내용 2",
                        "link": "http://test2.com",
                        "source": "test"
                    }
                ]
            }
            
            result = self.nodes.collect_articles(self.test_state)
            
            # 검증
            self.assertIn("raw_articles", result)
            self.assertIsInstance(result["raw_articles"], dict)
            self.assertEqual(len(result["raw_articles"]), 2)
            self.assertIn("조선일보", result["raw_articles"])
            self.assertIn("한겨레", result["raw_articles"])
            
            print("✅ 기사 수집 테스트 통과")
    
    def test_analyze_articles_with_mock_llm(self):
        """기사 분석 테스트 (Mock LLM 사용)"""
        # 원시 기사 상태 설정
        self.test_state["raw_articles"] = {
            "조선일보": [
                {
                    "title": "테스트 기사",
                    "description": "테스트 내용",
                    "link": "http://test.com"
                }
            ]
        }
        
        # Mock LLM 응답 설정
        mock_response = MagicMock()
        mock_response.content = """
        요약: 테스트 기사 요약입니다.
        어조: 중립적
        감정: 중립적
        주요논점: 테스트 논점
        키워드: 테스트, 키워드, 분석
        """
        
        with patch.object(self.nodes, 'llm') as mock_llm:
            mock_llm.invoke.return_value = mock_response
            
            result = self.nodes.analyze_articles(self.test_state)
            
            # 검증
            self.assertIn("analyzed_articles", result)
            self.assertEqual(len(result["analyzed_articles"]["조선일보"]), 1)
            
            analyzed_article = result["analyzed_articles"]["조선일보"][0]
            self.assertIn("summary", analyzed_article)
            self.assertIn("tone", analyzed_article)
            self.assertIn("sentiment", analyzed_article)
            
            print("✅ 기사 분석 테스트 통과")
    
    def test_state_immutability(self):
        """상태 불변성 테스트"""
        # 원본 상태를 깊은 복사로 보존
        original_state = {
            "keyword": self.test_state["keyword"],
            "selected_publishers": self.test_state["selected_publishers"].copy(),
            "raw_articles": self.test_state["raw_articles"].copy(),
            "analyzed_articles": self.test_state["analyzed_articles"].copy(),
            "comparison_analysis": self.test_state["comparison_analysis"].copy(),
            "final_report": self.test_state["final_report"],
            "usage_suggestions": self.test_state["usage_suggestions"].copy()
        }
        
        # 언론사 선택 실행
        result = self.nodes.decide_publishers(self.test_state)
        
        # 원본 상태가 변경되지 않았는지 확인
        self.assertEqual(self.test_state["keyword"], original_state["keyword"])
        self.assertEqual(self.test_state["selected_publishers"], original_state["selected_publishers"])
        self.assertEqual(self.test_state["raw_articles"], original_state["raw_articles"])
        
        # 결과는 새로운 상태를 가져야 함
        self.assertNotEqual(result["selected_publishers"], original_state["selected_publishers"])
        self.assertTrue(len(result["selected_publishers"]) > 0)
        
        print("✅ 상태 불변성 테스트 통과")
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        # LLM이 None인 경우
        self.nodes.llm = None
        
        result = self.nodes.decide_publishers(self.test_state)
        
        # 기본값 언론사가 선택되는지 확인
        self.assertIn("selected_publishers", result)
        self.assertTrue(len(result["selected_publishers"]) > 0)
        
        print("✅ 에러 처리 테스트 통과")

class TestWorkflowState(unittest.TestCase):
    def test_state_structure(self):
        """WorkflowState 구조 테스트"""
        state = {
            "keyword": "테스트",
            "selected_publishers": ["조선일보"],
            "raw_articles": {"조선일보": []},
            "analyzed_articles": {"조선일보": []},
            "comparison_analysis": {},
            "final_report": "",
            "usage_suggestions": []
        }
        
        # 필수 필드 확인
        required_fields = [
            "keyword", "selected_publishers", "raw_articles",
            "analyzed_articles", "comparison_analysis", 
            "final_report", "usage_suggestions"
        ]
        
        for field in required_fields:
            self.assertIn(field, state)
        
        print("✅ WorkflowState 구조 테스트 통과")

def run_tests():
    """테스트 실행 함수"""
    print("🧪 워크플로우 노드 테스트 시작")
    print("=" * 50)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 테스트 케이스 추가
    test_suite.addTest(TestWorkflowNodes('test_decide_publishers_basic'))
    test_suite.addTest(TestWorkflowNodes('test_collect_articles_with_publishers'))
    test_suite.addTest(TestWorkflowNodes('test_analyze_articles_with_mock_llm'))
    test_suite.addTest(TestWorkflowNodes('test_state_immutability'))
    test_suite.addTest(TestWorkflowNodes('test_error_handling'))
    test_suite.addTest(TestWorkflowState('test_state_structure'))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print(f"❌ {len(result.failures)} 테스트 실패, {len(result.errors)} 에러 발생")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests() 