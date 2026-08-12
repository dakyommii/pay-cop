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
    <main className="page">
      <nav className="page-nav">
        <Link href="/payment">결제 정보 입력 →</Link>
      </nav>
      <h1 className="page-title">카드 등록</h1>
      <p className="page-subtitle">보유한 카드와 이번 달 실적을 등록해두면 결제 추천에 반영돼요.</p>

      {userError && <p className="msg-error" style={{ marginBottom: 12 }}>사용자 초기화 실패: {userError}</p>}
      {error && <p className="msg-error" style={{ marginBottom: 12 }}>{error}</p>}

      <form onSubmit={handleSubmit} className="form">
        <div className="field">
          <input
            type="text"
            placeholder="카드명 (예: 신한카드)"
            value={form.card_name}
            onChange={(e) => setForm({ ...form, card_name: e.target.value })}
            required
          />
        </div>
        <div className="field">
          <input
            type="text"
            placeholder="카드 종류 (예: 신용카드)"
            value={form.card_type}
            onChange={(e) => setForm({ ...form, card_type: e.target.value })}
            required
          />
        </div>
        <div className="field">
          <label className="field-label">이번 달 실적</label>
          <input
            type="number"
            min={0}
            value={form.current_performance}
            onChange={(e) => setForm({ ...form, current_performance: Number(e.target.value) })}
          />
        </div>
        <div className="field">
          <label className="field-label">월 실적 기준</label>
          <input
            type="number"
            min={0}
            value={form.required_performance}
            onChange={(e) => setForm({ ...form, required_performance: Number(e.target.value) })}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={!userId}>
          카드 등록
        </button>
      </form>

      <h2 className="section-title">등록된 카드</h2>
      {loading && <p className="text-muted">불러오는 중...</p>}
      <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        {cards.map((card) => {
          const ratio =
            card.required_performance > 0
              ? Math.min(1, card.current_performance / card.required_performance)
              : 0;
          return (
            <li key={card.id} className="card">
              <div className="card-header">
                <span className="card-title">{card.card_name}</span>
                <span className="card-tag">{card.card_type}</span>
              </div>
              <div className="card-meta">
                {card.current_performance.toLocaleString()}원 / {card.required_performance.toLocaleString()}원
              </div>
              <div className="progress-track">
                <div
                  className={`progress-fill${ratio < 1 ? " progress-fill--accent" : ""}`}
                  style={{ width: `${ratio * 100}%` }}
                />
              </div>
              <div className="card-footer">
                <label className="field-label">실적 수정:</label>
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
                />
              </div>
            </li>
          );
        })}
      </ul>
    </main>
  );
}
