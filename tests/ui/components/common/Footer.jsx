import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const Footer = () => {
    const router = useRouter();
    const currentYear = new Date().getFullYear();

    // Footer navigation links
    const footerLinks = {
        product: [
            { name: 'Variants', href: '/variants' },
            { name: 'Pricing', href: '/pricing' },
            { name: 'API Documentation', href: '/docs' }
        ],
        company: [
            { name: 'About Us', href: '/about' },
            { name: 'Blog', href: '/blog' },
            { name: 'Careers', href: '/careers' }
        ],
        support: [
            { name: 'Help Center', href: '/support' },
            { name: 'Contact Us', href: '/contact' },
            { name: 'Status', href: '/status' }
        ],
        legal: [
            { name: 'Privacy Policy', href: '/privacy' },
            { name: 'Terms of Service', href: '/terms' },
            { name: 'Cookie Policy', href: '/cookies' }
        ]
    };

    // Social media links
    const socialLinks = [
        { name: 'Twitter', icon: 'M22.46 6c-.85.38-1.75.64-2.7.76 1-.6 1.76-1.55 2.12-2.68-.93.55-1.96.95-3.06 1.17-.88-.94-2.13-1.53-3.51-1.53-2.66 0-4.81 2.16-4.81 4.81 0 .38.04.75.13 1.1-4-.2-7.54-2.11-9.91-5.02-.41.71-.65 1.53-.65 2.4 0 1.67.85 3.14 2.14 4.01-.79-.02-1.53-.24-2.18-.6v.06c0 2.33 1.66 4.28 3.86 4.72-.4.11-.83.17-1.27.17-.31 0-.62-.03-.92-.08.63 1.91 2.39 3.3 4.49 3.34-1.65 1.29-3.72 2.06-5.97 2.06-.39 0-.77-.02-1.15-.07 2.13 1.36 4.65 2.16 7.37 2.16 8.84 0 13.68-7.32 13.68-13.68 0-.21 0-.42-.01-.62.94-.68 1.76-1.53 2.4-2.5z', href: 'https://twitter.com/trivya' },
        { name: 'LinkedIn', icon: 'M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z', href: 'https://linkedin.com/company/trivya' },
        { name: 'GitHub', icon: 'M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z', href: 'https://github.com/trivya' }
    ];

    return (
        <footer className="bg-charcoal-800 text-ivory" role="contentinfo">
            <div className="container mx-auto px-4 py-12">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
                    {/* Company Info */}
                    <div className="lg:col-span-2">
                        <div className="flex items-center space-x-2 mb-4">
                            <div className="relative">
                                <div className="h-8 w-8 bg-gold-500 rounded-full flex items-center justify-center" data-testid="footer-logo">
                                    <span className="text-charcoal-900 font-bold text-lg">T</span>
                                </div>
                            </div>
                            <span className="text-xl font-bold text-ivory">Trivya</span>
                        </div>
                        <p className="text-ivory/70 mb-6 max-w-md">
                            Enterprise-grade AI workforce that works around the clock, without the cost of three full-time employees.
                        </p>
                        <div className="flex space-x-4">
                            {socialLinks.map((social) => (
                                <a
                                    key={social.name}
                                    href={social.href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-ivory/70 hover:text-gold-500 transition-colors duration-200"
                                    aria-label={social.name}
                                >
                                    <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                                        <path d={social.icon} />
                                    </svg>
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Product Links */}
                    <div>
                        <h3 className="text-gold-500 font-semibold mb-4">Product</h3>
                        <ul className="space-y-2">
                            {footerLinks.product.map((link) => (
                                <li key={link.name}>
                                    <Link
                                        href={link.href}
                                        className={`text-ivory/70 hover:text-gold-500 transition-colors duration-200 ${router.pathname === link.href ? 'text-gold-500' : ''
                                            }`}
                                    >
                                        {link.name}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Company Links */}
                    <div>
                        <h3 className="text-gold-500 font-semibold mb-4">Company</h3>
                        <ul className="space-y-2">
                            {footerLinks.company.map((link) => (
                                <li key={link.name}>
                                    <Link
                                        href={link.href}
                                        className={`text-ivory/70 hover:text-gold-500 transition-colors duration-200 ${router.pathname === link.href ? 'text-gold-500' : ''
                                            }`}
                                    >
                                        {link.name}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Support Links */}
                    <div>
                        <h3 className="text-gold-500 font-semibold mb-4">Support</h3>
                        <ul className="space-y-2">
                            {footerLinks.support.map((link) => (
                                <li key={link.name}>
                                    <Link
                                        href={link.href}
                                        className={`text-ivory/70 hover:text-gold-500 transition-colors duration-200 ${router.pathname === link.href ? 'text-gold-500' : ''
                                            }`}
                                    >
                                        {link.name}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Bottom Section */}
                <div className="border-t border-charcoal-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
                    <p className="text-ivory/70 text-sm mb-4 md:mb-0" data-testid="copyright">
                        © {currentYear} Trivya. All rights reserved.
                    </p>
                    <div className="flex space-x-6">
                        {footerLinks.legal.map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                className="text-ivory/70 hover:text-gold-500 text-sm transition-colors duration-200"
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
