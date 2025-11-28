import React, { useState } from 'react';
import styles from './App.module.css';
import ErrorBoundary from './components/common/ErrorBoundary';
import LoginForm from './components/auth/LoginForm';
import SignupForm from './components/auth/SignupForm';
import LicenseKeyForm from './components/license/LicenseKeyForm';

/**
 * App Component
 * 
 * Main application component managing the authentication and license flow.
 * 
 * Flow:
 * 1. User sees Login/Signup
 * 2. After successful auth -> License validation
 * 3. After valid license -> Dashboard (placeholder)
 */
function App() {
    const [user, setUser] = useState(null);
    const [license, setLicense] = useState(null);
    const [view, setView] = useState('login'); // 'login', 'signup', 'license', 'dashboard'

    const handleLoginSuccess = (userData) => {
        console.log('Login successful:', userData);
        setUser(userData);
        setView('license');
    };

    const handleSignupSuccess = (userData) => {
        console.log('Signup successful:', userData);
        setUser(userData);
        setView('license');
    };

    const handleLicenseValid = (licenseData) => {
        console.log('License validated:', licenseData);
        setLicense(licenseData);
        setView('dashboard');
    };

    const toggleAuthView = () => {
        setView(view === 'login' ? 'signup' : 'login');
    };

    const renderContent = () => {
        // If user is not logged in, show auth forms
        if (!user) {
            return (
                <div className={styles.authContainer}>
                    {view === 'login' ? (
                        <>
                            <LoginForm onLoginSuccess={handleLoginSuccess} />
                            <div className={styles.toggleLink} onClick={toggleAuthView}>
                                Don't have an account? Sign up
                            </div>
                        </>
                    ) : (
                        <>
                            <SignupForm onSignupSuccess={handleSignupSuccess} />
                            <div className={styles.toggleLink} onClick={toggleAuthView}>
                                Already have an account? Log in
                            </div>
                        </>
                    )}
                </div>
            );
        }

        // If user is logged in but no license, show license form
        if (!license) {
            return <LicenseKeyForm onLicenseValid={handleLicenseValid} />;
        }

        // If user is logged in and has valid license, show dashboard
        return (
            <div className={styles.dashboard}>
                <h1 className={styles.dashboardTitle}>Welcome to Trivya Platform</h1>
                <div className={styles.dashboardContent}>
                    <p>Hello, {user.name}!</p>
                    <p>License Type: {license.type}</p>
                    <p>License Expiry: {license.expiryDate}</p>
                    <p>This is a placeholder for the main dashboard.</p>
                </div>
            </div>
        );
    };

    return (
        <ErrorBoundary>
            <div className={styles.app}>
                <main className={styles.main}>
                    {renderContent()}
                </main>
            </div>
        </ErrorBoundary>
    );
}

export default App;
