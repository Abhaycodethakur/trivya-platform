# App Component

## Description
The `App` component is the root of the Trivya Platform application. It manages the global authentication and licensing flow, conditionally rendering different views based on the user's authentication and license status.

## Application Flow

```
┌─────────────┐
│   Login     │ ←→ Signup
└──────┬──────┘
       │ (Auth Success)
       ↓
┌─────────────┐
│   License   │
│ Validation  │
└──────┬──────┘
       │ (Valid License)
       ↓
┌─────────────┐
│  Dashboard  │
└─────────────┘
```

## State Management

| State      | Type   | Description                                    |
|------------|--------|------------------------------------------------|
| `user`     | Object | Stores authenticated user data (id, name, token) |
| `license`  | Object | Stores validated license data (type, expiry, features) |
| `view`     | String | Current view: 'login', 'signup', 'license', 'dashboard' |

## Features
- **Conditional Rendering:** Automatically shows the appropriate form based on auth/license status.
- **Error Boundary:** Wraps the entire app to catch and display errors gracefully.
- **State Persistence:** Maintains user and license data throughout the session.
- **Toggle Navigation:** Easy switching between login and signup views.

## Usage Example

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

## Next Steps
- Implement persistent storage (localStorage/sessionStorage) for user/license data.
- Add routing library (React Router) for URL-based navigation.
- Build out the actual Dashboard component with real features.
