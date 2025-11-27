# LoginForm Component

## Description
The `LoginForm` component provides a secure and user-friendly interface for user authentication. It handles input validation, communicates with the authentication service, and manages loading and error states. It is styled according to the Trivya luxury design system.

## Props

| Name             | Type     | Default | Description                                      |
|------------------|----------|---------|--------------------------------------------------|
| `onLoginSuccess` | Function | `null`  | Callback function executed when login is successful. Receives the user object as an argument. |

## Usage Example

```jsx
import React from 'react';
import LoginForm from './components/auth/LoginForm';

const LoginPage = () => {
  const handleLogin = (user) => {
    console.log('User logged in:', user);
    // Redirect to dashboard or save token
  };

  return (
    <div className="login-page">
      <LoginForm onLoginSuccess={handleLogin} />
    </div>
  );
};

export default LoginPage;
```

## Features
- **Client-side Validation:** Checks for valid email format and required password.
- **Loading State:** Displays a spinner and disables the submit button during API calls.
- **Error Handling:** Displays user-friendly error messages for invalid credentials or network issues.
- **Accessibility:** Fully accessible with ARIA labels and states.
