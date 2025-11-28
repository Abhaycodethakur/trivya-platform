import React from 'react';
import { render, screen } from '@testing-library/react';
import ActivityFeed from '../../../src/components/dashboard/ActivityFeed';

describe('ActivityFeed Component', () => {
    test('renders activity feed title', () => {
        render(<ActivityFeed />);
        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    });

    test('renders activity items', () => {
        render(<ActivityFeed />);
        expect(screen.getByText('Ticket Resolved')).toBeInTheDocument();
        expect(screen.getByText('Knowledge Updated')).toBeInTheDocument();
        expect(screen.getByText('High Priority')).toBeInTheDocument();
        expect(screen.getByText('Agent Deployed')).toBeInTheDocument();
        expect(screen.getByText('Report Generated')).toBeInTheDocument();
    });

    test('displays activity descriptions', () => {
        render(<ActivityFeed />);
        expect(screen.getByText(/AI Agent resolved ticket #1234/)).toBeInTheDocument();
        expect(screen.getByText(/New FAQ added to knowledge base/)).toBeInTheDocument();
    });

    test('displays activity timestamps', () => {
        render(<ActivityFeed />);
        expect(screen.getByText('2 minutes ago')).toBeInTheDocument();
        expect(screen.getByText('15 minutes ago')).toBeInTheDocument();
        expect(screen.getByText('1 hour ago')).toBeInTheDocument();
    });

    test('renders activity icons', () => {
        render(<ActivityFeed />);
        // Icons are rendered as emoji text
        expect(screen.getByText('✅')).toBeInTheDocument();
        expect(screen.getByText('📚')).toBeInTheDocument();
        expect(screen.getByText('⚠️')).toBeInTheDocument();
    });
});
