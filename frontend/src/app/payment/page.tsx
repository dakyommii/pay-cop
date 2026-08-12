"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Card, RecommendResponse, listCards, recommendPayment } from "@/lib/api";
import { useCurrentUser } from "@/lib/useCurrentUser";

// 시딩된 PaymentEvent 카탈로그와 일치하는 간편결제 목록 (2단계 seed 데이터 기준).
const SIMPLE_PAY_OPTIONS = ["네이버페이", "카카오페이", "토스페이"];

// 업종 -> 매장 목록. 업종은 시딩된 Benefit.category와 일치해 카드 혜택이 매칭되고,
// 올리브영/스타벅스/맥도날드는 매장명 자체가 Benefit·PaymentEvent와도 일치한다.
const CATEGORY_OPTIONS: { label: string; merchants: string[] }[] = [
  { label: "뷰티", merchants: ["올리브영", "시코르"] },
  { label: "편의점", merchants: ["CU", "GS25", "세븐일레븐", "이마트24"] },
  { label: "카페", merchants: ["스타벅스", "이디야", "투썸플레이스"] },
  { label: "주유", merchants: ["GS칼텍스", "SK에너지", "현대오일뱅크"] },
  { label: "온라인쇼핑", merchants: ["쿠팡", "11번가", "G마켓"] },
  { label: "영화", merchants: ["CGV", "롯데시네마", "메가박스"] },
  { label: "배달앱", merchants: ["배달의민족", "요기요", "쿠팡이츠"] },
  { label: "패스트푸드", merchants: ["맥도날드", "버거킹", "롯데리아"] },
];
const CUSTOM_OPTION = "__custom__";

export default function PaymentPage() {
  const { userId, error: userError } = useCurrentUser();
  const [cards, setCards] = useState<Card[]>([]);
  const [merchant, setMerchant] = useState("");
  const [category, setCategory] = useState("");
  const [useCustomCategory, setUseCustomCategory] = useState(false);
  const [useCustomMerchant, setUseCustomMerchant] = useState(false);
  const [amount, setAmount] = useState<number>(0);
  const [selectedPayments, setSelectedPayments] = useState<string[]>([]);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const merchantOptions = CATEGORY_OPTIONS.find((c) => c.label === category)?.merchants ?? [];

  const handleCategoryChange = (value: string) => {
    setMerchant("");
    setUseCustomMerchant(false);
    if (value === CUSTOM_OPTION) {
      setUseCustomCategory(true);
      setCategory("");
    } else {
      setUseCustomCategory(false);
      setCategory(value);
    }
  };

  const handleMerchantChange = (value: string) => {
    if (value === CUSTOM_OPTION) {
      setUseCustomMerchant(true);
      setMerchant("");
    } else {
      setUseCustomMerchant(false);
      setMerchant(value);
    }
  };

  useEffect(() => {
    if (userId) {
      listCards(userId).then(setCards).catch((e) => setError((e as Error).message));
    }
  }, [userId]);

  const togglePayment = (payment: string) => {
    setSelectedPayments((prev) =>
      prev.includes(payment) ? prev.filter((p) => p !== payment) : [...prev, payment]
    );
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (cards.length === 0) {
      setError("먼저 카드를 등록해주세요.");
      return;
    }

    setLoading(true);
    try {
      const response = await recommendPayment({
        merchant,
        category,
        amount,
        cards: cards.map((c) => ({
          name: c.card_name,
          performance: c.current_performance,
          requiredPerformance: c.required_performance,
        })),
        payments: selectedPayments,
      });
      setResult(response);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <nav className="page-nav">
        <Link href="/">← 카드 등록으로</Link>
      </nav>
      <h1 className="page-title">결제 정보 입력</h1>
      <p className="page-subtitle">매장과 금액을 입력하면 등록된 카드 기준으로 가장 유리한 조합을 추천해드려요.</p>

      {userError && <p className="msg-error" style={{ marginBottom: 12 }}>사용자 초기화 실패: {userError}</p>}
      {error && <p className="msg-error" style={{ marginBottom: 12 }}>{error}</p>}
      {cards.length === 0 && !userError && (
        <p className="msg-notice" style={{ marginBottom: 12 }}>
          등록된 카드가 없습니다. <Link href="/" style={{ textDecoration: "underline" }}>카드를 먼저 등록</Link>해주세요.
        </p>
      )}

      <form onSubmit={handleSubmit} className="form">
        <div className="field">
          <select
            value={useCustomCategory ? CUSTOM_OPTION : category}
            onChange={(e) => handleCategoryChange(e.target.value)}
            required
          >
            <option value="" disabled>
              업종 선택
            </option>
            {CATEGORY_OPTIONS.map((c) => (
              <option key={c.label} value={c.label}>
                {c.label}
              </option>
            ))}
            <option value={CUSTOM_OPTION}>기타 (직접 입력)</option>
          </select>
          {useCustomCategory && (
            <input
              type="text"
              placeholder="업종 입력 (예: 뷰티)"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              required
            />
          )}
        </div>
        <div className="field">
          {useCustomCategory ? (
            <input
              type="text"
              placeholder="매장 입력 (예: 올리브영)"
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              required
            />
          ) : (
            <>
              <select
                value={useCustomMerchant ? CUSTOM_OPTION : merchant}
                onChange={(e) => handleMerchantChange(e.target.value)}
                disabled={!category}
                required
              >
                <option value="" disabled>
                  {category ? "매장 선택" : "먼저 업종을 선택하세요"}
                </option>
                {merchantOptions.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
                {category && <option value={CUSTOM_OPTION}>기타 (직접 입력)</option>}
              </select>
              {useCustomMerchant && (
                <input
                  type="text"
                  placeholder="매장 입력"
                  value={merchant}
                  onChange={(e) => setMerchant(e.target.value)}
                  required
                />
              )}
            </>
          )}
        </div>
        <div className="field">
          <label className="field-label">결제 금액</label>
          <input
            type="number"
            min={1}
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            required
          />
        </div>

        <div className="checkbox-group">
          {SIMPLE_PAY_OPTIONS.map((payment) => (
            <label key={payment} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedPayments.includes(payment)}
                onChange={() => togglePayment(payment)}
              />
              {payment}
            </label>
          ))}
        </div>

        <button type="submit" className="btn-primary" disabled={!userId || loading}>
          {loading ? "분석 중..." : "AI 추천 받기"}
        </button>
      </form>

      {result && (
        <section style={{ display: "flex", flexDirection: "column", gap: 24, marginTop: 28 }}>
          <div className="result-highlight">
            <div className="result-headline">
              {result.recommendedCard}
              {result.recommendedPayment && ` + ${result.recommendedPayment}`}
            </div>
            <div className="result-saving">예상 절약 {result.expectedSaving.toLocaleString()}원</div>
          </div>

          <div>
            <h3 className="section-title" style={{ marginTop: 0 }}>추천 이유</h3>
            <p style={{ fontSize: 14, lineHeight: 1.6 }}>{result.reason}</p>
          </div>

          <div>
            <h3 className="section-title" style={{ marginTop: 0 }}>절약 금액 비교</h3>
            <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 6 }}>
              {result.candidates.map((c, i) => {
                const isTop = c.cardName === result.recommendedCard && c.paymentType === result.recommendedPayment;
                const maxSaving = result.candidates[0]?.expectedSaving || 1;
                const ratio = maxSaving > 0 ? Math.max(0, c.expectedSaving / maxSaving) : 0;
                return (
                  <li key={i} className={`candidate-row${isTop ? " candidate-row--top" : ""}`}>
                    <div className="candidate-row-line">
                      <span>
                        {c.cardName}
                        {c.paymentType && ` + ${c.paymentType}`}
                        {!c.performanceMet && " (실적 미충족)"}
                      </span>
                      <strong>{c.expectedSaving.toLocaleString()}원</strong>
                    </div>
                    <div className="progress-track">
                      <div
                        className={`progress-fill${isTop ? "" : " progress-fill--accent"}`}
                        style={{ width: `${ratio * 100}%` }}
                      />
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}
