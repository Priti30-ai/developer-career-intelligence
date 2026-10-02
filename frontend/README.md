# Developer Career Intelligence System — Frontend

Modern analytics dashboard for the Developer Career Intelligence Platform, built with React, Vite, Tailwind CSS, React Router, Axios, and Recharts.

---

## Architecture & Directory Structure

```text
frontend/
├── src/
│   ├── assets/               # Static assets, SVG icons, and graphics
│   ├── components/           # Reusable UI component modules
│   │   ├── common/           # Generic building blocks (Card, Button, StatusBadge)
│   │   ├── layout/           # App shell (Header, Sidebar, Layout)
│   │   └── dashboard/        # Dashboard widgets (SystemStatusCard, ApiHealthCard)
│   ├── pages/                # Route view components (Dashboard)
│   ├── services/             # Centralized API layer (api.js via Axios)
│   ├── hooks/                # Custom React hooks (useApi)
│   ├── utils/                # Constants and helper utilities
│   ├── App.jsx               # Application router configuration
│   ├── main.jsx              # DOM entry point
│   └── index.css             # Tailwind CSS tokens & global styles
├── .env.example              # Template environment variables
├── .env                      # Local development environment configuration
├── package.json              # Dependencies and lifecycle scripts
├── postcss.config.js         # PostCSS configuration
├── tailwind.config.js        # Tailwind design tokens and theme extensions
├── vite.config.js            # Vite build and dev-server configuration
└── README.md                 # Frontend documentation
```

---

## Prerequisites

- **Node.js**: v18.0.0 or later (v24.x tested)
- **npm**: v9.0.0 or later (v11.x tested)
- **Backend API**: FastAPI service running at `http://localhost:8000`

---

## Configuration

The application uses Vite environment variables. Configure the backend API base URL in `.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

All API calls flow through the centralized Axios client at `src/services/api.js`.

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run the Development Server
```bash
npm run dev
```
The application will start at `http://localhost:5173`.

### 3. Build for Production
```bash
npm run build
```
Generates an optimized production build in the `dist/` directory.

### 4. Preview Production Build
```bash
npm run preview
```

---

## Key Features in Foundation Phase

- **Centralized API Client**: Axios client with configured timeouts, interceptors, and environment-driven base URL.
- **Client-to-Server Health Check**: Built-in interactive connection testing to the FastAPI `/health` endpoint.
- **Academic Mentor Presentation Ready**: Clear system roadmap, service registry status, and clean layout designed for professional evaluation.
- **Responsive Layout**: Sidebar collapsible on mobile screens, sticky header with live backend latency monitoring.
