import { useEffect, useState } from "react";
import { apiRequest } from "../api";
import { formatMoney } from "../utils";
import NewSaleForm from "../components/NewSaleForm";

const dateFormat = new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" });

export default function SalesPage() {
  const [sales, setSales] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    try {
      const [salesData, productsData] = await Promise.all([
        apiRequest("/sales/"),
        apiRequest("/products/"),
      ]);
      setSales(salesData);
      setProducts(productsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function downloadInvoice(saleId) {
    try {
      const blob = await apiRequest(`/sales/${saleId}/invoice`, { responseType: "blob" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `invoice-${saleId}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Sales</h1>

      {error && <div className="rounded-lg bg-red-50 text-red-700 px-4 py-3">{error}</div>}

      <NewSaleForm products={products} onCreated={loadData} />

      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <h2 className="text-lg font-bold text-slate-800 px-6 pt-5 pb-3">Sales history</h2>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">#</th>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Customer</th>
              <th className="px-4 py-3 font-medium">Items</th>
              <th className="px-4 py-3 font-medium">Sold by</th>
              <th className="px-4 py-3 font-medium text-right">Total</th>
              <th className="px-4 py-3 font-medium text-right">Invoice</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-slate-500">Loading...</td>
              </tr>
            )}
            {!loading && sales.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-slate-500">No sales yet</td>
              </tr>
            )}
            {sales.map((sale) => (
              <tr key={sale.id} className="hover:bg-slate-50 align-top">
                <td className="px-4 py-3 text-slate-500">{sale.id}</td>
                <td className="px-4 py-3 text-slate-600 whitespace-nowrap">
                  {dateFormat.format(new Date(sale.created_at))}
                </td>
                <td className="px-4 py-3 text-slate-800">{sale.customer_name || "—"}</td>
                <td className="px-4 py-3 text-slate-600">
                  {sale.items.map((item) => `${item.quantity}× ${item.product.name}`).join(", ")}
                </td>
                <td className="px-4 py-3 text-slate-600">{sale.created_by?.username || "—"}</td>
                <td className="px-4 py-3 text-right font-medium text-slate-800">
                  {formatMoney(sale.total_amount)}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => downloadInvoice(sale.id)}
                    className="text-slate-600 hover:text-slate-900 font-medium"
                  >
                    Download
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}