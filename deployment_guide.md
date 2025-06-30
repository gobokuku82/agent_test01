# 🚀 Streamlit Cloud 배포 가이드

## 📋 배포 전 체크리스트

- [ ] GitHub 리포지토리 생성 및 코드 푸시
- [ ] 네이버 검색 API 키 발급
- [ ] OpenAI API 키 발급  
- [ ] requirements.txt 확인

## 🌐 Streamlit Cloud 배포 단계

### 1단계: Streamlit Cloud 접속
1. **https://share.streamlit.io** 접속
2. GitHub 계정으로 로그인

### 2단계: 새 앱 생성
1. **"New app"** 버튼 클릭
2. **Repository** 선택: `your-username/repository-name`
3. **Branch**: `main` (기본값)
4. **Main file path**: `streamlit_app.py`
5. **App URL** 설정 (선택사항)

### 3단계: 배포 시작
1. **"Deploy!"** 버튼 클릭
2. 자동 배포 시작 (2-3분 소요)

### 4단계: API 키 설정 (중요!)
배포 완료 후 **반드시** API 키를 설정해야 합니다:

1. **앱 대시보드에서 앱 선택**
2. **우측 상단 ⚙️ Settings 클릭**
3. **Secrets 탭 선택**
4. **다음 내용을 텍스트박스에 입력:**

```toml
NAVER_CLIENT_ID = "실제_네이버_클라이언트_ID"
NAVER_CLIENT_SECRET = "실제_네이버_클라이언트_시크릿"
OPENAI_API_KEY = "실제_OpenAI_API_키"
```

5. **"Save" 버튼 클릭**
6. 앱이 자동으로 재시작됩니다 (30초 소요)

## 🔑 API 키 발급 상세 가이드

### 🔍 네이버 검색 API 
1. **https://developers.naver.com/apps/#/register** 접속
2. **"애플리케이션 등록"** 클릭
3. **애플리케이션 정보 입력:**
   - 애플리케이션 이름: `언론사 프레이밍 분석기`
   - 사용 API: **검색** 선택
   - 환경: **WEB** 선택
   - 서비스 URL: Streamlit 앱 URL 입력
4. **등록 완료 후 Client ID, Client Secret 복사**

### 🤖 OpenAI API
1. **https://platform.openai.com/api-keys** 접속
2. **"Create new secret key"** 클릭
3. **이름 설정**: `streamlit-news-analyzer`
4. **키 생성 후 즉시 복사** (다시 볼 수 없음!)
5. **결제 정보 등록** (사용량에 따라 과금)

## ⚡ 실시간 모니터링

### 배포 상태 확인
- **앱 대시보드**: 실행 상태, 로그, 메트릭 확인
- **앱 URL**: 실제 서비스 접속
- **GitHub 연동**: 코드 푸시시 자동 재배포

### 문제 해결
**앱이 실행되지 않는 경우:**
1. **Logs 탭**에서 오류 메시지 확인
2. **Secrets 설정** 재확인
3. **requirements.txt** 패키지 버전 확인

**API 키 오류가 나는 경우:**
1. Secrets 탭에서 키 값 재확인
2. 따옴표나 공백 제거
3. 네이버/OpenAI 콘솔에서 키 상태 확인

## 🔄 업데이트 및 관리

### 코드 업데이트
```bash
git add .
git commit -m "업데이트 내용"
git push origin main
```
→ **자동으로 Streamlit Cloud에 재배포됩니다!**

### 설정 변경
- **Secrets**: 언제든지 앱 설정에서 수정 가능
- **도메인**: Custom domain 설정 가능 (유료)
- **리소스**: 앱 사용량에 따라 자동 스케일링

## 📊 사용량 모니터링

### Streamlit Cloud 제한사항
- **무료 계정**: 3개 앱, 1GB 메모리
- **API 호출**: 네이버 25,000건/일, OpenAI 사용량 과금
- **동시 접속**: 제한 없음 (리소스 내에서)

### 비용 최적화
- **OpenAI API**: GPT-3.5-turbo 사용 (저렴)
- **캐싱**: 중복 분석 방지
- **제한**: 언론사당 3개 기사로 제한

## 🎉 배포 완료!

✅ **성공적으로 배포되면:**
- 전세계 어디서나 앱 접속 가능
- 실시간 언론사 프레이밍 분석 서비스 운영
- GitHub 푸시만으로 자동 업데이트

🔗 **앱 URL 공유:**
- 가족, 친구, 동료들과 공유
- 소셜 미디어에 홍보
- 포트폴리오에 추가

---

**🆘 도움이 필요하면:**
- Streamlit 공식 문서: https://docs.streamlit.io/streamlit-cloud
- 커뮤니티 포럼: https://discuss.streamlit.io 