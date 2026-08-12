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

// 시딩된 Benefit 카탈로그와 일치하는 카드명 (2단계 seed 데이터 기준). 목록에 없는 카드는
// "직접 입력"으로 등록할 수 있지만, 혜택 매칭은 카탈로그에 있는 카드명에만 걸린다.
const CARD_NAME_OPTIONS = ["신한카드", "삼성카드", "현대카드"];
const CUSTOM_CARD_NAME = "__custom__";
const CARD_TYPE_OPTIONS = ["신용카드", "체크카드"];

export default function Home() {
  const { userId, error: userError } = useCurrentUser();
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CardInput>(emptyForm);
  const [useCustomCardName, setUseCustomCardName] = useState(false);

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
      setUseCustomCardName(false);
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
          <select
            value={useCustomCardName ? CUSTOM_CARD_NAME : form.card_name}
            onChange={(e) => {
              if (e.target.value === CUSTOM_CARD_NAME) {
                setUseCustomCardName(true);
                setForm({ ...form, card_name: "" });
              } else {
                setUseCustomCardName(false);
                setForm({ ...form, card_name: e.target.value });
              }
            }}
            required
          >
            <option value="" disabled>
              카드명 선택
            </option>
            {CARD_NAME_OPTIONS.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
            <option value={CUSTOM_CARD_NAME}>직접 입력</option>
          </select>
          {useCustomCardName && (
            <input
              type="text"
              placeholder="카드명 입력"
              value={form.card_name}
              onChange={(e) => setForm({ ...form, card_name: e.target.value })}
              required
            />
          )}
        </div>
        <div className="field">
          <select
            value={form.card_type}
            onChange={(e) => setForm({ ...form, card_type: e.target.value })}
            required
          >
            <option value="" disabled>
              카드 종류 선택
            </option>
            {CARD_TYPE_OPTIONS.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
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
