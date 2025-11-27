# Loading Component

## Description
The `Loading` component is a reusable UI element designed to indicate active processes or data fetching. It adheres to the Trivya luxury design system, featuring a gold and cyan color palette on a charcoal background. It supports two main visual styles: a rotating spinner and a shimmering skeleton loader.

## Props

| Name      | Type     | Default   | Description                                      |
|-----------|----------|-----------|--------------------------------------------------|
| `size`    | String   | `'medium'`| Size of the loader. Options: `'small'`, `'medium'`, `'large'`. |
| `message` | String   | `null`    | Optional text message displayed below the loader.|
| `type`    | String   | `'spinner'`| Visual style. Options: `'spinner'`, `'skeleton'`.|

## Usage Examples

### Default Spinner
```jsx
import Loading from './Loading';

<Loading />
```

### Spinner with Message
```jsx
<Loading message="Authenticating User..." />
```

### Large Skeleton Loader
Useful for loading placeholders for large content blocks.
```jsx
<Loading type="skeleton" size="large" />
```

### Small Skeleton for Avatar
```jsx
<Loading type="skeleton" size="small" />
```

### Accessibility
The component automatically includes `aria-live="polite"` and `aria-busy="true"` to announce status changes to screen readers. The `message` prop is also used as the `aria-label`.
