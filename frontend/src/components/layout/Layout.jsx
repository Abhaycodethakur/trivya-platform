import React from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import styles from './Layout.module.css';

/**
 * Main Layout Component
 * 
 * Provides the overall page structure with sidebar navigation and top bar.
 * Uses luxury theme: charcoal background, gold accents, cyan highlights.
 */
const Layout = ({ children }) => {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.mainContent}>
        <TopBar />
        <main className={styles.content}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
