// 카드고릴라(card-gorilla.com) 실시간 인기순위에서 2026-08-12에 직접 확인한 실제 카드
// 상품명 · 카드 종류 · 전월실적 조건. 할인율/적립률 등은 우리가 만들어낸 값이 아니므로
// 포함하지 않았고, 카드 등록 폼의 자동완성(카드 종류·실적 기준)에만 사용한다.
//
// 참고: 우리 백엔드의 Benefit 카탈로그(신한카드/삼성카드/현대카드 단위 혜택율)는 이
// 구체적인 상품명과는 매칭되지 않는다. 즉 "신한카드 Mr.Life"로 등록하면 카드 할인은
// 0원으로 계산되고(실제 할인율을 지어내지 않았으므로), 실적 충족 여부와 간편결제
// 적립만 정상 반영된다. 혜택 매칭까지 되길 원하면 이슈어 단위("신한카드" 등)로
// 등록하면 된다.
export interface CardCatalogEntry {
  issuer: string;
  name: string;
  cardType: "신용카드" | "체크카드";
  requiredPerformance: number;
}

export const CARD_ISSUERS = ["신한카드", "삼성카드", "현대카드"] as const;

export const CARD_CATALOG: CardCatalogEntry[] = [
  { issuer: "신한카드", name: "신한카드 Mr.Life", cardType: "신용카드", requiredPerformance: 300000 },
  { issuer: "신한카드", name: "신한카드 처음(ANNIVERSE)", cardType: "신용카드", requiredPerformance: 300000 },
  { issuer: "신한카드", name: "신한카드 Deep Oil", cardType: "신용카드", requiredPerformance: 300000 },
  { issuer: "신한카드", name: "신한카드 Deep Dream 체크", cardType: "체크카드", requiredPerformance: 0 },
  { issuer: "삼성카드", name: "삼성 iD SELECT ALL 카드", cardType: "신용카드", requiredPerformance: 400000 },
  { issuer: "삼성카드", name: "삼성카드 taptap O", cardType: "신용카드", requiredPerformance: 300000 },
  { issuer: "삼성카드", name: "K-패스 삼성체크카드", cardType: "체크카드", requiredPerformance: 300000 },
  { issuer: "현대카드", name: "알파벳카드S", cardType: "신용카드", requiredPerformance: 400000 },
  { issuer: "현대카드", name: "대한항공카드 300", cardType: "신용카드", requiredPerformance: 500000 },
  { issuer: "현대카드", name: "현대카드M CHECK", cardType: "체크카드", requiredPerformance: 0 },
];
