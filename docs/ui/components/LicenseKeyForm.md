# LicenseKeyForm Component

## Description
The `LicenseKeyForm` component is the gateway to the Trivya Platform. It ensures that only users with a valid, active license can access the application. It features a high-security, luxury design with real-time validation feedback.

## Props

| Name             | Type     | Default | Description                                      |
|------------------|----------|---------|--------------------------------------------------|
| `onLicenseValid` | Function | `null`  | Callback function executed when a license is successfully validated. Receives the license details object (type, expiry, features). |

## Usage Example

```jsx
import React from 'react';
import LicenseKeyForm from './components/license/LicenseKeyForm';

const ActivationPage = () => {
  const handleActivation = (licenseDetails) => {
    console.log('License Activated:', licenseDetails);
    // Store license info and redirect to dashboard
  };

  return (
    <div className="activation-page">
      <LicenseKeyForm onLicenseValid={handleActivation} />
    </div>
  );
};

export default ActivationPage;
```

## Features
- **Input Formatting:** Automatically capitalizes input for better readability.
- **Mock Validation:** Validates against a list of known keys (e.g., `TRIVYA-GOLD-2024-KEY1`).
- **Feedback:** Clear error messages for invalid or expired keys, and success confirmation.
- **Security:** Prevents multiple submissions while validating.
