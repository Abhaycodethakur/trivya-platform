import React from 'react';
import { render, screen } from '@testing-library/react';
import Dashboard from '../../components/dashboard/Dashboard';

describe('Dashboard Component', () => {
    test('renders dashboard title', () => {
        render(<Dashboard />);
        expect(screen.getByText('Welcome to Trivya')).toBeInTheDocument();
        expect(screen.getByText('AI-Powered Customer Support Platform')).toBeInTheDocument();
    });

    test('renders quick actions section', () => {
        render(<Dashboard />);
        expect(screen.getByText('Quick Actions')).toBeInTheDocument();
        expect(screen.getByText('Deploy AI Agent')).toBeInTheDocument();
        expect(screen.getByText('Add Knowledge')).toBeInTheDocument();
        expect(screen.getByText('View Analytics')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    test('renders AI insights section', () => {
        render(<Dashboard />);
        expect(screen.getByText('AI Insights')).toBeInTheDocument();
        expect(screen.getByText('Efficiency Boost')).toBeInTheDocument();
        expect(screen.getByText('Response Time')).toBeInTheDocument();
    });

    test('displays insight content', () => {
        render(<Dashboard />);
        expect(screen.getByText(/87% of tickets automatically/)).toBeInTheDocument();
        expect(screen.getByText(/decreased by 45%/)).toBeInTheDocument();
    });
});
