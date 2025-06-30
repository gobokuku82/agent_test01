# Streamlit Secrets 설정 예시
# 실제 사용시에는 .streamlit/secrets.toml 파일을 생성하고 아래 내용을 입력하세요

"""
.streamlit/secrets.toml 파일 내용 예시:

[default]
NAVER_CLIENT_ID = "your_naver_client_id_here"
NAVER_CLIENT_SECRET = "your_naver_client_secret_here"
OPENAI_API_KEY = "your_openai_api_key_here"

설정 방법:
1. 프로젝트 루트에 .streamlit 폴더 생성
2. .streamlit/secrets.toml 파일 생성
3. 위 형식으로 API 키 입력 (따옴표 필수)
4. 앱 재시작

보안 주의사항:
- secrets.toml 파일은 절대 git에 커밋하지 마세요
- .gitignore에 .streamlit/ 폴더 추가 권장
- Streamlit Cloud 배포시에는 웹 인터페이스에서 secrets 설정

API 키 발급 방법:
- 네이버 API: https://developers.naver.com/apps/#/register
- OpenAI API: https://platform.openai.com/api-keys
""" 