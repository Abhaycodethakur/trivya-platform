# Trivya Platform Frontend

## Getting Started

### Prerequisites
- Node.js 16+ installed
- npm or yarn package manager

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

### Running the Application

#### Development Mode
```bash
npm start
```
This will start the development server at `http://localhost:3000`

#### Production Build
```bash
npm run build
```
This creates an optimized production build in the `build` folder.

### Testing
```bash
npm test
```

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── auth/           # Authentication components
│   │   ├── common/         # Reusable components
│   │   └── license/        # License validation
│   ├── services/
│   │   └── __mocks__/      # Mock services
│   ├── App.jsx             # Main app component
│   ├── App.module.css      # App styles
│   └── index.js            # Entry point
└── package.json
```

## Features

- ✅ User Authentication (Login/Signup)
- ✅ License Validation
- ✅ Error Boundary
- ✅ Loading States
- ✅ Luxury Design System

## Valid Test Credentials

### Login
- Email: `test@example.com`
- Password: `password`

### License Keys
- `TRIVYA-GOLD-2024-KEY1` (Gold tier)
- `TRIVYA-ENTR-2024-KEY2` (Enterprise tier)
- `TRIVYA-TEST-1234-5678` (Test tier)
