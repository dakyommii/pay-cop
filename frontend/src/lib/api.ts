const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface User {
  id: number;
  name: string;
}

export interface Card {
  id: number;
  user_id: number;
  card_name: string;
  card_type: string;
  current_performance: number;
  required_performance: number;
}

export interface CardInput {
  card_name: string;
  card_type: string;
  current_performance: number;
  required_performance: number;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export function createUser(name: string) {
  return request<User>("/users", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function listCards(userId: number) {
  return request<Card[]>(`/users/${userId}/cards`);
}

export function createCard(userId: number, payload: CardInput) {
  return request<Card>(`/users/${userId}/cards`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCardPerformance(userId: number, cardId: number, currentPerformance: number) {
  return request<Card>(`/users/${userId}/cards/${cardId}/performance`, {
    method: "PATCH",
    body: JSON.stringify({ current_performance: currentPerformance }),
  });
}

export interface RecommendCardInput {
  name: string;
  performance: number;
  requiredPerformance: number;
}

export interface RecommendRequest {
  merchant: string;
  category: string;
  amount: number;
  cards: RecommendCardInput[];
  payments: string[];
}

export interface RecommendCandidate {
  cardName: string;
  paymentType: string | null;
  expectedSaving: number;
  performanceMet: boolean;
}

export interface RecommendResponse {
  recommendedCard: string;
  recommendedPayment: string | null;
  expectedSaving: number;
  reason: string;
  candidates: RecommendCandidate[];
}

export function recommendPayment(payload: RecommendRequest) {
  return request<RecommendResponse>("/payment/recommend", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
