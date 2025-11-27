import React, { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Loading from '../../../frontend/src/components/common/Loading';

const MockParentComponent = () => {
    const [isLoading, setIsLoading] = useState(false);

    return (
        <div>
            <button onClick={() => setIsLoading(!isLoading)}>
                Toggle Loading
            </button>
            {isLoading && <Loading message="Loading content..." />}
            {!isLoading && <div data-testid="content">Content Loaded</div>}
        </div>
    );
};

describe('Loading Component Integration', () => {
    test('toggles visibility based on parent state', () => {
        render(<MockParentComponent />);

        // Initially not loading
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
        expect(screen.getByTestId('content')).toBeInTheDocument();

        // Click to start loading
        fireEvent.click(screen.getByText('Toggle Loading'));

        // Loading component should appear
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Loading content...')).toBeInTheDocument();
        expect(screen.queryByTestId('content')).not.toBeInTheDocument();

        // Click to stop loading
        fireEvent.click(screen.getByText('Toggle Loading'));

        // Loading component should disappear
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
        expect(screen.getByTestId('content')).toBeInTheDocument();
    });
});
