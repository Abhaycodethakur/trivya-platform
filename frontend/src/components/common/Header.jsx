import React from 'react';
import PropTypes from 'prop-types';

import styles from './Header.module.scss';

/**
 * Premium global header for authenticated areas.
 *
 * Provides branding, quick links, system status, and a sidebar toggle
 * to ensure a consistent experience across desktop and mobile.
 */
const Header = ({ onToggleMenu, isSidebarOpen }) => {
  return (
    <header className={styles.header} role="banner">
      <div className={styles.container}>
        <div className={styles.branding}>
          <div className={styles.logo} aria-hidden="true">
            T
          </div>
          <div>
            <p className={styles.brandTitle}>Trivya Command</p>
            <p className={styles.brandSubtitle}>AI Operations Suite</p>
          </div>
        </div>

        <nav className={styles.quickNav} aria-label="Global quick links">
          <a href="#dashboard">Dashboard</a>
          <a href="#variants">Variants</a>
          <a href="#support">Support</a>
        </nav>

        <div className={styles.actions}>
          <span className={styles.statusPill} role="status">
            Status: Operational
          </span>
          <button
            type="button"
            className={styles.menuButton}
            aria-label="Toggle navigation menu"
            aria-expanded={isSidebarOpen}
            aria-controls="primary-navigation"
            onClick={onToggleMenu}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </header>
  );
};

Header.propTypes = {
  onToggleMenu: PropTypes.func,
  isSidebarOpen: PropTypes.bool,
};

Header.defaultProps = {
  onToggleMenu: () => {},
  isSidebarOpen: false,
};

export default Header;
