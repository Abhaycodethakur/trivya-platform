import React, { useState } from 'react';
import PropTypes from 'prop-types';

import Header from '../common/Header';
import Sidebar from './Sidebar';
import styles from './Layout.module.scss';

/**
 * Layout component providing the authenticated shell
 * with premium theming, responsive sidebar, and fixed header.
 */
const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleToggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className={styles.layout}>
      <Header onToggleMenu={handleToggleSidebar} isSidebarOpen={isSidebarOpen} />

      <div className={styles.shell}>
        <Sidebar isOpen={isSidebarOpen} onClose={handleToggleSidebar} />

        {isSidebarOpen && (
          <button
            type="button"
            className={styles.overlay}
            onClick={handleToggleSidebar}
            aria-label="Close navigation menu"
          />
        )}

        <main className={styles.content} id="primary-content" role="main">
          {children}
        </main>
      </div>
    </div>
  );
};

Layout.propTypes = {
  children: PropTypes.node,
};

Layout.defaultProps = {
  children: null,
};

export default Layout;
