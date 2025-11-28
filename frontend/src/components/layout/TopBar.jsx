import React, { useState } from 'react';
import styles from './TopBar.module.css';

/**
 * TopBar Component
 * 
 * Displays page title, search, notifications, and user actions.
 * Features luxury theme with gold accents and smooth animations.
 */
const TopBar = () => {
    const [notifications, setNotifications] = useState(3);

    return (
        <header className={styles.topBar}>
            <div className={styles.leftSection}>
                <h2 className={styles.pageTitle}>Dashboard</h2>
            </div>

            <div className={styles.rightSection}>
                <div className={styles.searchContainer}>
                    <input
                        type="text"
                        placeholder="Search..."
                        className={styles.searchInput}
                    />
                    <span className={styles.searchIcon}>🔍</span>
                </div>

                <button className={styles.iconButton} aria-label="Notifications">
                    <span className={styles.icon}>🔔</span>
                    {notifications > 0 && (
                        <span className={styles.badge}>{notifications}</span>
                    )}
                </button>

                <button className={styles.iconButton} aria-label="Help">
                    <span className={styles.icon}>❓</span>
                </button>

                <div className={styles.userMenu}>
                    <button className={styles.userButton}>
                        <span className={styles.userAvatar}>👤</span>
                        <span className={styles.userName}>Admin</span>
                        <span className={styles.dropdownIcon}>▼</span>
                    </button>
                </div>
            </div>
        </header>
    );
};

export default TopBar;
