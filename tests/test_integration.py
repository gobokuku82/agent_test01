import sys
import os
import time

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news_workflow import NewsAnalysisWorkflow
from streaming_workflow import StreamingWorkflow
from unittest.mock import patch, MagicMock

def test_full_workflow_with_mock():
    """전체 워크플로우 통합 테스트 (Mock 사용)"""
    print("🧪 전체 워크플로우 통합 테스트 시작")
    print("=" * 50)
    
    try:
        # Mock 데이터 준비
        mock_articles = {
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
        
        mock_llm_response = MagicMock()
        mock_llm_response.content = """
        요약: 테스트 기사 요약입니다.
        어조: 중립적
        감정: 중립적
        주요논점: 테스트 논점입니다.
        키워드: 테스트, 통합, 워크플로우
        """
        
        # 워크플로우 실행 (Mock 사용)
        with patch('workflow_nodes.ChatOpenAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_llm_class.return_value = mock_llm
            
            with patch('enhanced_news_fetcher.EnhancedNewsAPI') as mock_api_class:
                mock_api = MagicMock()
                mock_api.collect_articles_hybrid.return_value = mock_articles
                mock_api_class.return_value = mock_api
                
                # 워크플로우 생성 및 실행
                workflow = NewsAnalysisWorkflow()
                result = workflow.run_analysis("테스트키워드")
        
        # 결과 검증
        assert "keyword" in result
        assert "selected_publishers" in result
        assert "raw_articles" in result
        assert "analyzed_articles" in result  
        assert "comparison_analysis" in result
        assert "final_report" in result
        assert "usage_suggestions" in result
        
        # 키워드 확인
        assert result["keyword"] == "테스트키워드"
        
        # 언론사 선택 확인
        assert len(result["selected_publishers"]) > 0
        
        print("✅ 전체 워크플로우 구조 검증 통과")
        print(f"📊 선택된 언론사: {result['selected_publishers']}")
        print(f"📰 수집된 기사 수: {sum(len(articles) for articles in result['raw_articles'].values())}")
        print(f"🔍 분석된 기사 수: {sum(len(articles) for articles in result['analyzed_articles'].values())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        return False

def test_streaming_workflow():
    """스트리밍 워크플로우 테스트"""
    print("\n🧪 스트리밍 워크플로우 테스트 시작")
    print("=" * 50)
    
    try:
        # Mock 설정
        with patch('workflow_nodes.ChatOpenAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "요약: 테스트\n어조: 중립적\n감정: 중립적\n주요논점: 테스트\n키워드: 테스트"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm
            
            with patch('enhanced_news_fetcher.EnhancedNewsAPI') as mock_api_class:
                mock_api = MagicMock()
                mock_api.collect_articles_hybrid.return_value = {
                    "조선일보": [{"title": "테스트", "description": "테스트", "link": "http://test.com"}]
                }
                mock_api_class.return_value = mock_api
                
                # 스트리밍 워크플로우 실행
                streaming_workflow = StreamingWorkflow()
                
                step_count = 0
                last_progress = 0
                events = []
                
                for update in streaming_workflow.run_streaming_analysis("테스트키워드"):
                    step_count += 1
                    events.append(update["type"])
                    
                    # 진행률이 증가하는지 확인
                    current_progress = update.get("progress", 0)
                    if current_progress > last_progress:
                        last_progress = current_progress
                    
                    print(f"🔄 {update['type']}: {update.get('message', '')[:50]}...")
                    
                    # 최대 20단계로 제한 (무한루프 방지)
                    if step_count > 20:
                        break
        
        # 검증
        assert step_count > 0, "스트리밍 이벤트가 발생하지 않음"
        assert "start" in events, "시작 이벤트 없음"
        assert "complete" in events, "완료 이벤트 없음"
        assert last_progress == 100, f"최종 진행률이 100%가 아님: {last_progress}%"
        
        print(f"✅ 스트리밍 테스트 통과 - 총 {step_count}개 이벤트, 최종 진행률: {last_progress}%")
        return True
        
    except Exception as e:
        print(f"❌ 스트리밍 테스트 실패: {e}")
        return False

def test_error_resilience():
    """에러 복원력 테스트"""
    print("\n🧪 에러 복원력 테스트 시작")
    print("=" * 50)
    
    try:
        # API 키 없이 워크플로우 실행
        with patch('workflow_nodes.ChatOpenAI') as mock_llm_class:
            # LLM 초기화 실패 시뮬레이션
            mock_llm_class.side_effect = Exception("API key not found")
            
            workflow = NewsAnalysisWorkflow()
            result = workflow.run_analysis("테스트키워드")
            
            # 기본값으로라도 결과가 나오는지 확인
            assert "keyword" in result
            assert result["keyword"] == "테스트키워드"
            
        print("✅ API 키 없는 상황에서도 기본 동작 확인")
        
        # 네트워크 오류 시뮬레이션
        with patch('enhanced_news_fetcher.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # 기본 상태로 초기화되는지 확인
            from enhanced_news_fetcher import EnhancedNewsAPI
            api = EnhancedNewsAPI()
            result = api.collect_articles_hybrid("테스트", ["조선일보"])
            
            # 빈 결과라도 정상적인 구조인지 확인
            assert isinstance(result, dict)
            
        print("✅ 네트워크 오류 상황에서도 안정적 동작 확인")
        return True
        
    except Exception as e:
        print(f"❌ 에러 복원력 테스트 실패: {e}")
        return False

def test_performance():
    """성능 테스트"""
    print("\n🧪 성능 테스트 시작")
    print("=" * 50)
    
    try:
        start_time = time.time()
        
        # 빠른 Mock 워크플로우 실행
        with patch('workflow_nodes.ChatOpenAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="요약: 빠른 테스트")
            mock_llm_class.return_value = mock_llm
            
            with patch('enhanced_news_fetcher.EnhancedNewsAPI') as mock_api_class:
                mock_api = MagicMock()
                mock_api.collect_articles_hybrid.return_value = {"조선일보": []}
                mock_api_class.return_value = mock_api
                
                workflow = NewsAnalysisWorkflow()
                result = workflow.run_analysis("성능테스트")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 성능 기준: 15초 이내 (네트워크 호출과 RSS 피드 처리 고려)
        assert execution_time < 15.0, f"실행 시간이 너무 김: {execution_time:.2f}초"
        
        print(f"✅ 성능 테스트 통과 - 실행 시간: {execution_time:.2f}초")
        return True
        
    except Exception as e:
        print(f"❌ 성능 테스트 실패: {e}")
        return False

def run_all_integration_tests():
    """모든 통합 테스트 실행"""
    print("🚀 통합 테스트 스위트 시작")
    print("=" * 60)
    
    tests = [
        ("전체 워크플로우", test_full_workflow_with_mock),
        ("스트리밍 워크플로우", test_streaming_workflow),
        ("에러 복원력", test_error_resilience),
        ("성능", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 실행 중...")
        success = test_func()
        results.append((test_name, success))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 통합 테스트 결과 요약")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n총 {len(tests)}개 테스트 중 {success_count}개 통과")
    
    if success_count == len(tests):
        print("🎉 모든 통합 테스트가 성공했습니다!")
    else:
        print(f"⚠️ {len(tests) - success_count}개 테스트가 실패했습니다.")
    
    return success_count == len(tests)

if __name__ == "__main__":
    run_all_integration_tests() 