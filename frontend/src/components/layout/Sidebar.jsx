import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './Sidebar.module.css';

/**
 * Sidebar Navigation Component
 * 
 * Provides main navigation with luxury theme styling.
 * Features: gold accents, smooth transitions, active state highlighting.
 */
const Sidebar = () => {
    const location = useLocation();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const navItems = [
        { path: '/dashboard', icon: '📊', label: 'Dashboard' },
        { path: '/variants', icon: '🤖', label: 'AI Variants' },
        { path: '/knowledge', icon: '📚', label: 'Knowledge Base' },
        { path: '/analytics', icon: '📈', label: 'Analytics' },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
        { path: '/compliance', icon: '🔒', label: 'Compliance' },
    ];

    return (
        <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
            <div className={styles.logo}>
                <h1 className={styles.logoText}>Trivya</h1>
                <button
                    className={styles.collapseBtn}
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    aria-label="Toggle sidebar"
                >
                    {isCollapsed ? '→' : '←'}
                </button>
            </div>

            <nav className={styles.nav}>
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`${styles.navItem} ${location.pathname === item.path ? styles.active : ''
                            }`}
                    >
                        <span className={styles.icon}>{item.icon}</span>
                        {!isCollapsed && <span className={styles.label}>{item.label}</span>}
                    </Link>
                ))}
            </nav>

            <div className={styles.footer}>
                {!isCollapsed && (
                    <div className={styles.userInfo}>
                        <div className={styles.avatar}>👤</div>
                        <div className={styles.userDetails}>
                            <p className={styles.userName}>User Name</p>
                            <p className={styles.userRole}>Admin</p>
                        </div>
                    </div>
                )}
            </div>
        </aside>
    );
};

export default Sidebar;
