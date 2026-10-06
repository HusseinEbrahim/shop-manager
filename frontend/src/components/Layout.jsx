import { NavLink, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../AuthContext";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/products", label: "Products" },
  { to: "/sales", label: "Sales" },
];

export default function Layout() {
  const { user, loading, logout } = useAuth();

  if (loading) return <div className="p-8 text-slate-500">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen flex bg-slate-100">
      <aside className="w-56 bg-slate-900 text-slate-100 flex flex-col">
        <div className="px-6 py-5 text-lg font-bold">Shop Manager</div>

        <nav className="flex-1 px-3 space-y-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm ${
                  isActive ? "bg-slate-700 font-medium" : "hover:bg-slate-800"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-6 py-4 border-t border-slate-800 text-sm">
          <div className="font-medium">{user.username}</div>
          <div className="text-slate-400 capitalize">{user.role}</div>
          <button onClick={logout} className="mt-3 text-slate-300 hover:text-white">
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}