# Streamlit Cloud 배포용 Secrets 설정 가이드

"""
🚀 Streamlit Cloud 배포시 Secrets 설정 방법:

1. Streamlit Cloud 앱 대시보드에서 본 앱 선택
2. Settings → Secrets 메뉴 클릭  
3. 다음 내용을 텍스트박스에 입력:

NAVER_CLIENT_ID = "실제_네이버_클라이언트_ID"
NAVER_CLIENT_SECRET = "실제_네이버_클라이언트_시크릿"
OPENAI_API_KEY = "실제_OpenAI_API_키"

4. Save 클릭하면 앱이 자동으로 재시작됩니다.

---

🛠️ 로컬 개발용 설정 (.streamlit/secrets.toml):

[default]
NAVER_CLIENT_ID = "your_naver_client_id"
NAVER_CLIENT_SECRET = "your_naver_client_secret"
OPENAI_API_KEY = "your_openai_api_key"

---

📚 API 키 발급 안내:

🔍 네이버 검색 API:
- https://developers.naver.com/apps/#/register
- 애플리케이션 등록 후 검색 API 선택
- Client ID와 Client Secret 발급

🤖 OpenAI API:
- https://platform.openai.com/api-keys
- Create new secret key 클릭하여 발급
- 사용량에 따라 요금 부과됨 (주의)

---

🔒 보안 주의사항:

✅ Streamlit Cloud의 Secrets는 암호화되어 안전하게 저장됩니다
✅ 환경변수로 앱에 주입되어 코드에서 st.secrets로 접근 가능
✅ GitHub 리포지토리에는 절대 API 키를 커밋하지 마세요
✅ .gitignore에 .streamlit/secrets.toml 추가 필수

---

🌐 배포 준비사항:

1. GitHub 리포지토리에 코드 푸시
2. Streamlit Cloud에서 리포지토리 연결
3. 위 방법으로 Secrets 설정
4. 자동 배포 완료!
""" 