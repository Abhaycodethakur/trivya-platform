import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../../components/layout/Layout';

describe('Layout Component', () => {
    const renderLayout = (children) => {
        return render(
            <BrowserRouter>
                <Layout>{children}</Layout>
            </BrowserRouter>
        );
    };

    test('renders layout structure', () => {
        renderLayout(<div>Test Content</div>);
        expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    test('renders sidebar component', () => {
        renderLayout(<div>Content</div>);
        // Sidebar should contain navigation items
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    test('renders top bar component', () => {
        renderLayout(<div>Content</div>);
        // TopBar should have search input
        expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
    });

    test('renders children content', () => {
        const testContent = 'Test Dashboard Content';
        renderLayout(<div>{testContent}</div>);
        expect(screen.getByText(testContent)).toBeInTheDocument();
    });
});
