import React from 'react';
import PropTypes from 'prop-types';
import styles from './ErrorBoundary.module.css';

/**
 * ErrorBoundary Component
 * 
 * Catches JavaScript errors anywhere in their child component tree,
 * logs those errors, and displays a fallback UI.
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log the error to an error reporting service
        console.error("Uncaught error:", error, errorInfo);

        if (this.props.onError) {
            this.props.onError(error, errorInfo);
        }
    }

    handleReload = () => {
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className={styles.container} role="alert">
                    <h1 className={styles.heading}>Something went wrong.</h1>
                    <p className={styles.message}>
                        We apologize for the inconvenience. Our team has been notified of this issue.
                        Please try reloading the page.
                    </p>
                    <button
                        className={styles.button}
                        onClick={this.handleReload}
                    >
                        Reload Page
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

ErrorBoundary.propTypes = {
    /**
     * The child components to be rendered.
     */
    children: PropTypes.node.isRequired,
    /**
     * Optional callback function called when an error is caught.
     * Useful for logging to external services like Sentry.
     */
    onError: PropTypes.func,
};

export default ErrorBoundary;
