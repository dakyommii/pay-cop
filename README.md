# AI Payment Copilot

AI 기반 실시간 결제 및 혜택 추천 플랫폼. 사용자가 등록한 카드의 혜택·실적 조건과
간편결제 이벤트를 종합해, 결제 직전에 가장 유리한 결제수단과 예상 절약 금액을
추천 이유와 함께 알려주는 MVP입니다.

전체 설계는 [`DESIGN.md`](./DESIGN.md), 이를 구현하기 위해 단계별로 사용한 프롬프트는
[`PROMPTS.md`](./PROMPTS.md), MVP 범위 밖 기능들이 지금 구조 어디에 연결되는지는
[`docs/future-extensions.md`](./docs/future-extensions.md)에 정리되어 있습니다.

## 무엇을 하는가

1. 보유 카드와 이번 달 카드 실적을 등록한다.
2. 결제할 매장/업종/금액을 입력한다.
3. Rule Engine이 카드 혜택 · 실적 조건 충족 여부 · 간편결제 이벤트를 계산해 카드×간편결제
   조합별 예상 절약액을 산출한다.
4. LLM이 계산된 결과를 바탕으로(직접 계산은 하지 않음) 사람이 읽기 쉬운 추천 이유를 생성한다.
5. 화면에서 추천 카드/결제수단, 예상 절약액, 추천 이유, 다른 후보와의 절약액 비교를 보여준다.

DESIGN.md §5의 예시(올리브영 48,300원 결제, 신한카드 실적 430,000/300,000, 네이버페이 보유)를
넣으면 "신한카드 + 네이버페이, 예상 절약 5,796원"이 그대로 재현됩니다.

## MVP 범위

포함: 카드 등록, 카드 실적 입력, 간편결제 등록, 결제 정보 입력, AI 추천, 예상 절약 금액 계산,
추천 이유 설명.

제외 (DESIGN.md §4): 실제 카드사 API 연동, OCR 영수증 인식, 위치 기반 자동 감지, 음성 AI,
실시간 푸시 알림, 해외 결제 추천. → 각 항목이 왜/어디서 확장 가능한지는
[`docs/future-extensions.md`](./docs/future-extensions.md) 참고.

## 기술 스택

- **Frontend**: Next.js 15 (App Router, TypeScript)
- **Backend**: FastAPI (Python), SQLAlchemy, Alembic
- **DB**: PostgreSQL
- **AI**: OpenAI API (키가 없으면 규칙 기반 폴백 문구로 자동 대체 — 서비스가 절대 깨지지 않음)

## 프로젝트 구조

```
backend/
  app/
    models/        # SQLAlchemy 모델 (User, Card, Benefit, PaymentEvent)
    repositories/   # DB CRUD
    services/       # rule_engine(계산) / llm_explainer(설명) / *_service(오케스트레이션)
    routers/        # FastAPI 엔드포인트
    schemas/        # Pydantic 요청/응답 스키마
  scripts/seed.py    # 카드 혜택·간편결제 이벤트 샘플 데이터 시딩 (idempotent)
  alembic/           # DB 마이그레이션
  tests/             # pytest (모델 CRUD / API / Rule Engine / LLM 폴백 / E2E 시나리오)
frontend/
  src/app/           # 카드 등록(`/`), 결제 추천(`/payment`) 화면
  src/lib/           # API 클라이언트, 임시 사용자 훅
infra/init_db.sh      # 로컬 PostgreSQL에 payment_copilot 롤/DB 생성
docs/future-extensions.md
```

## 사전 준비

- Python 3.9+
- Node.js 20.4+ (Next.js 15 기준. Next.js 16을 쓰려면 Node 20.9+ 필요)
- 로컬 PostgreSQL (이 프로젝트는 brew `postgresql@16`을 포트 `5433`에서 사용 중이라고 가정)

## 시작하기

### 1. DB 준비

```bash
./infra/init_db.sh
```

`payment_copilot` 롤/DB를 (이미 있으면 건너뛰고) 생성한다. 다른 포트를 쓰면
`PGPORT=<port> ./infra/init_db.sh`로 실행.

### 2. Backend (FastAPI)

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

`OPENAI_API_KEY`를 비워두면 LLM 호출 없이 규칙 기반 추천 이유 문구가 그대로 반환됩니다.

### 3. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

- http://localhost:3000
- 카드 등록: `/` , 결제 추천: `/payment`

## API 예시

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

```json
{
  "recommendedCard": "신한카드",
  "recommendedPayment": "네이버페이",
  "expectedSaving": 5796,
  "reason": "현재 결제에서는 신한카드가 가장 유리합니다. ...",
  "candidates": [
    { "cardName": "신한카드", "paymentType": "네이버페이", "expectedSaving": 5796, "performanceMet": true },
    { "cardName": "신한카드", "paymentType": "카카오페이", "expectedSaving": 4830, "performanceMet": true }
  ]
}
```

`recommendedCard`/`recommendedPayment`/`expectedSaving`/`reason`은 DESIGN.md §11 스펙 그대로이고,
`candidates`는 프론트엔드의 절약 금액 비교 화면을 위한 추가 필드입니다.

## 테스트

```bash
cd backend
source .venv/bin/activate
pytest
```

- `test_models_crud.py` / `test_cards_api.py`: 모델·카드 등록 API
- `test_rule_engine.py`: 혜택 계산 로직 (실적 미충족, 혜택 없음, 결제수단 없음 등)
- `test_llm_explainer.py`: LLM 성공/실패 시 폴백 동작
- `test_payment_recommend_api.py`, `test_e2e_scenarios.py`: `/payment/recommend` 통합 및
  DESIGN.md 시나리오 고정값 회귀 테스트
