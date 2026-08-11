from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.exceptions import NotFoundError
from app.routers import cards, payment, users

app = FastAPI(title="AI Payment Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # Vercel은 배포마다 프리뷰 URL이 바뀌고(pay-cop-<hash>-<team>.vercel.app) 프로덕션
    # 별칭도 붙는다. 이 프로젝트의 모든 vercel.app 서브도메인을 정규식으로 허용한다.
    # 인증/쿠키가 없는 공개 MVP API라 넓게 허용해도 위험이 낮다.
    allow_origin_regex=r"https://pay-cop.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(cards.router)
app.include_router(payment.router)


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.get("/health")
def health():
    return {"status": "ok"}
