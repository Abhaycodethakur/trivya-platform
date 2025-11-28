import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Loading from '../../components/common/Loading';

describe('Loading Component', () => {

    test('renders default spinner correctly', () => {
        const { container } = render(<Loading />);
        const spinner = container.querySelector('.spinner');
        expect(spinner).toBeInTheDocument();
        expect(spinner).toHaveClass('medium'); // Default size
    });

    test('renders with message', () => {
        const testMessage = "Authenticating...";
        render(<Loading message={testMessage} />);
        expect(screen.getByText(testMessage)).toBeInTheDocument();
    });

    test('renders skeleton variant', () => {
        const { container } = render(<Loading type="skeleton" />);
        const skeleton = container.querySelector('.skeleton');
        expect(skeleton).toBeInTheDocument();
    });

    test('has correct accessibility attributes', () => {
        render(<Loading message="Loading data" />);
        const container = screen.getByRole('status');
        expect(container).toHaveAttribute('aria-live', 'polite');
        expect(container).toHaveAttribute('aria-busy', 'true');
        expect(container).toHaveAttribute('aria-label', 'Loading data');
    });

    test('applies size classes correctly', () => {
        const { container, rerender } = render(<Loading size="small" />);
        expect(container.querySelector('.spinner')).toHaveClass('small');

        rerender(<Loading size="large" />);
        expect(container.querySelector('.spinner')).toHaveClass('large');
    });

    test('matches snapshot', () => {
        const { asFragment } = render(<Loading message="Snapshot Test" size="medium" type="spinner" />);
        expect(asFragment()).toMatchSnapshot();
    });

    test('renders gracefully with unexpected props', () => {
        // @ts-ignore
        render(<Loading size="extra-large" type="unknown" />);
        // Should still render the container and potentially base classes without crashing
        const container = screen.getByRole('status');
        expect(container).toBeInTheDocument();
    });
});
