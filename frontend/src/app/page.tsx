"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardInput, createCard, listCards, updateCardPerformance } from "@/lib/api";
import { useCurrentUser } from "@/lib/useCurrentUser";

const emptyForm: CardInput = {
  card_name: "",
  card_type: "",
  current_performance: 0,
  required_performance: 0,
};

export default function Home() {
  const { userId, error: userError } = useCurrentUser();
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CardInput>(emptyForm);

  const refresh = async (uid: number) => {
    setLoading(true);
    try {
      setCards(await listCards(uid));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) refresh(userId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!userId) return;
    try {
      await createCard(userId, form);
      setForm(emptyForm);
      await refresh(userId);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handlePerformanceChange = async (cardId: number, value: number) => {
    if (!userId) return;
    try {
      await updateCardPerformance(userId, cardId, value);
      await refresh(userId);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <main style={{ maxWidth: 480, margin: "40px auto", padding: "0 16px", fontFamily: "sans-serif" }}>
      <h1>카드 등록</h1>
      <p style={{ marginBottom: 16 }}>
        <Link href="/payment">결제 정보 입력 →</Link>
      </p>

      {userError && <p style={{ color: "crimson" }}>사용자 초기화 실패: {userError}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 24 }}
      >
        <input
          placeholder="카드명 (예: 신한카드)"
          value={form.card_name}
          onChange={(e) => setForm({ ...form, card_name: e.target.value })}
          required
        />
        <input
          placeholder="카드 종류 (예: 신용카드)"
          value={form.card_type}
          onChange={(e) => setForm({ ...form, card_type: e.target.value })}
          required
        />
        <label style={{ fontSize: 14 }}>
          이번 달 실적
          <input
            type="number"
            min={0}
            value={form.current_performance}
            onChange={(e) => setForm({ ...form, current_performance: Number(e.target.value) })}
          />
        </label>
        <label style={{ fontSize: 14 }}>
          월 실적 기준
          <input
            type="number"
            min={0}
            value={form.required_performance}
            onChange={(e) => setForm({ ...form, required_performance: Number(e.target.value) })}
          />
        </label>
        <button type="submit" disabled={!userId}>
          카드 등록
        </button>
      </form>

      <h2>등록된 카드</h2>
      {loading && <p>불러오는 중...</p>}
      <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        {cards.map((card) => {
          const ratio =
            card.required_performance > 0
              ? Math.min(1, card.current_performance / card.required_performance)
              : 0;
          return (
            <li key={card.id} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{card.card_name}</strong>
                <span>{card.card_type}</span>
              </div>
              <div style={{ fontSize: 14, color: "#555", margin: "4px 0" }}>
                {card.current_performance.toLocaleString()}원 / {card.required_performance.toLocaleString()}원
              </div>
              <div style={{ height: 6, background: "#eee", borderRadius: 3, overflow: "hidden" }}>
                <div
                  style={{
                    height: "100%",
                    width: `${ratio * 100}%`,
                    background: ratio >= 1 ? "#2f9e44" : "#4dabf7",
                  }}
                />
              </div>
              <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center" }}>
                <label style={{ fontSize: 13 }}>실적 수정:</label>
                <input
                  type="number"
                  min={0}
                  defaultValue={card.current_performance}
                  onBlur={(e) => {
                    const value = Number(e.target.value);
                    if (value !== card.current_performance) {
                      handlePerformanceChange(card.id, value);
                    }
                  }}
                  style={{ width: 120 }}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </main>
  );
}
