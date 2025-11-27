# ErrorBoundary Component

## Description
The `ErrorBoundary` component is a critical utility that catches JavaScript errors anywhere in its child component tree, logs those errors, and displays a fallback UI instead of the component tree that crashed. It prevents the entire application from breaking due to a single component error.

## Props

| Name      | Type     | Default   | Description                                      |
|-----------|----------|-----------|--------------------------------------------------|
| `children`| Node     | Required  | The components to be wrapped and protected.      |
| `onError` | Function | `null`    | Optional callback for custom error handling/logging. |

## Usage Examples

### Basic Usage
Wrap your entire application or major route components to ensure the app doesn't crash completely.
```jsx
import ErrorBoundary from './components/common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <MainContent />
    </ErrorBoundary>
  );
}
```

### Advanced Usage with Logging
Pass an `onError` handler to log errors to an external service like Sentry or a custom logger.
```jsx
const logErrorToService = (error, info) => {
  // Send to logging service
  console.log("Logged to service:", error, info);
};

<ErrorBoundary onError={logErrorToService}>
  <Dashboard />
</ErrorBoundary>
```

### Integration Note
This component is designed to work seamlessly with the Trivya design system. It uses the global color variables and provides a consistent "Something went wrong" experience across the platform.
