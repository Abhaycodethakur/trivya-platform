# SignupForm Component

## Description
The `SignupForm` component allows new users to register for the Trivya platform. It includes comprehensive validation for user details and ensures password confirmation matches. It follows the same luxury design principles as the rest of the authentication suite.

## Props

| Name              | Type     | Default | Description                                      |
|-------------------|----------|---------|--------------------------------------------------|
| `onSignupSuccess` | Function | `null`  | Callback function executed when registration is successful. Receives the new user object. |

## Usage Example

```jsx
import React from 'react';
import SignupForm from './components/auth/SignupForm';

const RegisterPage = () => {
  const handleRegistration = (user) => {
    console.log('New user registered:', user);
    // Redirect to onboarding or dashboard
  };

  return (
    <div className="register-page">
      <SignupForm onSignupSuccess={handleRegistration} />
    </div>
  );
};

export default RegisterPage;
```

## Validation Rules
- **Name:** Required, minimum 2 characters.
- **Email:** Required, valid email format.
- **Password:** Required, minimum 8 characters.
- **Confirm Password:** Must exactly match the password.

## Features
- **Real-time Validation:** Clears errors as the user types.
- **Loading State:** Prevents double-submission and indicates progress.
- **Error Handling:** Displays backend errors (e.g., "Email already exists").
