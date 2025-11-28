import React from 'react';
import PropTypes from 'prop-types';
import styles from './Loading.module.css';

/**
 * Loading Component
 * 
 * A reusable loading indicator that supports spinner and skeleton types.
 * Adheres to the Trivya luxury design system.
 */
const Loading = ({ size = 'medium', message, type = 'spinner' }) => {
  // Error Boundary fallback could be implemented here or in a parent wrapper.
  // For this component, we ensure safe rendering.

  const containerClass = styles.container;
  const sizeClass = styles[size];
  const typeClass = styles[type];

  return (
    <div 
      className={containerClass}
      role="status"
      aria-live="polite"
      aria-busy="true"
      aria-label={message || "Loading"}
    >
      <div className={`${typeClass} ${sizeClass}`} />
      {message && <span className={styles.message}>{message}</span>}
    </div>
  );
};

Loading.propTypes = {
  /**
   * Size of the loading indicator
   */
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  /**
   * Optional message to display below the spinner
   */
  message: PropTypes.string,
  /**
   * Type of loading indicator
   */
  type: PropTypes.oneOf(['spinner', 'skeleton']),
};

export default Loading;
