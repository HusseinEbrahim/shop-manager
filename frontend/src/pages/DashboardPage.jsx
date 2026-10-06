import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { apiRequest } from "../api";
import { formatMoney } from "../utils";

function StatCard({ label, value, highlight }) {
  return (
    <div className="bg-white rounded-xl shadow p-5">
      <div className="text-sm text-slate-500">{label}</div>
      <div className={`mt-1 text-2xl font-bold ${highlight ? "text-red-600" : "text-slate-800"}`}>
        {value}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/dashboard/summary")
      .then(setSummary)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div className="rounded-lg bg-red-50 text-red-700 px-4 py-3">{error}</div>;
  }

  if (!summary) {
    return <div className="text-slate-500">Loading...</div>;
  }

  const lowCount = summary.low_stock_products.length;
  const chartData = summary.top_products.map((p) => ({ name: p.name, units: p.units_sold }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Today's revenue" value={formatMoney(summary.today_sales_total)} />
        <StatCard label="Sales today" value={summary.today_sales_count} />
        <StatCard label="Low-stock items" value={lowCount} highlight={lowCount > 0} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-bold text-slate-800 mb-4">Top products (last 30 days)</h2>
          {chartData.length === 0 ? (
            <p className="text-slate-500 text-sm">No sales in the last 30 days</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value) => [`${value} units`, "Sold"]} />
                  <Bar dataKey="units" fill="#334155" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-slate-800">Low stock</h2>
            <Link to="/products" className="text-sm text-slate-500 hover:text-slate-800">
              View all products →
            </Link>
          </div>
          {lowCount === 0 ? (
            <p className="text-slate-500 text-sm">All products are well stocked</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {summary.low_stock_products.map((p) => (
                <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                  <span className="text-slate-800">{p.name}</span>
                  <span className="text-red-600 font-semibold">
                    {p.stock_quantity} left{" "}
                    <span className="text-slate-400 font-normal">(alert at {p.low_stock_threshold})</span>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}