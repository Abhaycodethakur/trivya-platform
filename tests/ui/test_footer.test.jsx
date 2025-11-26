import React from 'react';
import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/router';
import Footer from './components/common/Footer';

// Mock the hooks
jest.mock('next/router', () => ({
    useRouter: jest.fn(),
}));

// Mock Next.js Link component - Pass className and onClick
jest.mock('next/link', () => {
    return ({ children, href, className, onClick }) => {
        return <a href={href} className={className} onClick={onClick}>{children}</a>;
    };
});

describe('Footer Component', () => {
    const mockPush = jest.fn();

    beforeEach(() => {
        // Reset mocks before each test
        jest.clearAllMocks();

        // Setup default router mock
        useRouter.mockReturnValue({
            pathname: '/',
            push: mockPush,
        });
    });

    describe('Basic Rendering', () => {
        test('renders footer with correct CSS classes', () => {
            render(<Footer />);

            const footer = screen.getByRole('contentinfo');
            expect(footer).toBeInTheDocument();
            expect(footer.className).toContain('bg-charcoal-800');
            expect(footer.className).toContain('text-ivory');
        });

        test('renders Trivya logo and company name', () => {
            render(<Footer />);

            // Check for logo
            const logo = screen.getByTestId('footer-logo');
            expect(logo).toBeInTheDocument();
            expect(screen.getByText('T')).toBeInTheDocument();

            // Check for company name
            expect(screen.getAllByText('Trivya')[0]).toBeInTheDocument();
        });

        test('displays company description', () => {
            render(<Footer />);

            const description = screen.getByText(/Enterprise-grade AI workforce/i);
            expect(description).toBeInTheDocument();
        });
    });

    describe('Navigation Links', () => {
        test('renders all footer link sections', () => {
            render(<Footer />);

            // Check section headings
            expect(screen.getByText('Product')).toBeInTheDocument();
            expect(screen.getByText('Company')).toBeInTheDocument();
            expect(screen.getByText('Support')).toBeInTheDocument();
        });

        test('renders Product section links with correct href', () => {
            render(<Footer />);

            const variantsLink = screen.getByText('Variants').closest('a');
            const pricingLink = screen.getByText('Pricing').closest('a');
            const apiDocsLink = screen.getByText('API Documentation').closest('a');

            expect(variantsLink).toHaveAttribute('href', '/variants');
            expect(pricingLink).toHaveAttribute('href', '/pricing');
            expect(apiDocsLink).toHaveAttribute('href', '/docs');
        });

        test('renders Company section links with correct href', () => {
            render(<Footer />);

            const aboutLink = screen.getByText('About Us').closest('a');
            const blogLink = screen.getByText('Blog').closest('a');
            const careersLink = screen.getByText('Careers').closest('a');

            expect(aboutLink).toHaveAttribute('href', '/about');
            expect(blogLink).toHaveAttribute('href', '/blog');
            expect(careersLink).toHaveAttribute('href', '/careers');
        });

        test('renders Support section links with correct href', () => {
            render(<Footer />);

            const helpLink = screen.getByText('Help Center').closest('a');
            const contactLink = screen.getByText('Contact Us').closest('a');
            const statusLink = screen.getByText('Status').closest('a');

            expect(helpLink).toHaveAttribute('href', '/support');
            expect(contactLink).toHaveAttribute('href', '/contact');
            expect(statusLink).toHaveAttribute('href', '/status');
        });

        test('renders Legal section links with correct href', () => {
            render(<Footer />);

            const privacyLink = screen.getByText('Privacy Policy').closest('a');
            const termsLink = screen.getByText('Terms of Service').closest('a');
            const cookieLink = screen.getByText('Cookie Policy').closest('a');

            expect(privacyLink).toHaveAttribute('href', '/privacy');
            expect(termsLink).toHaveAttribute('href', '/terms');
            expect(cookieLink).toHaveAttribute('href', '/cookies');
        });
    });

    describe('Social Media Links', () => {
        test('renders all social media icons', () => {
            render(<Footer />);

            const twitterLink = screen.getByLabelText('Twitter');
            const linkedinLink = screen.getByLabelText('LinkedIn');
            const githubLink = screen.getByLabelText('GitHub');

            expect(twitterLink).toBeInTheDocument();
            expect(linkedinLink).toBeInTheDocument();
            expect(githubLink).toBeInTheDocument();
        });

        test('social media links have correct href attributes', () => {
            render(<Footer />);

            const twitterLink = screen.getByLabelText('Twitter');
            const linkedinLink = screen.getByLabelText('LinkedIn');
            const githubLink = screen.getByLabelText('GitHub');

            expect(twitterLink).toHaveAttribute('href', 'https://twitter.com/trivya');
            expect(linkedinLink).toHaveAttribute('href', 'https://linkedin.com/company/trivya');
            expect(githubLink).toHaveAttribute('href', 'https://github.com/trivya');
        });

        test('social media links open in new tab', () => {
            render(<Footer />);

            const twitterLink = screen.getByLabelText('Twitter');

            expect(twitterLink).toHaveAttribute('target', '_blank');
            expect(twitterLink).toHaveAttribute('rel', 'noopener noreferrer');
        });
    });

    describe('Copyright Year', () => {
        test('displays current year in copyright', () => {
            render(<Footer />);

            const currentYear = new Date().getFullYear();
            const copyright = screen.getByTestId('copyright');

            expect(copyright).toHaveTextContent(`© ${currentYear} Trivya. All rights reserved.`);
        });
    });

    describe('Active Route Highlighting', () => {
        test('highlights active route with gold color', () => {
            // Mock router to return /variants as current path
            useRouter.mockReturnValue({
                pathname: '/variants',
                push: mockPush,
            });

            render(<Footer />);

            const variantsLink = screen.getByText('Variants').closest('a');
            expect(variantsLink.className).toContain('text-gold-500');
        });

        test('non-active routes have default color', () => {
            // Mock router to return / as current path
            useRouter.mockReturnValue({
                pathname: '/',
                push: mockPush,
            });

            render(<Footer />);

            const variantsLink = screen.getByText('Variants').closest('a');
            expect(variantsLink.className).toContain('text-ivory/70');
            // Check that it doesn't have the active class (text-gold-500) as a standalone class
            // It might be present in hover:text-gold-500, so we check specifically
            const classes = variantsLink.className.split(' ');
            expect(classes).not.toContain('text-gold-500');
        });
    });

    describe('Responsive Design', () => {
        test('footer has responsive grid classes', () => {
            const { container } = render(<Footer />);

            const gridContainer = container.querySelector('.grid');
            expect(gridContainer).toBeInTheDocument();
            expect(gridContainer.className).toContain('grid-cols-1');
            expect(gridContainer.className).toContain('md:grid-cols-2');
            expect(gridContainer.className).toContain('lg:grid-cols-5');
        });

        test('bottom section has responsive flex classes', () => {
            const { container } = render(<Footer />);

            const bottomSection = container.querySelector('.border-t');
            expect(bottomSection.className).toContain('flex-col');
            expect(bottomSection.className).toContain('md:flex-row');
        });
    });

    describe('Accessibility', () => {
        test('footer has correct role attribute', () => {
            render(<Footer />);

            const footer = screen.getByRole('contentinfo');
            expect(footer).toBeInTheDocument();
        });

        test('social media links have aria-labels', () => {
            render(<Footer />);

            expect(screen.getByLabelText('Twitter')).toBeInTheDocument();
            expect(screen.getByLabelText('LinkedIn')).toBeInTheDocument();
            expect(screen.getByLabelText('GitHub')).toBeInTheDocument();
        });
    });
});
