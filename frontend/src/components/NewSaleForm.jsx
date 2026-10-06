import { useState } from "react";
import { apiRequest } from "../api";
import { formatMoney } from "../utils";

const emptyItem = { product_id: "", quantity: 1 };

export default function NewSaleForm({ products, onCreated }) {
  const [customerName, setCustomerName] = useState("");
  const [items, setItems] = useState([{ ...emptyItem }]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  const productsById = Object.fromEntries(products.map((p) => [p.id, p]));

  function updateItem(index, field, value) {
    setItems(items.map((item, i) => (i === index ? { ...item, [field]: value } : item)));
  }

  function addItem() {
    setItems([...items, { ...emptyItem }]);
  }

  function removeItem(index) {
    setItems(items.filter((_, i) => i !== index));
  }

  const total = items.reduce((sum, item) => {
    const product = productsById[item.product_id];
    return product ? sum + Number(product.price) * Number(item.quantity || 0) : sum;
  }, 0);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      const sale = await apiRequest("/sales/", {
        method: "POST",
        body: {
          customer_name: customerName.trim() || null,
          items: items.map((item) => ({
            product_id: Number(item.product_id),
            quantity: Number(item.quantity),
          })),
        },
      });
      setSuccess(`Sale #${sale.id} recorded: ${formatMoney(sale.total_amount)}`);
      setCustomerName("");
      setItems([{ ...emptyItem }]);
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-6 space-y-4">
      <h2 className="text-lg font-bold text-slate-800">New sale</h2>

      {error && <div className="rounded-lg bg-red-50 text-red-700 text-sm px-3 py-2">{error}</div>}
      {success && <div className="rounded-lg bg-green-50 text-green-700 text-sm px-3 py-2">{success}</div>}

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Customer name (optional)</label>
        <input
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          className="w-full max-w-sm rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-400"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">Items</label>
        {items.map((item, index) => {
          const product = productsById[item.product_id];
          return (
            <div key={index} className="flex items-center gap-2">
              <select
                required
                value={item.product_id}
                onChange={(e) => updateItem(index, "product_id", e.target.value)}
                className="flex-1 rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-400"
              >
                <option value="">Select a product...</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id} disabled={p.stock_quantity === 0}>
                    {p.name} ({formatMoney(p.price)}, {p.stock_quantity} in stock)
                  </option>
                ))}
              </select>
              <input
                type="number"
                min="1"
                required
                value={item.quantity}
                onChange={(e) => updateItem(index, "quantity", e.target.value)}
                className="w-24 rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
              <span className="w-28 text-right text-sm text-slate-600">
                {product ? formatMoney(Number(product.price) * Number(item.quantity || 0)) : "—"}
              </span>
              {items.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="text-red-600 hover:text-red-800 px-2"
                >
                  ✕
                </button>
              )}
            </div>
          );
        })}
        <button type="button" onClick={addItem} className="text-sm text-slate-600 hover:text-slate-900">
          + Add another item
        </button>
      </div>

      <div className="flex items-center justify-between border-t border-slate-100 pt-4">
        <div className="text-lg font-bold text-slate-800">Total: {formatMoney(total)}</div>
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-slate-900 text-white px-5 py-2 font-medium hover:bg-slate-800 disabled:opacity-50"
        >
          {saving ? "Recording..." : "Record sale"}
        </button>
      </div>
    </form>
  );
}