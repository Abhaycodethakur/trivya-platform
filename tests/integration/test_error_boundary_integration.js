import React, { useEffect } from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ErrorBoundary from '../../../frontend/src/components/common/ErrorBoundary';

// A component that throws an error inside useEffect to simulate a runtime crash
const CrashingComponent = () => {
    useEffect(() => {
        throw new Error('Runtime Integration Error');
    }, []);
    return <div>Loading...</div>;
};

describe('ErrorBoundary Integration', () => {
    // Suppress console.error for the expected error
    const originalConsoleError = console.error;
    beforeAll(() => {
        console.error = jest.fn();
    });

    afterAll(() => {
        console.error = originalConsoleError;
    });

    test('catches runtime errors from child components and logs them', () => {
        render(
            <ErrorBoundary>
                <CrashingComponent />
            </ErrorBoundary>
        );

        // 1. Verify Fallback UI is displayed
        expect(screen.getByText('Something went wrong.')).toBeInTheDocument();
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

        // 2. Verify Error Logging
        // The ErrorBoundary logs "Uncaught error:" followed by the error object
        expect(console.error).toHaveBeenCalledWith(
            expect.stringContaining('Uncaught error:'),
            expect.any(Error),
            expect.any(Object)
        );
    });
});
