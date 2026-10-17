export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Kpis = {
  summary: {
    delivered_orders: number;
    on_time_rate: number;
    avg_review_score: number;
    avg_delivery_days: number;
  };
  by_state: { customer_state: string; orders: number; late_rate: number }[];
};

export async function getKpis(): Promise<Kpis> {
  const res = await fetch(`${API_URL}/kpis`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
