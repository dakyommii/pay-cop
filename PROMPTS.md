# AI Payment Copilot — 단계별 구현 프롬프트

이 문서는 `DESIGN.md`(설계문서)를 구현하기 위해 순서대로 실행할 프롬프트 모음입니다.
각 단계는 이전 단계의 산출물을 전제로 하므로 **순서대로** 진행하세요. 각 프롬프트는 Claude Code 등 코딩 에이전트에 그대로 붙여넣어 실행할 수 있도록 작성했습니다.

진행 방식 팁:
- 한 단계 실행 후 빌드/테스트가 통과하는지 확인하고 다음 단계로 넘어가세요.
- 각 프롬프트 하단의 "완료 기준"을 체크리스트처럼 사용하세요.
- 스택은 설계문서 12번(React/Next.js, PostgreSQL, OpenAI)을 따르되, 백엔드는 Spring Boot 대신
  **Python + FastAPI**로 구현합니다(로컬 환경과 개발 속도를 고려해 결정, 2026-08-03). LangChain은
  선택 사항으로 각 단계에서 필요 여부를 판단합니다.

---

## 0단계. 저장소 스캐폴딩 (모노레포 구조 잡기)

```
DESIGN.md에 정의된 "AI Payment Copilot" MVP를 구현할 것이다.
현재 저장소는 비어 있다. 다음과 같이 모노레포 구조를 잡아줘.

- backend/   : Python 3.9 + FastAPI 프로젝트. venv(.venv) + requirements.txt 기반
  (poetry 미설치 환경이므로 pip 사용). dependencies는 fastapi, uvicorn[standard],
  sqlalchemy, alembic, psycopg2-binary, pydantic-settings, python-dotenv.
- frontend/  : Next.js(App Router) + TypeScript 프로젝트. 최소한의 페이지 라우팅만 있는
  상태로 스캐폴딩.
- 로컬 PostgreSQL 16(brew, 이미 실행 중)을 사용한다. Docker는 쓰지 않는다. 개발용 DB/유저를
  생성하는 스크립트(infra/init_db.sh 또는 README 안내)를 만들어줘. DB명은 payment_copilot.
- 루트에 README.md를 만들어 두 프로젝트를 어떻게 각각 실행하는지, DB는 어떻게 준비하는지
  적어줘.

아직 비즈니스 로직은 만들지 말고, 각 프로젝트가 정상적으로 빌드/실행되는 것까지만 확인해줘.
```

**완료 기준**
- `backend`가 venv 안에서 `uvicorn app.main:app --reload`로 기동되고 `/docs`가 뜬다.
- `frontend`가 `npm run dev`로 기본 페이지가 뜬다.
- 로컬 PostgreSQL에 `payment_copilot` DB가 생성되어 있고 backend에서 연결 확인이 된다.

---

## 1단계. 데이터 모델 & DB 스키마 (DESIGN.md §10)

```
DESIGN.md의 10번 "데이터 구조" 섹션을 기준으로 backend에 SQLAlchemy 모델과 Alembic
마이그레이션을 만들어줘.

- User(id, name)
- Card(id, user_id FK, card_name, card_type, current_performance, required_performance)
- Benefit(id, card_name(문자열, Card.card_name과 값으로 매칭 — 특정 사용자의 Card row에
  대한 FK가 아님. 혜택은 "신한카드"라는 카드 상품에 속하고 그 카드를 등록한 모든 사용자가
  공유하는 카탈로그이기 때문), category, discount_rate, condition)
- PaymentEvent(id, payment_type, merchant, benefit_rate)

PaymentRequest는 DB에 저장하는 모델이 아니라 API 요청용 Pydantic 스키마이므로 SQLAlchemy
모델로 만들지 마.
각 모델에 대한 기본 CRUD 함수(레포지토리 계층)도 함께 만들어줘.
Alembic 초기 마이그레이션으로 테이블 생성 스크립트를 작성하고, 로컬 PostgreSQL
(payment_copilot DB)에 대해 마이그레이션이 정상 적용되는지 확인해줘.
```

**완료 기준**
- `alembic upgrade head`가 정상 적용된다.
- 4개 테이블이 생성된다.
- SQLAlchemy 세션으로 각 모델에 대한 기본 CRUD가 동작하는 테스트가 통과한다.

---

## 2단계. 샘플 데이터 시딩 (DESIGN.md §6.2, §6.3)

```
DESIGN.md 6.2 "카드 혜택 DB", 6.3 "간편결제 이벤트 DB"의 예시 데이터를 기준으로
초기 샘플 데이터를 넣어줘.

- Benefit 샘플: 신한카드 - 편의점 10%, 올리브영 10%, 스타벅스 20%, 실적조건 300000원 이상.
  다른 카드사(삼성카드, 현대카드)도 최소 1~2개씩 그럴듯한 샘플 혜택을 추가해줘.
- PaymentEvent 샘플: 네이버페이-올리브영-2%, 카카오페이-맥도날드-5%, 토스페이-편의점-10%.

Alembic의 두 번째 마이그레이션(데이터 삽입 revision)으로 넣거나, 혹은 별도 시딩 스크립트
(예: `backend/scripts/seed.py`) 방식 중 이 프로젝트 구조에 더 맞는 방식을 선택해서 적용해줘.
어떤 방식을 선택했는지와 이유를 알려줘.
```

**완료 기준**
- 앱 기동 후 DB에 Benefit, PaymentEvent 샘플 로우가 존재한다.
- 동일 데이터가 중복 삽입되지 않는다(재기동 시 idempotent).

---

## 3단계. 카드 등록 기능 — 백엔드 (DESIGN.md §6.1, 사용자 시나리오 Step1~2)

```
DESIGN.md 6.1 "사용자 카드 관리" 기능을 backend에 FastAPI REST API로 구현해줘.

- POST /users/{user_id}/cards : 카드 등록 (card_name, card_type, current_performance,
  required_performance)
- GET /users/{user_id}/cards : 등록된 카드 목록 조회
- PATCH /users/{user_id}/cards/{card_id}/performance : 이번 달 실적 업데이트

요청/응답 Pydantic 스키마를 명확히 분리하고, 존재하지 않는 user_id/card_id 요청 시 404를
반환하도록 처리해줘. 라우터/서비스/레포지토리 계층을 분리하고, pytest + TestClient 기반
통합 테스트를 최소 1개 이상 작성해줘.
```

**완료 기준**
- 3개 엔드포인트가 동작하며 테스트가 통과한다.
- 잘못된 입력(음수 금액 등)에 대해 4xx 응답이 온다.

---

## 4단계. 카드 등록 기능 — 프론트엔드 (DESIGN.md §13 ①, 사용자 시나리오 Step1~2)

```
3단계에서 만든 카드 등록 API를 사용하는 프론트엔드 화면을 frontend에 구현해줘.

- 카드 등록 폼: 카드명, 카드 종류, 이번 달 실적, 월 실적 기준 입력
- 등록된 카드 목록 표시 (실적 진행률 같이 보여주면 좋음: currentPerformance /
  requiredPerformance)
- 실적 인라인 수정 가능하게

API 클라이언트는 하나의 모듈로 분리하고, 로딩/에러 상태를 최소한으로 처리해줘.
디자인은 화려할 필요 없고 기능이 명확히 보이는 정도면 충분해.
```

**완료 기준**
- 브라우저에서 카드를 등록하고 목록에 즉시 반영되는 것을 직접 확인한다.
- 실적 수정이 반영된다.

---

## 5단계. 결제 정보 입력 & Rule Engine — 혜택 계산 (DESIGN.md §6.2~6.5, §9)

```
DESIGN.md 9번 "추천 알고리즘"의 흐름을 backend에 Rule Engine(순수 로직, LLM 미사용)으로
구현해줘. 아직 LLM 연동은 하지 마 — 이 단계는 계산 로직만 만든다.

입력: PaymentRequest(merchant, category, amount), 사용자가 등록한 Card 목록, 사용 가능한
간편결제 목록(payments: 문자열 배열)

처리 순서:
1. 각 카드에 대해 merchant/category와 매칭되는 Benefit 조회
2. 실적 조건(requiredPerformance) 충족 여부 확인 → 미충족 카드는 후보에서 제외하거나
   "실적 미충족" 표시로 후보에는 남기되 낮은 우선순위로 처리 (설계 판단은 네가 정하고 이유를
   설명해줘)
3. 각 후보 카드에 대해 discountRate 기반 예상 할인 금액 계산
4. 사용 가능한 간편결제 중 해당 merchant에 매칭되는 PaymentEvent가 있으면 추가 적립액 계산
5. 카드+결제수단 조합별 총 예상 절약액(discountAmount + eventAmount)을 계산해 candidate 리스트
   생성, 절약액 기준 내림차순 정렬

DESIGN.md 11번 API 예시의 요청 형태와 호환되는 내부 서비스 메서드로 구현하고, 5번 시나리오
(올리브영 48,300원, 신한카드 실적 430,000원, 네이버페이/카카오페이 보유)를 단위 테스트로
작성해서 기대값(신한카드+네이버페이, 절약액 약 5,796원 근처)이 나오는지 검증해줘.
```

**완료 기준**
- Rule Engine 단위 테스트가 DESIGN.md의 예시 시나리오와 일치하는 결과를 낸다.
- 실적 미충족 케이스, 매칭 혜택 없는 케이스에 대한 테스트도 추가되어 있다.

---

## 6단계. LLM 연동 — 추천 이유 생성 (DESIGN.md §6.4, §6.6, §8)

```
5단계에서 만든 Rule Engine의 candidate 리스트를 입력받아, OpenAI GPT(LangChain 사용 여부는
네가 판단해 선택하고 이유를 알려줘)로 "추천 이유"를 생성하는 서비스를 backend에 추가해줘.

중요한 제약 (DESIGN.md 8번):
- LLM은 할인 계산이나 이벤트 조회를 하지 않는다. 이미 계산된 candidate(카드명, 할인액,
  적립액, 실적 충족 여부 등)만 프롬프트에 넣고, LLM은 "사용자 친화적 설명 생성"과
  "대안 비교 문구 생성"만 담당한다.
- 프롬프트 템플릿은 DESIGN.md 6.6의 예시 문체("현재 결제에서는 ~가 가장 유리합니다...")를
  참고해서 만들어줘.
- API 키는 환경변수(OPENAI_API_KEY)로 주입하고 절대 코드에 하드코딩하지 마.
- LLM 호출 실패 시 서비스 전체가 죽지 않도록, 계산된 candidate 정보만으로 최소한의
  fallback 설명(rule-based 문자열 조합)을 반환하는 폴백 로직을 넣어줘.

LLM 응답을 모킹한 테스트와, 폴백 로직이 동작하는지 확인하는 테스트를 작성해줘.
```

**완료 기준**
- 정상 시 LLM이 생성한 자연어 추천 이유가 반환된다.
- LLM 호출 실패를 시뮬레이션했을 때 폴백 문자열이 반환되고 서비스가 500을 던지지 않는다.

---

## 7단계. `/payment/recommend` API 통합 (DESIGN.md §11)

```
DESIGN.md 11번에 명시된 API 스펙 그대로 POST /payment/recommend 엔드포인트를 만들어줘.

Request 예시:
{
  "merchant": "올리브영",
  "category": "뷰티",
  "amount": 48300,
  "cards": [{ "name": "신한카드", "performance": 430000 }],
  "payments": ["네이버페이", "카카오페이"]
}

Response 예시:
{
  "recommendedCard": "신한카드",
  "recommendedPayment": "네이버페이",
  "expectedSaving": 5796,
  "reason": "올리브영 업종 할인과 네이버페이 추가 적립을 동시에 받을 수 있습니다."
}

이 엔드포인트는 내부적으로 5단계 Rule Engine → 6단계 LLM 설명 생성을 순서대로 호출하는
오케스트레이션 역할만 한다. 요청 검증(merchant/amount 필수, amount 양수 등)을 추가하고,
DESIGN.md 5번 시나리오를 그대로 재현하는 통합 테스트(라우터 레벨, LLM은 모킹)를 작성해줘.
```

**완료 기준**
- 통합 테스트에서 DESIGN.md 11번 예시와 동일한 요청으로 기대한 형태의 응답이 온다.
- 잘못된 요청에 대해 400이 반환된다.

---

## 8단계. 프론트엔드 — 결제 정보 입력 & AI 추천 결과 화면 (DESIGN.md §13 ②③④⑤)

```
frontend에 다음 화면들을 추가해줘 (DESIGN.md 13번 MVP 화면 흐름, 사용자 시나리오 Step3~5
기준).

- 결제 정보 입력 화면: 매장명, 카테고리, 금액 입력 (등록된 카드/간편결제는 4단계에서 만든
  카드 목록과 사용자가 선택한 간편결제 체크박스에서 가져옴)
- AI 추천 결과 화면: 추천 카드/추천 결제수단을 강조해서 보여줌
- 추천 이유 화면: LLM이 생성한 설명 텍스트 표시
- 절약 금액 비교 화면: 후보 카드별 예상 절약액을 비교하는 간단한 리스트 또는 바 형태 비교
  (막대그래프까지는 필요 없고, 정렬된 리스트 + 강조 표시 정도면 충분)

7단계 /payment/recommend API를 호출하고, 로딩 상태와 에러 상태를 처리해줘.
```

**완료 기준**
- 브라우저에서 카드 등록 → 결제 정보 입력 → 추천 결과까지 이어지는 플로우를 눈으로 확인한다.
- 추천 이유 텍스트와 절약 금액이 화면에 정상 표시된다.

---

## 9단계. End-to-End 시나리오 검증 (DESIGN.md §5)

```
DESIGN.md 5번 "사용자 시나리오"를 그대로 재현하는 End-to-End 테스트(가능하면 backend
통합 테스트 + 필요시 frontend E2E)를 작성해줘.

시나리오:
1. 신한카드, 삼성카드, 현대카드 등록
2. 삼성카드 실적 430,000원 입력
3. 올리브영 48,300원 결제 정보 입력
4. /payment/recommend 호출
5. 응답에 추천 신한카드, 예상 절약 약 4,800~5,796원대(계산 방식에 따라 정확한 값은 5단계
   Rule Engine 구현을 따름), 추천 이유에 "올리브영", "실적" 관련 언급이 포함되는지 검증

테스트 통과 후, README.md에 이 시나리오를 로컬에서 수동으로 재현하는 방법(curl 예시 포함)도
추가해줘.
```

**완료 기준**
- E2E 테스트가 통과한다.
- README에 수동 재현 절차와 curl 예시가 있다.

---

## 10단계 (선택). 향후 확장 훅 포인트 정리 (DESIGN.md §15)

```
DESIGN.md 15번 "향후 확장" 항목(카드사 API 연동, 실시간 이벤트 수집, OCR, 위치 기반 추천,
소비 패턴 기반 추천, 월간 리포트 등)을 지금 구현하지는 말고, 각 항목이 현재 아키텍처의
어느 계층/인터페이스에 연결될지만 짧게 문서화해줘 (예: "카드사 API 연동은 현재 샘플
Benefit 데이터를 채우는 시딩 로직을 외부 API 클라이언트로 교체하는 지점이며, Benefit
Repository 인터페이스는 그대로 유지된다" 같은 식).

코드 변경은 최소화하고, 확장 지점이 애매한 곳이 있다면 지금 인터페이스를 살짝 손봐서
확장에 유리하게만 만들어줘. 불필요한 추상화나 미리 만드는 플러그인 구조는 만들지 마 —
지금 필요한 것 이상으로 설계하지 마.
```

**완료 기준**
- 확장 포인트를 정리한 짧은 문서(예: `docs/future-extensions.md`)가 생긴다.
- 과도한 추상화 없이 기존 코드가 그대로 동작한다.
