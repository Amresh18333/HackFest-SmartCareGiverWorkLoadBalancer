# Smart Caregiver Workload Balancer 🩺⚖️

> Predict burnout risk and auto-suggest task rebalancing for care teams.

Built for HackFest, **Smart Caregiver Workload Balancer** helps care organizations keep an eye on how work is distributed across their caregivers — flagging burnout risk early and recommending smarter ways to rebalance tasks before staff are overloaded.

**🔗 Live demo:** [hack-fest-smart-care-giver-work-loa-bice.vercel.app](https://hack-fest-smart-care-giver-work-loa-bice.vercel.app)

---

## ✨ What it does

- **Burnout risk prediction** — surfaces which caregivers are trending toward overload based on their current workload.
- **Smart task rebalancing** — auto-suggests how to redistribute tasks across the team to even out the load.
- **AI-assisted insights** — uses an LLM (via the Groq API) to generate recommendations and explanations, rather than relying on static rules alone.
- **Secure, multi-user access** — authentication and role handling backed by Supabase and JWT.

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite (built to `frontend/dist`, deployed on **Vercel**) |
| Backend | Python, **FastAPI** (served with `uvicorn`, deployed on **Render**) |
| Database / Auth | **Supabase** (Postgres, Auth) |
| AI / LLM | **Groq API** |
| Auth tokens | JWT |

## 📁 Project Structure

```
HackFest-SmartCareGiverWorkLoadBalancer/
├── backend/            # FastAPI application (app.main:app)
├── frontend/            # React + Vite client
├── package.json         # Root-level dependency (Supabase JS client)
├── render.yaml           # Render deployment config (backend)
├── vercel.json           # Vercel deployment config (frontend)
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites

- Node.js (for the frontend)
- Python 3.11+ (for the backend)
- A [Supabase](https://supabase.com/) project (URL + keys)
- A [Groq](https://groq.com/) API key

### 1. Clone the repository

```bash
git clone https://github.com/Amresh18333/HackFest-SmartCareGiverWorkLoadBalancer.git
cd HackFest-SmartCareGiverWorkLoadBalancer
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with the following variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
JWT_SECRET_KEY=your_jwt_secret
CORS_ORIGINS=http://localhost:5173
GROQ_API_KEY=your_groq_api_key
ENVIRONMENT=development
```

Run the API locally:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`, with a health check at `/health`.

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173` (default Vite port).

## ☁️ Deployment

This project is set up to deploy as two separate services:

- **Frontend → Vercel**, configured via [`vercel.json`](./vercel.json) (installs and builds from the `frontend/` directory, outputs to `frontend/dist`).
- **Backend → Render**, configured via [`render.yaml`](./render.yaml) (Python runtime, root directory `backend/`, started with `uvicorn app.main:app`).

Make sure the environment variables listed above are set in each platform's dashboard before deploying.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or file an issue.

## 📄 License

No license has been specified for this repository yet. Add a `LICENSE` file to clarify usage terms.
