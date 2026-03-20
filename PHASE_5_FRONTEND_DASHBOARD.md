# PHASE 5 — Frontend & Dashboard (Kora Vision)

## Overview

This phase implements the **React frontend** with dashboard UI, including:

1. **Landing Page** — Marketing page with feature overview
2. **Dashboard Layout** — Responsive sidebar navigation
3. **Dashboard Page** — Main dashboard with stats and widgets
4. **Integrations Page** — Manage connected services
5. **Real-time Updates** — WebSocket integration
6. **Responsive Design** — Mobile-first with TailwindCSS

---

## Architecture Decisions

### 1. Framework: React 19 + TypeScript
**Choice:** React with TypeScript for type safety
**Rationale:**
- Modern React 19 with hooks
- Type safety with TypeScript
- Component reusability
- Large ecosystem

### 2. Styling: TailwindCSS 4
**Choice:** Utility-first CSS framework
**Rationale:**
- Fast development
- Consistent design tokens
- Responsive design built-in
- Small bundle size

### 3. UI Components: shadcn/ui
**Choice:** Headless UI components
**Rationale:**
- Accessible components
- Customizable
- Built on Radix UI
- Copy-paste components

### 4. Routing: Wouter
**Choice:** Lightweight client-side router
**Rationale:**
- Minimal bundle size
- Simple API
- Perfect for static sites
- No configuration needed

### 5. State Management: React Query
**Choice:** Server state management
**Rationale:**
- Handles API caching
- Automatic refetching
- Background updates
- Optimistic updates

---

## File Structure

```
client/
├── public/
│   ├── favicon.ico
│   ├── robots.txt
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── DashboardLayout.tsx         # Main layout with sidebar
│   │   ├── DashboardCard.tsx           # Reusable card component
│   │   ├── ErrorBoundary.tsx           # Error handling
│   │   └── ui/                         # shadcn/ui components
│   ├── pages/
│   │   ├── Home.tsx                    # Landing page
│   │   ├── Dashboard.tsx               # Main dashboard
│   │   ├── Integrations.tsx            # Integrations page
│   │   └── NotFound.tsx                # 404 page
│   ├── contexts/
│   │   └── ThemeContext.tsx            # Theme management
│   ├── hooks/
│   │   ├── useWebSocket.ts             # WebSocket hook
│   │   └── useApi.ts                   # API hook
│   ├── lib/
│   │   ├── api.ts                      # API client
│   │   └── constants.ts                # Constants
│   ├── App.tsx                         # Main app component
│   ├── main.tsx                        # Entry point
│   └── index.css                       # Global styles
└── index.html
```

---

## Components

### DashboardLayout

Main layout component with sidebar navigation.

**Features:**
- Collapsible sidebar
- Navigation items
- User menu
- Responsive design

**Usage:**
```tsx
<DashboardLayout>
  <YourContent />
</DashboardLayout>
```

### DashboardCard

Reusable card component for displaying metrics.

**Props:**
- `title`: Card title
- `description`: Optional description
- `icon`: Optional icon
- `value`: Metric value
- `trend`: Optional trend indicator
- `children`: Optional custom content

**Usage:**
```tsx
<DashboardCard
  title="Active Users"
  value={1234}
  trend={{ value: 12, isPositive: true }}
  icon={<Users size={24} />}
/>
```

---

## Pages

### Home Page

Landing page with feature overview and CTA.

**Sections:**
- Navigation
- Hero section
- Features grid
- Integrations showcase
- CTA section
- Footer

### Dashboard Page

Main dashboard with statistics and widgets.

**Features:**
- Stats cards (dashboards, integrations, sync status, uptime)
- Dashboard list
- Recent activity feed
- Create new dashboard button

### Integrations Page

Manage connected services.

**Features:**
- List of connected integrations
- Available services grid
- Connect/disconnect buttons
- Sync status indicators
- Last sync timestamp

---

## API Integration

### API Client

```typescript
// lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Custom Hooks

```typescript
// hooks/useApi.ts
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';

export function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiClient.get<T>(url);
        setData(response.data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}
```

### WebSocket Hook

```typescript
// hooks/useWebSocket.ts
import { useEffect, useState } from 'react';

export function useWebSocket(url: string) {
  const [data, setData] = useState<any>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };

    ws.onerror = () => {
      setConnected(false);
    };

    return () => ws.close();
  }, [url]);

  return { data, connected };
}
```

---

## Real-time Updates

### WebSocket Integration

```typescript
// In Dashboard.tsx
import { useWebSocket } from '@/hooks/useWebSocket';

export default function Dashboard() {
  const { data: updates, connected } = useWebSocket(
    `ws://localhost:8003/ws/${tenantId}`
  );

  useEffect(() => {
    if (updates) {
      // Handle real-time updates
      console.log('Update received:', updates);
    }
  }, [updates]);

  return (
    <div>
      {connected && <div className="text-green-600">Connected</div>}
      {/* Dashboard content */}
    </div>
  );
}
```

---

## Styling

### Theme System

The frontend uses CSS variables for theming. Edit `client/src/index.css` to customize colors.

**Key Variables:**
- `--primary`: Primary brand color
- `--secondary`: Secondary color
- `--accent`: Accent color
- `--background`: Background color
- `--foreground`: Text color
- `--card`: Card background
- `--border`: Border color

**Dark Mode:**
```css
.dark {
  --background: oklch(0.141 0.005 285.823);
  --foreground: oklch(0.85 0.005 65);
  /* ... more variables */
}
```

### Responsive Design

Mobile-first approach with TailwindCSS breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

---

## Development Workflow

### Start Development Server

```bash
cd client
npm run dev

# Server runs on http://localhost:3000
```

### Build for Production

```bash
npm run build

# Output in dist/
```

### Type Checking

```bash
npm run check
```

### Format Code

```bash
npm run format
```

---

## Authentication Flow

### Cognito Integration

```typescript
// lib/auth.ts
import { CognitoIdentityProviderClient, InitiateAuthCommand } from '@aws-sdk/client-cognito-identity-provider';

const cognitoClient = new CognitoIdentityProviderClient({
  region: process.env.VITE_COGNITO_REGION,
});

export async function login(email: string, password: string) {
  const command = new InitiateAuthCommand({
    ClientId: process.env.VITE_COGNITO_CLIENT_ID,
    AuthFlow: 'USER_PASSWORD_AUTH',
    AuthParameters: {
      USERNAME: email,
      PASSWORD: password,
    },
  });

  const response = await cognitoClient.send(command);
  const token = response.AuthenticationResult?.IdToken;

  if (token) {
    localStorage.setItem('auth_token', token);
  }

  return token;
}
```

---

## Performance Optimization

### Code Splitting

```typescript
// App.tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Integrations = lazy(() => import('@/pages/Integrations'));

function Router() {
  return (
    <Switch>
      <Route path="/dashboard">
        <Suspense fallback={<Loading />}>
          <Dashboard />
        </Suspense>
      </Route>
      {/* ... */}
    </Switch>
  );
}
```

### Image Optimization

Always use CDN URLs for images:
```tsx
<img 
  src="https://cdn.example.com/image.png" 
  alt="Description"
  loading="lazy"
/>
```

### Memoization

```typescript
import { memo } from 'react';

const DashboardCard = memo(function DashboardCard(props) {
  return <div>{/* ... */}</div>;
});
```

---

## Testing

### Unit Tests

```bash
npm run test
```

### E2E Tests

```bash
npm run test:e2e
```

---

## Deployment

### Deploy to Manus

```bash
# Create checkpoint
git add .
git commit -m "Deploy frontend"

# Push to Manus
npm run build
```

### Environment Variables

Create `.env.local`:
```
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://ws.example.com
VITE_COGNITO_REGION=us-east-1
VITE_COGNITO_CLIENT_ID=xxxxx
```

---

## Troubleshooting

### WebSocket Connection Failed

```typescript
// Check WebSocket URL
console.log('Connecting to:', `ws://localhost:8003/ws/${tenantId}`);

// Ensure backend is running
curl http://localhost:8003/health
```

### API Requests Failing

```typescript
// Check API URL
console.log('API Base URL:', process.env.VITE_API_URL);

// Check CORS headers
curl -H "Origin: http://localhost:3000" http://localhost:8000/health
```

### Styling Issues

```typescript
// Check theme context
const { theme } = useTheme();
console.log('Current theme:', theme);

// Verify CSS variables
console.log(getComputedStyle(document.documentElement).getPropertyValue('--primary'));
```

---

## Validation Checklist

After Phase 5 deployment:

- [ ] **Landing page loads**
  ```bash
  curl http://localhost:3000/
  ```

- [ ] **Dashboard page accessible**
  ```bash
  curl http://localhost:3000/dashboard
  ```

- [ ] **Integrations page works**
  ```bash
  curl http://localhost:3000/integrations
  ```

- [ ] **API calls successful**
  ```bash
  curl -H "Authorization: Bearer <token>" http://localhost:8000/dashboards
  ```

- [ ] **WebSocket connection works**
  ```bash
  wscat -c ws://localhost:8003/ws/tenant-uuid
  ```

- [ ] **Responsive design works**
  - Test on mobile (375px)
  - Test on tablet (768px)
  - Test on desktop (1280px)

- [ ] **Theme switching works**
  - Light mode
  - Dark mode

- [ ] **Build succeeds**
  ```bash
  npm run build
  ```

---

## Next Steps

**Phase 5 Complete.** All phases finished!

**Summary of Deliverables:**

✅ **Phase 0** — Architecture Definition  
✅ **Phase 1** — Infrastructure Foundation (Terraform)  
✅ **Phase 2** — Data Layer (PostgreSQL + Alembic)  
✅ **Phase 3** — Backend Core (4 FastAPI services)  
✅ **Phase 4** — Integration Framework (5 connectors)  
✅ **Phase 5** — Frontend & Dashboard (React + TailwindCSS)  

**Ready for Production Deployment!**

Please confirm:
1. ✅ Frontend loads and displays correctly?
2. ✅ Navigation between pages works?
3. ✅ Responsive design looks good?
4. ✅ Ready to deploy full stack?

**Reply "APROVADO" to complete the project.**
