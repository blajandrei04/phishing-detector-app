# Phishing Detector — Angular Frontend

A modern, high-performance web interface built with **Angular 17+** and **NgRx** state management. This application serves as the user-facing interface for the Phishing Detector platform, communicating with the FastAPI backend to analyze URLs, display SHAP-based model explanations, and provide administrator dashboard views.

---

## 🚀 Key Features

*   **Real-time Threat Analysis Portal**: Clean search/input interface with client-side URL validation and immediate threat verification response.
*   **Explainable AI (XAI) Presentation**: Dynamic, responsive SHAP charts that explain exactly which feature values led the model to mark a URL as phishing or safe.
*   **Security Metrics Dashboard**: Real-time stats visualization (Total scans, threats found, safe rate) and interactive SVG-based charts (Donut charts, activity logs).
*   **Role-Based Access Control (RBAC)**: Secure routes protected by Angular AuthGuards, restricting the Admin Panel and statistics pages to authenticated users.
*   **Responsive Design & Dark Mode**: Modern design built on top of customized CSS variables supporting smooth transitions and instant dark theme toggles.
*   **Interactive History Logs**: Paginated logs with client-side filtering and full threat report retrieval.

---

## 📁 Project Directory Structure

```
frontend/frontend/
├── src/
│   ├── app/
│   │   ├── core/                  # Core singletons, services, facades, and state
│   │   │   ├── facades/           # Facade pattern encapsulating NgRx selectors/dispatch
│   │   │   ├── guards/            # AuthGuard and Role Guards for route protection
│   │   │   ├── interceptors/     # JWT authorization token injection and API headers
│   │   │   ├── services/          # HTTP client services for API communication
│   │   │   └── store/             # NgRx State Management (Actions, Reducers, Effects)
│   │   ├── models/                # Strongly typed TypeScript interfaces (Request/Response schemas)
│   │   ├── pages/                 # Routing component views
│   │   │   ├── admin-review/      # Admin portal for false positive feedback labeling
│   │   │   ├── analyzer/          # URL scanning landing view
│   │   │   ├── dashboard/         # Threat Intelligence metrics dashboard
│   │   │   ├── history/           # Paginated scan history view
│   │   │   ├── login/             # Administrator authentication form
│   │   │   ├── results/           # Detailed SHAP and active inspection threat reports
│   │   │   └── settings/          # User profile and password configurations
│   │   └── shared/                # Reusable presentation components (e.g., sidebar, topnav)
│   ├── assets/                    # Static assets, fonts, and icons
│   ├── index.html                 # App container HTML
│   ├── main.ts                    # Bootstrap configuration
│   └── styles.scss                # Global Design Tokens (colors, fonts, variables)
```

---

## 🛠️ State Management Architecture (NgRx)

To ensure predictable data flow and robust local state caching across route changes, the application uses **NgRx**:
*   **Actions**: Strongly typed events (e.g., `[Auth] Login Request`, `[Auth] Load User Success`) describing state alterations.
*   **Reducers**: Pure functions managing immutable state updates for the user context, auth tokens, and session status.
*   **Effects**: Side-effect handlers managing async HTTP communication with the backend APIs.
*   **Selectors**: Optimized, memoized selectors querying state slices (e.g., `selectIsAuthenticated`, `selectCurrentUser`).
*   **Facades**: The **Facade Pattern** is implemented to simplify components, exposing direct observables (`isAuthenticated$`, `user$`) and wrapper methods without injecting the NgRx Store directly.

---

## 🔧 Local Setup & Build Commands

### Prerequisites
*   **Node.js**: v18.0.0+
*   **Angular CLI**: Install globally via `npm install -g @angular/cli`

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm start
# Server runs at http://localhost:4200/
```

### 3. Build Production Bundle
```bash
npm run build
# Compiled files are stored in the dist/ folder, optimized for distribution
```

### 4. Running Unit Tests
```bash
npm run test
# Executes unit test suites using the Vitest test runner
```
