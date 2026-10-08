# Shop Manager

A full-stack inventory, sales, and billing system for small retail businesses. Owners manage products and track performance, staff record sales, stock updates automatically, and every sale generates a downloadable PDF invoice.

**🔗 Live demo:** https://shop-manager-pink.vercel.app
**📘 API docs:** https://YOUR-RENDER-URL.onrender.com/docs

| Role  | Username | Password    |
|-------|----------|-------------|
| Owner | `demo`   | `demo12345` |
| Staff | `staff`  | `staff12345` |

> The backend runs on a free tier and sleeps when idle, so the first login may take 30–60 seconds while it wakes up.

![Dashboard](docs/screenshots/dashboard.png)

## Features

- **Inventory management:** add, edit, and delete products, with search and low-stock indicators
- **Multi-item sales:** record sales with several products; stock is deducted automatically
- **Overselling prevention:** sales are validated against available stock inside a database transaction with row-level locking, so concurrent sales can't sell the same unit twice
- **Role-based access control:** owners have full control; staff can view products and record sales only, enforced in both the API and the UI
- **JWT authentication:** secure login with Argon2 password hashing
- **Analytics dashboard:** today's revenue and sales count (calculated in IST), a top-5 products chart for the last 30 days, and a low-stock list
- **PDF invoices:** a generated invoice for every sale, with line items, totals, and the staff member who made the sale
- **Sales history:** every sale with its items, customer, timestamp, and who recorded it

## Screenshots

| Products | Sales |
|----------|-------|
| ![Products](docs/screenshots/products.png) | ![Sales](docs/screenshots/sales.png) |

![Invoice](docs/screenshots/invoice.png)

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React, React Router, Tailwind CSS, Recharts, Vite |
| Backend    | Python, FastAPI, SQLAlchemy, Pydantic |
| Database   | PostgreSQL (Neon) |
| Auth       | JWT (PyJWT), Argon2 password hashing (pwdlib) |
| PDFs       | fpdf2 |
| Testing    | pytest, FastAPI TestClient |
| Deployment | Docker, Render (backend), Vercel (frontend) |

## Engineering Highlights

- **Transactional stock updates:** a sale validates every item before changing anything, then commits all changes at once. If any item fails (missing product or insufficient stock), nothing is saved.
- **Concurrency safety:** `SELECT ... FOR UPDATE` locks product rows while a sale is processed, preventing race conditions when two sales happen at the same moment.
- **Price snapshots:** each sale item stores the unit price at the time of sale, so later price changes never alter historical records.
- **Server-side totals:** clients send only product IDs and quantities; prices and totals are always calculated by the backend.
- **SQL analytics:** the dashboard uses joins, aggregation (`SUM`, `COUNT`, `GROUP BY`), and timezone conversion inside PostgreSQL.
- **Automated tests:** 16 tests covering authentication, permissions, validation, stock logic, transactions, and invoice generation, run against an isolated test database.

## Project Structure

```
shop-manager/
├── backend/
│   ├── routers/          # API routes: auth, products, sales, dashboard
│   ├── tests/            # pytest test suite
│   ├── main.py           # FastAPI app setup
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # JWT and password hashing
│   ├── invoices.py       # PDF invoice generation
│   ├── seed.py           # Demo data generator
│   └── Dockerfile
└── frontend/
    └── src/
        ├── pages/        # Dashboard, Products, Sales, Login
        ├── components/   # Layout, forms
        ├── api.js        # API client with auth handling
        └── AuthContext.jsx
```

## Running Locally

**Prerequisites:** Python 3.12+, Node.js 20+, and a PostgreSQL database (for example, a free Neon database).

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://user:password@host/dbname
SECRET_KEY=your-random-secret-key
```

Load demo data and start the server:

```bash
python seed.py
uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000, with interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at http://localhost:5173.

### Tests

Add a separate test database to `backend/.env`:

```
TEST_DATABASE_URL=postgresql+psycopg://user:password@host/test_dbname
```

Then run:

```bash
cd backend
pytest -v
```

## API Overview

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST   | `/auth/login` | Public | Log in and receive a JWT |
| GET    | `/auth/me` | Logged in | Current user |
| POST   | `/auth/users` | Owner | Create a staff or owner account |
| GET    | `/products/` | Logged in | List products |
| POST   | `/products/` | Owner | Create a product |
| PATCH  | `/products/{id}` | Owner | Update a product |
| DELETE | `/products/{id}` | Owner | Delete a product (blocked if it has sales) |
| POST   | `/sales/` | Logged in | Record a sale |
| GET    | `/sales/` | Logged in | Sales history |
| GET    | `/sales/{id}/invoice` | Logged in | Download a PDF invoice |
| GET    | `/dashboard/summary` | Logged in | Dashboard statistics |