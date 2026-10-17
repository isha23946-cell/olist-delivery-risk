import { getKpis } from "@/lib/api";

function Card({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="mt-1 text-3xl font-semibold text-gray-900">{value}</div>
    </div>
  );
}

export default async function Home() {
  const { summary, by_state } = await getKpis();
  const maxLate = Math.max(...by_state.map((s) => s.late_rate));
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-4xl p-8">
        <h1 className="text-2xl font-bold">Olist Delivery Risk</h1>
        <p className="mt-1 text-gray-600">Overview of delivered orders</p>
        <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card label="Delivered orders" value={summary.delivered_orders.toLocaleString("en-US")} />
          <Card label="On-time rate" value={`${(summary.on_time_rate * 100).toFixed(1)}%`} />
          <Card label="Avg review score" value={summary.avg_review_score.toFixed(2)} />
          <Card label="Avg delivery days" value={summary.avg_delivery_days.toFixed(1)} />
        </div>
        <h2 className="mt-10 text-lg font-semibold">Late rate by customer state</h2>
        <p className="text-sm text-gray-500">Top 10 states by number of orders</p>
        <div className="mt-4 space-y-2">
          {by_state.map((s) => (
            <div key={s.customer_state} className="flex items-center gap-3">
              <div className="w-8 text-sm font-medium">{s.customer_state}</div>
              <div className="h-5 flex-1 rounded bg-gray-200">
                <div
                  className="h-5 rounded bg-red-500"
                  style={{ width: `${(s.late_rate / maxLate) * 100}%` }}
                />
              </div>
              <div className="w-14 text-right text-sm">{(s.late_rate * 100).toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
