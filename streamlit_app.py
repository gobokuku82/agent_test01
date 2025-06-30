import streamlit as st
import pandas as pd
from streaming_workflow import StreamingWorkflow
import json
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="실시간 언론사 프레이밍 분석기",
    page_icon="⚡",
    layout="wide"
)

def get_api_keys():
    """
    환경에 따라 API 키를 안전하게 가져오는 함수
    """
    try:
        # Streamlit Cloud에서는 secrets에서 직접 가져오기
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            naver_client_id = st.secrets.get("NAVER_CLIENT_ID", "")
            naver_client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
            openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
        else:
            # 로컬에서는 환경변수 또는 기본값 사용
            naver_client_id = os.getenv("NAVER_CLIENT_ID", "")
            naver_client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
            openai_api_key = os.getenv("OPENAI_API_KEY", "")
            
        return naver_client_id, naver_client_secret, openai_api_key
        
    except Exception as e:
        # 모든 예외 상황에서 빈 문자열 반환
        return "", "", ""

def main():
    st.title("⚡ 실시간 언론사 미디어 프레이밍 분석기")
    st.markdown("**LangGraph 기반 실시간 추적 & 단계별 피드백 시스템**")
    st.markdown("---")
    
    # 사이드바 - 워크플로우 정보
    with st.sidebar:
        st.header("📊 실시간 추적")
        
        workflow_status = st.empty()
        step_details = st.empty()
        
        st.markdown("---")
        st.markdown("""
        **⚡ 실시간 기능:**
        - 단계별 실시간 진행 상황
        - 각 단계 결과 즉시 표시
        - 상세한 작업 로그
        - 중간 결과 미리보기
        """)
    
    # 메인 컨텐츠
    st.header("🔍 키워드 기반 실시간 분석")
    
    # 키워드 입력
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword = st.text_input(
            "분석할 키워드를 입력하세요:",
            placeholder="예: 대통령, 경제정책, 교육개혁, 북한, 환경정책 등",
            help="AI가 실시간으로 단계별 분석을 수행합니다."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("⚡ 실시간 분석 시작", type="primary", use_container_width=True)
    
    # API 키 확인
    naver_client_id, naver_client_secret, openai_api_key = get_api_keys()
    
    if not naver_client_id or not naver_client_secret or not openai_api_key:
        st.error("⚠️ API 키가 설정되지 않았습니다.")
        
        # 환경 감지
        is_cloud = hasattr(st, 'secrets') or 'streamlit.io' in os.environ.get('STREAMLIT_SERVER_URL', '')
        
        if is_cloud:
            # Streamlit Cloud 환경
            with st.expander("🔧 Streamlit Cloud Secrets 설정", expanded=True):
                st.markdown("""
                **Streamlit Cloud에서 Secrets 설정 방법:**
                
                1. **앱 관리 페이지**에서 본 앱 선택
                2. **⚙️ Settings** 클릭  
                3. **🔐 Secrets** 탭 선택
                4. **텍스트박스에 다음 입력:**
                
                ```
                NAVER_CLIENT_ID = "your_naver_client_id"
                NAVER_CLIENT_SECRET = "your_naver_client_secret"
                OPENAI_API_KEY = "your_openai_api_key"
                ```
                
                5. **💾 Save** 클릭 → 앱 자동 재시작
                """)
        else:
            # 로컬 환경
            with st.expander("🛠️ 로컬 개발 환경 설정", expanded=True):
                st.markdown("""
                **로컬에서 API 키 설정 방법:**
                
                **방법 1: 환경변수 설정**
                ```bash
                export NAVER_CLIENT_ID="your_client_id"
                export NAVER_CLIENT_SECRET="your_client_secret"  
                export OPENAI_API_KEY="your_openai_key"
                ```
                
                **방법 2: .streamlit/secrets.toml 파일**
                ```toml
                [default]
                NAVER_CLIENT_ID = "your_client_id"
                NAVER_CLIENT_SECRET = "your_client_secret"
                OPENAI_API_KEY = "your_openai_key"
                ```
                """)
        
        st.info("🔑 **API 키 발급**: [네이버 개발자센터](https://developers.naver.com) | [OpenAI Platform](https://platform.openai.com/api-keys)")
        return
    
    # API 키가 정상적으로 설정된 경우
    st.success("✅ API 키가 정상적으로 설정되었습니다.")
    
    # 분석 실행
    if analyze_button and keyword.strip():
        run_streaming_analysis(keyword.strip(), workflow_status, step_details)
    elif analyze_button:
        st.warning("키워드를 입력해주세요.")

def run_streaming_analysis(keyword: str, workflow_status, step_details):
    """
    실시간 스트리밍 분석 실행
    """
    
    # 메인 진행 상황 표시 영역
    st.markdown("---")
    st.header("⚡ 실시간 분석 진행")
    
    # 진행 상황 컨테이너들
    main_progress = st.progress(0)
    status_container = st.container()
    
    # 단계별 결과 표시 영역
    results_container = st.container()
    step_results = {}
    
    # 스트리밍 워크플로우 실행
    streaming_workflow = StreamingWorkflow()
    
    with status_container:
        status_text = st.empty()
        current_step_info = st.empty()
    
    # 실시간 스트리밍 실행
    for update in streaming_workflow.run_streaming_analysis(keyword):
        
        # 진행률 업데이트
        main_progress.progress(update["progress"])
        
        # 상태 메시지 업데이트
        status_text.markdown(f"### {update['message']}")
        
        # 사이드바 상태 업데이트
        workflow_status.markdown(f"**현재 진행률:** {update['progress']}%")
        
        if update["type"] == "start":
            current_step_info.info("🚀 분석을 시작합니다...")
            step_details.markdown("**준비 중...**")
            
        elif update["type"] == "step_start":
            current_step_info.info(f"📋 {update['message']}")
            step_details.markdown(f"**단계:** {update['step']}")
            
        elif update["type"] == "step_running":
            current_step_info.warning(f"⚙️ {update['message']}")
            
        elif update["type"] == "step_complete":
            current_step_info.success(f"✅ {update['message']}")
            
            # 단계별 결과 저장 및 표시
            step_results[update["step"]] = update["step_data"]
            display_step_result(results_container, update["step"], update["step_data"], update["state"])
            
            # 사이드바에 상세 정보 표시
            step_details.json(update["step_data"])
            
        elif update["type"] == "step_error":
            current_step_info.error(f"❌ {update['message']}")
            
        elif update["type"] == "complete":
            current_step_info.balloons()
            current_step_info.success("🎉 모든 분석이 완료되었습니다!")
            
            # 최종 결과 표시
            display_final_results(keyword, update["state"])
            
        # UI 업데이트를 위한 짧은 대기
        time.sleep(0.1)

def display_step_result(container, step_name: str, step_data: dict, state: dict):
    """단계별 결과를 실시간으로 표시"""
    
    with container:
        if step_name == "decide_publishers":
            st.subheader("🎯 선택된 언론사")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("선택된 언론사 수", step_data.get("total_count", 0))
                
            with col2:
                publishers = step_data.get("selected_publishers", [])
                if publishers:
                    st.write("**선택된 언론사:**")
                    for pub in publishers:
                        st.write(f"• {pub}")
                        
        elif step_name == "collect_articles":
            st.subheader("📰 기사 수집 결과")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 수집 기사", step_data.get("total_articles", 0))
            with col2:
                sources = step_data.get("data_sources", {})
                st.metric("데이터 소스", len(sources))
            with col3:
                publishers_with_articles = len([p for p, count in step_data.get("articles_by_publisher", {}).items() if count > 0])
                st.metric("기사 수집 언론사", publishers_with_articles)
            
            # 언론사별 수집 현황
            articles_by_pub = step_data.get("articles_by_publisher", {})
            if articles_by_pub:
                st.write("**언론사별 수집 현황:**")
                df = pd.DataFrame(list(articles_by_pub.items()), columns=["언론사", "기사 수"])
                st.dataframe(df, use_container_width=True)
                
        elif step_name == "analyze_articles":
            st.subheader("🔍 기사 분석 결과")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("분석 완료 기사", step_data.get("analyzed_count", 0))
                
            with col2:
                sentiment_dist = step_data.get("sentiment_distribution", {})
                if sentiment_dist:
                    st.write("**감정 분포:**")
                    for sentiment, count in sentiment_dist.items():
                        st.write(f"• {sentiment}: {count}개")
                        
        elif step_name == "compare_analysis":
            st.subheader("📊 비교 분석 결과")
            
            analysis_points = step_data.get("analysis_points", 0)
            st.metric("분석 관점", analysis_points)
            
            comparison = step_data.get("comparison_analysis", {})
            if comparison:
                st.write("**주요 분석 관점:**")
                for key, value in comparison.items():
                    if value and value != "분석 불가":
                        st.write(f"• **{key.replace('_', ' ').title()}:** {value[:100]}...")
                        
        elif step_name == "generate_report":
            st.subheader("📄 보고서 생성 결과")
            
            report_length = step_data.get("report_length", 0)
            st.metric("보고서 길이", f"{report_length:,}자")
            
            preview = step_data.get("report_preview", "")
            if preview:
                st.write("**보고서 미리보기:**")
                st.text(preview)
                
        elif step_name == "suggest_usage":
            st.subheader("💡 활용 방안 제안")
            
            suggestion_count = step_data.get("suggestion_count", 0)
            st.metric("제안된 활용 방안", suggestion_count)
            
            suggestions = step_data.get("usage_suggestions", [])
            if suggestions:
                st.write("**주요 활용 방안:**")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    st.write(f"{i}. {suggestion[:100]}...")

def display_final_results(keyword: str, state: dict):
    """최종 분석 결과 표시"""
    
    st.markdown("---")
    st.header("🎯 최종 분석 결과")
    
    # 결과 요약 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "선택된 언론사", 
            len(state.get("selected_publishers", [])),
            help="AI가 자동 선택한 언론사 수"
        )
    
    with col2:
        total_articles = sum(len(articles) for articles in state.get("analyzed_articles", {}).values())
        st.metric(
            "분석된 기사", 
            total_articles,
            help="수집되어 분석된 총 기사 수"
        )
    
    with col3:
        comparison_keys = len(state.get("comparison_analysis", {}))
        st.metric(
            "비교 관점", 
            comparison_keys,
            help="언론사 간 비교된 분석 관점 수"
        )
    
    with col4:
        usage_suggestions = len(state.get("usage_suggestions", []))
        st.metric(
            "활용 방안", 
            usage_suggestions,
            help="AI가 제안한 활용 방안 수"
        )
    
    # 탭으로 상세 결과 표시
    tab1, tab2, tab3 = st.tabs(["📰 상세 기사", "📄 최종 보고서", "💡 활용 방안"])
    
    with tab1:
        display_detailed_articles(state.get("analyzed_articles", {}))
    
    with tab2:
        final_report = state.get("final_report", "")
        if final_report:
            st.markdown(final_report)
            
            st.download_button(
                label="📥 보고서 다운로드 (Markdown)",
                data=final_report,
                file_name=f"언론사_분석_보고서_{keyword}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    with tab3:
        usage_suggestions = state.get("usage_suggestions", [])
        if usage_suggestions:
            for i, suggestion in enumerate(usage_suggestions, 1):
                st.write(f"**{i}.** {suggestion}")
                
            st.download_button(
                label="📥 전체 분석 결과 다운로드 (JSON)",
                data=json.dumps(state, ensure_ascii=False, indent=2),
                file_name=f"언론사_분석_결과_{keyword}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def display_detailed_articles(analyzed_articles: dict):
    """상세 기사 정보 표시"""
    
    if not analyzed_articles:
        st.info("분석된 기사가 없습니다.")
        return
        
    for publisher, articles in analyzed_articles.items():
        if articles:
            st.write(f"### 📰 {publisher}")
            
            for i, article in enumerate(articles, 1):
                with st.expander(f"{i}. {article.get('title', 'N/A')[:60]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📝 요약:** {article.get('summary', 'N/A')}")
                        st.write(f"**🎭 어조:** {article.get('tone', 'N/A')}")
                        st.write(f"**💭 감정:** {article.get('sentiment', 'N/A')}")
                    
                    with col2:
                        st.write(f"**🎯 주요 논점:** {article.get('main_argument', 'N/A')}")
                        keywords = article.get('keywords', [])
                        if keywords:
                            st.write(f"**🏷️ 키워드:** {', '.join(keywords)}")
                        st.write(f"**📊 데이터 소스:** {article.get('source', 'N/A')}")
                        
                    st.write(f"**🔗 링크:** {article.get('link', 'N/A')}")

if __name__ == "__main__":
    main() 