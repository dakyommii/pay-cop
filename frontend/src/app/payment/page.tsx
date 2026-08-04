"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Card, RecommendResponse, listCards, recommendPayment } from "@/lib/api";
import { useCurrentUser } from "@/lib/useCurrentUser";

// 시딩된 PaymentEvent 카탈로그와 일치하는 간편결제 목록 (2단계 seed 데이터 기준).
const SIMPLE_PAY_OPTIONS = ["네이버페이", "카카오페이", "토스페이"];

export default function PaymentPage() {
  const { userId, error: userError } = useCurrentUser();
  const [cards, setCards] = useState<Card[]>([]);
  const [merchant, setMerchant] = useState("");
  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState<number>(0);
  const [selectedPayments, setSelectedPayments] = useState<string[]>([]);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
    <main style={{ maxWidth: 480, margin: "40px auto", padding: "0 16px", fontFamily: "sans-serif" }}>
      <p style={{ marginBottom: 16 }}>
        <Link href="/">← 카드 등록으로</Link>
      </p>
      <h1>결제 정보 입력</h1>

      {userError && <p style={{ color: "crimson" }}>사용자 초기화 실패: {userError}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {cards.length === 0 && !userError && (
        <p style={{ color: "#a15c00" }}>
          등록된 카드가 없습니다. <Link href="/">카드를 먼저 등록</Link>해주세요.
        </p>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 24 }}>
        <input
          placeholder="매장 (예: 올리브영)"
          value={merchant}
          onChange={(e) => setMerchant(e.target.value)}
          required
        />
        <input
          placeholder="업종 (예: 뷰티)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          required
        />
        <label style={{ fontSize: 14 }}>
          결제 금액
          <input
            type="number"
            min={1}
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            required
          />
        </label>

        <fieldset style={{ border: "1px solid #ddd", borderRadius: 8, padding: 8 }}>
          <legend style={{ fontSize: 13 }}>보유 간편결제</legend>
          {SIMPLE_PAY_OPTIONS.map((payment) => (
            <label key={payment} style={{ marginRight: 12, fontSize: 14 }}>
              <input
                type="checkbox"
                checked={selectedPayments.includes(payment)}
                onChange={() => togglePayment(payment)}
              />{" "}
              {payment}
            </label>
          ))}
        </fieldset>

        <button type="submit" disabled={!userId || loading}>
          {loading ? "분석 중..." : "AI 추천 받기"}
        </button>
      </form>

      {result && (
        <section style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ border: "2px solid #2f9e44", borderRadius: 8, padding: 12 }}>
            <h2 style={{ margin: "0 0 8px" }}>AI 추천 결과</h2>
            <div style={{ fontSize: 20, fontWeight: "bold" }}>
              {result.recommendedCard}
              {result.recommendedPayment && ` + ${result.recommendedPayment}`}
            </div>
            <div style={{ color: "#2f9e44", fontWeight: "bold", marginTop: 4 }}>
              예상 절약: {result.expectedSaving.toLocaleString()}원
            </div>
          </div>

          <div>
            <h3>추천 이유</h3>
            <p>{result.reason}</p>
          </div>

          <div>
            <h3>절약 금액 비교</h3>
            <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 6 }}>
              {result.candidates.map((c, i) => {
                const isTop = c.cardName === result.recommendedCard && c.paymentType === result.recommendedPayment;
                const maxSaving = result.candidates[0]?.expectedSaving || 1;
                const ratio = maxSaving > 0 ? Math.max(0, c.expectedSaving / maxSaving) : 0;
                return (
                  <li
                    key={i}
                    style={{
                      padding: 8,
                      borderRadius: 6,
                      background: isTop ? "#ebfbee" : "#f5f5f5",
                      color: "#1a1a1a",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                      <span>
                        {c.cardName}
                        {c.paymentType && ` + ${c.paymentType}`}
                        {!c.performanceMet && " (실적 미충족)"}
                      </span>
                      <strong>{c.expectedSaving.toLocaleString()}원</strong>
                    </div>
                    <div style={{ height: 6, background: "#eee", borderRadius: 3, overflow: "hidden", marginTop: 4 }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${ratio * 100}%`,
                          background: isTop ? "#2f9e44" : "#adb5bd",
                        }}
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
