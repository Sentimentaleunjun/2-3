# 2학년 3반 노래 신청 웹사이트

Render + Flask로 만든 간단한 노래 신청 웹사이트입니다.

## 기능
- 노래 신청 폼(이름, 노래 제목, 가수, 한마디)
- 최근 신청곡 20개 표시
- 관리자 로그인 후 곡 **선정 체크/해제**, **삭제** 기능
- UptimeRobot 체크용 `/health` 엔드포인트 제공

## 관리자 계정
- 아이디: `sentimentaleunjun`
- 비밀번호: `A292513a!!`

(추가 관리자 계정은 `app.py`의 `ADMIN_USERS`에서 수정 가능)

## 로컬 실행
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Render 배포
1. GitHub 저장소를 Render에 연결
2. `render.yaml` 사용해 배포
3. 배포 주소가 나오면 UptimeRobot에 `https://<your-render-url>/health` 등록
4. 체크 주기를 5분으로 설정

> 참고: 무료 플랜 정책은 변경될 수 있어요.
