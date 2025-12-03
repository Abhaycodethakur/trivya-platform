import React from 'react';
import PropTypes from 'prop-types';

import styles from './Sidebar.module.css';

/**
 * Sidebar Navigation Component
 *
 * Provides premium navigation with a luxury theme, placeholder links,
 * and responsive behavior for mobile layouts.
 */
const Sidebar = ({ isOpen, onClose }) => {
    const navItems = [
        { href: '#dashboard', icon: '📊', label: 'Dashboard' },
        { href: '#variants', icon: '🤖', label: 'Variants' },
        { href: '#support', icon: '💬', label: 'Support' },
        { href: '#workflows', icon: '⚙️', label: 'Workflows' },
        { href: '#insights', icon: '📈', label: 'Insights' },
    ];

    const sidebarClass = [styles.sidebar];
    if (isOpen) {
        sidebarClass.push(styles.open);
    }

    const handleNavClick = () => {
        if (typeof onClose === 'function') {
            onClose();
        }
    };

    return (
        <aside className={sidebarClass.join(' ')} aria-label="Primary navigation">
            <div className={styles.logo}>
                <div>
                    <p className={styles.logoText}>Trivya</p>
                    <p className={styles.logoSubtext}>Command Suite</p>
                </div>
                <button
                    type="button"
                    className={styles.mobileClose}
                    onClick={onClose}
                    aria-label="Close navigation menu"
                >
                    ×
                </button>
            </div>

            <nav
                className={styles.nav}
                id="primary-navigation"
                aria-label="Primary navigation"
            >
                {navItems.map((item) => (
                    <a
                        key={item.label}
                        href={item.href}
                        className={styles.navItem}
                        onClick={handleNavClick}
                    >
                        <span className={styles.icon}>{item.icon}</span>
                        <span className={styles.label}>{item.label}</span>
                    </a>
                ))}
            </nav>

            <div className={styles.footer}>
                <div className={styles.userInfo}>
                    <div className={styles.avatar}>👤</div>
                    <div className={styles.userDetails}>
                        <p className={styles.userName}>Aria Stern</p>
                        <p className={styles.userRole}>Customer Lead</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

Sidebar.propTypes = {
    isOpen: PropTypes.bool,
    onClose: PropTypes.func,
};

Sidebar.defaultProps = {
    isOpen: false,
    onClose: undefined,
};

export default Sidebar;
