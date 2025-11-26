import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../../hooks/useAuth';
import { useLicense } from '../../hooks/useLicense';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const { license } = useLicense();
  const router = useRouter();

  // Handle scroll effect for header
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle logout
  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Check if current route matches
  const isActiveRoute = (route) => {
    return router.pathname === route;
  };

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-charcoal-900 bg-opacity-95 backdrop-blur-md shadow-lg' 
          : 'bg-charcoal-900 bg-opacity-80'
      }`}
      role="banner"
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="relative">
                <div data-testid="logo" className="h-10 w-auto">LOGO</div>
                <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-cyan-500 rounded-full animate-pulse"></div>
              </div>
              <span className="text-2xl font-bold text-ivory">Trivya</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              href="/dashboard" 
              className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                isActiveRoute('/dashboard') ? 'text-gold-500' : ''
              }`}
            >
              Dashboard
            </Link>
            <Link 
              href="/variants" 
              className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                isActiveRoute('/variants') ? 'text-gold-500' : ''
              }`}
            >
              Variants
            </Link>
            <Link 
              href="/support" 
              className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                isActiveRoute('/support') ? 'text-gold-500' : ''
              }`}
            >
              Support
            </Link>
            <Link 
              href="/compliance" 
              className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                isActiveRoute('/compliance') ? 'text-gold-500' : ''
              }`}
            >
              Compliance
            </Link>
          </nav>

          {/* User Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-gold-500 to-gold-600 flex items-center justify-center">
                    <span className="text-charcoal-900 font-semibold text-sm">
                      {user?.name?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <span className="text-ivory text-sm">{user?.name || 'User'}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-transparent border border-gold-500 text-gold-500 rounded hover:bg-gold-500 hover:text-charcoal-900 transition-all duration-200"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-4 py-2 bg-transparent border border-gold-500 text-gold-500 rounded hover:bg-gold-500 hover:text-charcoal-900 transition-all duration-200"
                >
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="px-4 py-2 bg-gold-500 text-charcoal-900 rounded hover:bg-gold-600 transition-all duration-200"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-ivory"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pt-4 border-t border-charcoal-700">
            <nav className="flex flex-col space-y-4">
              <Link 
                href="/dashboard" 
                className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                  isActiveRoute('/dashboard') ? 'text-gold-500' : ''
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link 
                href="/variants" 
                className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                  isActiveRoute('/variants') ? 'text-gold-500' : ''
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Variants
              </Link>
              <Link 
                href="/support" 
                className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                  isActiveRoute('/support') ? 'text-gold-500' : ''
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Support
              </Link>
              <Link 
                href="/compliance" 
                className={`text-ivory hover:text-gold-500 transition-colors duration-200 ${
                  isActiveRoute('/compliance') ? 'text-gold-500' : ''
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Compliance
              </Link>
              
              <div className="pt-4 border-t border-charcoal-700">
                {isAuthenticated ? (
                  <div className="flex flex-col space-y-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-gold-500 to-gold-600 flex items-center justify-center">
                        <span className="text-charcoal-900 font-semibold text-sm">
                          {user?.name?.charAt(0) || 'U'}
                        </span>
                      </div>
                      <span className="text-ivory text-sm">{user?.name || 'User'}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 bg-transparent border border-gold-500 text-gold-500 rounded hover:bg-gold-500 hover:text-charcoal-900 transition-all duration-200 text-center"
                    >
                      Logout
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col space-y-4">
                    <Link
                      href="/login"
                      className="px-4 py-2 bg-transparent border border-gold-500 text-gold-500 rounded hover:bg-gold-500 hover:text-charcoal-900 transition-all duration-200 text-center"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Login
                    </Link>
                    <Link
                      href="/signup"
                      className="px-4 py-2 bg-gold-500 text-charcoal-900 rounded hover:bg-gold-600 transition-all duration-200 text-center"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Sign Up
                    </Link>
                  </div>
                )}
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
