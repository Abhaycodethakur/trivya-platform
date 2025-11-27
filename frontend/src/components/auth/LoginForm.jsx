import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styles from './LoginForm.module.css';
import Loading from '../common/Loading';
import * as authService from '../../services/__mocks__/authService';

/**
 * LoginForm Component
 * 
 * Handles user authentication with email and password.
 * Includes validation, loading states, and error handling.
 */
const LoginForm = ({ onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [validationErrors, setValidationErrors] = useState({});

    const validateForm = () => {
        const errors = {};
        if (!email) {
            errors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            errors.email = 'Please enter a valid email address';
        }

        if (!password) {
            errors.password = 'Password is required';
        }

        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);

        try {
            const user = await authService.login(email, password);
            if (onLoginSuccess) {
                onLoginSuccess(user);
            }
        } catch (err) {
            setError(err.message || 'An unexpected error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Welcome Back</h2>

            {error && (
                <div className={styles.globalError} role="alert">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} noValidate aria-busy={isLoading}>
                <div className={styles.formGroup}>
                    <label htmlFor="email" className={styles.label}>Email Address</label>
                    <input
                        id="email"
                        type="email"
                        className={`${styles.input} ${validationErrors.email ? styles.errorInput : ''}`}
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={isLoading}
                        aria-invalid={!!validationErrors.email}
                        aria-describedby={validationErrors.email ? "email-error" : undefined}
                    />
                    {validationErrors.email && (
                        <span id="email-error" className={styles.errorMessage}>
                            {validationErrors.email}
                        </span>
                    )}
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="password" className={styles.label}>Password</label>
                    <input
                        id="password"
                        type="password"
                        className={`${styles.input} ${validationErrors.password ? styles.errorInput : ''}`}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={isLoading}
                        aria-invalid={!!validationErrors.password}
                        aria-describedby={validationErrors.password ? "password-error" : undefined}
                    />
                    {validationErrors.password && (
                        <span id="password-error" className={styles.errorMessage}>
                            {validationErrors.password}
                        </span>
                    )}
                </div>

                <button
                    type="submit"
                    className={styles.submitButton}
                    disabled={isLoading}
                >
                    {isLoading ? <Loading size="small" type="spinner" /> : 'Sign In'}
                </button>
            </form>
        </div>
    );
};

LoginForm.propTypes = {
    /**
     * Callback function called upon successful login with user data.
     */
    onLoginSuccess: PropTypes.func,
};

export default LoginForm;
