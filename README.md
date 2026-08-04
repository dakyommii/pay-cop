# AI Payment Copilot

설계문서는 [`DESIGN.md`](./DESIGN.md), 단계별 구현 프롬프트는 [`PROMPTS.md`](./PROMPTS.md) 참고.

기술 스택: Next.js(TypeScript) 프론트엔드 + FastAPI(Python) 백엔드 + PostgreSQL.

## 사전 준비

- Python 3.9+
- Node.js 20.4+ (Next.js 15 기준. Next.js 16을 쓰려면 Node 20.9+ 필요)
- 로컬 PostgreSQL (이 프로젝트는 brew `postgresql@16`을 포트 `5433`에서 사용 중이라고 가정)

## DB 준비

```bash
./infra/init_db.sh
```

`payment_copilot` 롤/DB를 (이미 있으면 건너뛰고) 생성한다. 다른 포트를 쓰면
`PGPORT=<port> ./infra/init_db.sh`로 실행.

## Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 필요시 DATABASE_URL / OPENAI_API_KEY 수정
alembic upgrade head    # 스키마 적용
python -m scripts.seed  # 카드 혜택 / 간편결제 이벤트 샘플 데이터 시딩 (idempotent)
uvicorn app.main:app --reload
```

- 앱: http://localhost:8000
- API 문서(Swagger): http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

- http://localhost:3000
- 카드 등록: `/` , 결제 추천: `/payment`

## 시나리오 수동 재현 (DESIGN.md §5)

백엔드가 떠 있고 시드 데이터가 들어간 상태에서:

```bash
curl -s -X POST localhost:8000/payment/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "merchant": "올리브영",
    "category": "뷰티",
    "amount": 48300,
    "cards": [
      { "name": "신한카드", "performance": 430000, "requiredPerformance": 300000 }
    ],
    "payments": ["네이버페이", "카카오페이"]
  }'
```

`recommendedCard: "신한카드"`, `recommendedPayment: "네이버페이"`, `expectedSaving: 5796`이 나와야 한다.
이 시나리오를 포함해 고정된 입력값 여러 개(실적 미충족, 간편결제 없음, 관련 없는 카드 무시 등)를
`backend/tests/test_e2e_scenarios.py`에서 자동으로 검증한다 (`pytest`로 실행).
