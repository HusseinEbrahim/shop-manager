import { useEffect, useState } from "react";
import { apiRequest } from "../api";
import { useAuth } from "../AuthContext";
import { formatMoney } from "../utils";
import ProductForm from "../components/ProductForm";

export default function ProductsPage() {
  const { user } = useAuth();
  const isOwner = user.role === "owner";

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState(null); // null = closed, {} = adding, product = editing

  async function loadProducts() {
    try {
      setProducts(await apiRequest("/products/"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  async function handleSave(data) {
    if (editing.id) {
      await apiRequest(`/products/${editing.id}`, { method: "PATCH", body: data });
    } else {
      await apiRequest("/products/", { method: "POST", body: data });
    }
    setEditing(null);
    loadProducts();
  }

  async function handleDelete(product) {
    if (!window.confirm(`Delete "${product.name}"?`)) return;
    try {
      await apiRequest(`/products/${product.id}`, { method: "DELETE" });
      loadProducts();
    } catch (err) {
      alert(err.message);
    }
  }

  const query = search.toLowerCase();
  const filtered = products.filter((p) =>
    [p.name, p.category, p.supplier].some((value) => value?.toLowerCase().includes(query))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Products</h1>
        {isOwner && (
          <button
            onClick={() => setEditing({})}
            className="rounded-lg bg-slate-900 text-white px-4 py-2 font-medium hover:bg-slate-800"
          >
            + Add product
          </button>
        )}
      </div>

      <input
        placeholder="Search by name, category, or supplier..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-400"
      />

      {error && <div className="rounded-lg bg-red-50 text-red-700 px-4 py-3">{error}</div>}

      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 font-medium">Price</th>
              <th className="px-4 py-3 font-medium">Stock</th>
              <th className="px-4 py-3 font-medium">Supplier</th>
              {isOwner && <th className="px-4 py-3 font-medium text-right">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">Loading...</td>
              </tr>
            )}
            {!loading && filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">No products found</td>
              </tr>
            )}
            {filtered.map((p) => {
              const isLow = p.stock_quantity <= p.low_stock_threshold;
              return (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">{p.name}</td>
                  <td className="px-4 py-3 text-slate-600">{p.category || "—"}</td>
                  <td className="px-4 py-3 text-slate-800">{formatMoney(p.price)}</td>
                  <td className="px-4 py-3">
                    <span className={isLow ? "text-red-600 font-semibold" : "text-slate-800"}>
                      {p.stock_quantity}
                    </span>
                    {isLow && (
                      <span className="ml-2 rounded-full bg-red-100 text-red-700 text-xs px-2 py-0.5">Low</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{p.supplier || "—"}</td>
                  {isOwner && (
                    <td className="px-4 py-3 text-right space-x-3">
                      <button onClick={() => setEditing(p)} className="text-slate-600 hover:text-slate-900">
                        Edit
                      </button>
                      <button onClick={() => handleDelete(p)} className="text-red-600 hover:text-red-800">
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {editing && (
        <ProductForm
          product={editing.id ? editing : null}
          onSave={handleSave}
          onCancel={() => setEditing(null)}
        />
      )}
    </div>
  );
}