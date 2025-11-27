import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ErrorBoundary from '../../../../../frontend/src/components/common/ErrorBoundary';

// Helper component that throws an error
const Bomb = ({ shouldThrow }) => {
    if (shouldThrow) {
        throw new Error('💥 CABOOM 💥');
    }
    return <div>Everything is fine.</div>;
};

describe('ErrorBoundary Component', () => {
    // Prevent console.error from cluttering the test output
    const originalConsoleError = console.error;
    beforeAll(() => {
        console.error = jest.fn();
    });

    afterAll(() => {
        console.error = originalConsoleError;
    });

    test('renders children without error', () => {
        render(
            <ErrorBoundary>
                <div>Safe Content</div>
            </ErrorBoundary>
        );
        expect(screen.getByText('Safe Content')).toBeInTheDocument();
    });

    test('catches error and renders fallback UI', () => {
        render(
            <ErrorBoundary>
                <Bomb shouldThrow={true} />
            </ErrorBoundary>
        );

        expect(screen.getByText('Something went wrong.')).toBeInTheDocument();
        expect(screen.getByText(/Our team has been notified/)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Reload Page/i })).toBeInTheDocument();
    });

    test('calls onError prop when error is caught', () => {
        const handleError = jest.fn();
        render(
            <ErrorBoundary onError={handleError}>
                <Bomb shouldThrow={true} />
            </ErrorBoundary>
        );

        expect(handleError).toHaveBeenCalledTimes(1);
        expect(handleError).toHaveBeenCalledWith(expect.any(Error), expect.any(Object));
    });

    test('matches snapshot of fallback UI', () => {
        const { asFragment } = render(
            <ErrorBoundary>
                <Bomb shouldThrow={true} />
            </ErrorBoundary>
        );
        expect(asFragment()).toMatchSnapshot();
    });
});
