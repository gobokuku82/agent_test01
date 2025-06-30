#!/usr/bin/env python3
"""
🧪 한국 언론사 미디어 프레이밍 분석기 - 전체 테스트 실행기

이 스크립트는 프로젝트의 모든 테스트를 실행합니다:
- 단위 테스트 (workflow_nodes 테스트)
- 통합 테스트 (전체 워크플로우 테스트)
- 성능 테스트
- 에러 복원력 테스트

사용법:
    python tests/run_all_tests.py
    또는
    cd tests && python run_all_tests.py
"""

import sys
import os
import time
import subprocess

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header(title, width=60):
    """테스트 섹션 헤더 출력"""
    print("\n" + "=" * width)
    print(f" {title} ".center(width, "="))
    print("=" * width)

def print_separator():
    """구분선 출력"""
    print("-" * 60)

def run_unit_tests():
    """단위 테스트 실행"""
    print_header("🔬 단위 테스트")
    
    try:
        # test_workflow_nodes.py 실행
        from test_workflow_nodes import run_tests
        success = run_tests()
        
        if success:
            print("✅ 단위 테스트 전체 통과!")
            return True
        else:
            print("❌ 단위 테스트 일부 실패")
            return False
            
    except Exception as e:
        print(f"❌ 단위 테스트 실행 중 오류: {e}")
        return False

def run_integration_tests():
    """통합 테스트 실행"""
    print_header("🔗 통합 테스트")
    
    try:
        # test_integration.py 실행
        from test_integration import run_all_integration_tests
        success = run_all_integration_tests()
        
        if success:
            print("✅ 통합 테스트 전체 통과!")
            return True
        else:
            print("❌ 통합 테스트 일부 실패")
            return False
            
    except Exception as e:
        print(f"❌ 통합 테스트 실행 중 오류: {e}")
        return False

def run_dependency_check():
    """종속성 검사"""
    print_header("📦 종속성 검사")
    
    required_packages = [
        'streamlit', 'requests', 'openai', 'pandas',
        'beautifulsoup4', 'langchain', 'langchain-openai', 
        'langgraph', 'feedparser'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 설치되지 않음")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령으로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ 모든 필수 패키지가 설치되어 있습니다!")
        return True

def run_code_structure_check():
    """코드 구조 검사"""
    print_header("🏗️ 코드 구조 검사")
    
    required_files = [
        'streamlit_app.py',
        'streaming_workflow.py', 
        'news_workflow.py',
        'workflow_nodes.py',
        'enhanced_news_fetcher.py',
        'requirements.txt'
    ]
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    missing_files = []
    
    for file_name in required_files:
        file_path = os.path.join(project_root, file_name)
        if os.path.exists(file_path):
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - 파일 없음")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠️ 누락된 파일: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 모든 필수 파일이 존재합니다!")
        return True

def generate_test_report(results):
    """테스트 결과 보고서 생성"""
    print_header("📊 테스트 결과 보고서")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"총 테스트 카테고리: {total_tests}")
    print(f"통과: {passed_tests}")
    print(f"실패: {failed_tests}")
    print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n상세 결과:")
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"  {test_name}: {status}")
    
    # 실패한 테스트가 있으면 권장사항 제시
    if failed_tests > 0:
        print("\n🔧 문제 해결 권장사항:")
        
        for test_name, success in results:
            if not success:
                if "종속성" in test_name:
                    print("  - pip install -r requirements.txt 실행")
                elif "구조" in test_name:
                    print("  - 누락된 파일들을 프로젝트에 추가")
                elif "단위" in test_name:
                    print("  - workflow_nodes.py의 개별 함수들 점검")
                elif "통합" in test_name:
                    print("  - API 키 설정 및 전체 워크플로우 점검")
    
    return passed_tests == total_tests

def main():
    """메인 테스트 실행 함수"""
    start_time = time.time()
    
    print("🚀 한국 언론사 미디어 프레이밍 분석기 - 전체 테스트 시작")
    print(f"⏰ 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 실행 순서
    tests = [
        ("종속성 검사", run_dependency_check),
        ("코드 구조 검사", run_code_structure_check),
        ("단위 테스트", run_unit_tests),
        ("통합 테스트", run_integration_tests)
    ]
    
    results = []
    
    # 각 테스트 실행
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name} 실행 중...")
        print_separator()
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} 완료")
            else:
                print(f"❌ {test_name} 실패")
                
        except Exception as e:
            print(f"❌ {test_name} 실행 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 보고서 생성
    all_passed = generate_test_report(results)
    
    # 실행 시간 계산
    end_time = time.time()
    execution_time = end_time - start_time
    
    print_separator()
    print(f"⏱️ 총 실행 시간: {execution_time:.2f}초")
    print(f"🏁 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 최종 결과
    if all_passed:
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("✨ 프로젝트가 정상적으로 동작할 준비가 되었습니다.")
        exit_code = 0
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("🔧 위의 권장사항을 참고하여 문제를 해결해주세요.")
        exit_code = 1
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        print("🐛 이 오류를 개발자에게 보고해주세요.")
        sys.exit(1) 