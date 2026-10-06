import { useState } from "react";

const fields = [
  { name: "name", label: "Name", required: true },
  { name: "category", label: "Category" },
  { name: "price", label: "Price (₹)", type: "number", step: "0.01", min: "0.01", required: true },
  { name: "stock_quantity", label: "Stock", type: "number", min: "0", required: true },
  { name: "low_stock_threshold", label: "Low-stock alert at", type: "number", min: "0", required: true },
  { name: "supplier", label: "Supplier" },
];

const emptyForm = {
  name: "",
  category: "",
  price: "",
  stock_quantity: "0",
  low_stock_threshold: "10",
  supplier: "",
};

export default function ProductForm({ product, onSave, onCancel }) {
  const [form, setForm] = useState(
    product
      ? {
          name: product.name,
          category: product.category ?? "",
          price: String(product.price),
          stock_quantity: String(product.stock_quantity),
          low_stock_threshold: String(product.low_stock_threshold),
          supplier: product.supplier ?? "",
        }
      : emptyForm
  );
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await onSave({
        name: form.name.trim(),
        category: form.category.trim() || null,
        price: Number(form.price),
        stock_quantity: Number(form.stock_quantity),
        low_stock_threshold: Number(form.low_stock_threshold),
        supplier: form.supplier.trim() || null,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md bg-white rounded-xl shadow-lg p-6 space-y-4">
        <h2 className="text-xl font-bold text-slate-800">
          {product ? "Edit product" : "Add product"}
        </h2>

        {error && (
          <div className="rounded-lg bg-red-50 text-red-700 text-sm px-3 py-2">{error}</div>
        )}

        {fields.map((field) => (
          <div key={field.name}>
            <label className="block text-sm font-medium text-slate-700 mb-1">{field.label}</label>
            <input
              type={field.type || "text"}
              step={field.step}
              min={field.min}
              required={field.required}
              value={form[field.name]}
              onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-400"
            />
          </div>
        ))}

        <div className="flex justify-end gap-2 pt-2">
          <button type="button" onClick={onCancel} className="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100">
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-slate-900 text-white px-4 py-2 font-medium hover:bg-slate-800 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}