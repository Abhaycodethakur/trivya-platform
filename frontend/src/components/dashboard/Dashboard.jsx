import React from 'react';

import styles from './Dashboard.module.scss';

/**
 * Dashboard Component
 *
 * Provides the primary control center for Trivya customers, showcasing
 * placeholder regions for activity, metrics, usage, and settings while we
 * build the full experience in subsequent phases.
 */
const Dashboard = () => {
  return (
    <section
      className={styles.dashboard}
      aria-label="AI operations dashboard overview"
    >
      <header className={styles.header}>
        <p className={styles.eyebrow}>AI Workforce Command</p>
        <h1>Welcome back, Alex!</h1>
        <p className={styles.subcopy}>
          Here&apos;s the latest look at your agents, performance signals, and
          subscription usage.
        </p>
      </header>

      <div className={styles.grid}>
        <div className={`${styles.card} ${styles.activityFeed}`}>
          <div className={styles.cardHeader}>
            <span className={styles.pill}>Live stream</span>
            <h2>Activity Feed</h2>
          </div>
          <p>
            Real-time agent events will populate this surface. Keep an eye on
            escalations, resolutions, and customer sentiment in one stream.
          </p>
        </div>

        <div className={`${styles.card} ${styles.metricsPanel}`}>
          <div className={styles.cardHeader}>
            <span className={styles.pill}>KPIs</span>
            <h2>Metrics Panel</h2>
          </div>
          <p>
            Key performance indicators, win rates, and SLA coverage will appear
            here once the metrics service is wired in.
          </p>
        </div>

        <div className={`${styles.card} ${styles.settingsPanel}`}>
          <div className={styles.cardHeader}>
            <span className={styles.pill}>Control</span>
            <h2>Settings Panel</h2>
          </div>
          <p>
            Use this panel to adjust workflows, license tiers, and compliance
            toggles. Placeholder buttons will be replaced with live controls.
          </p>
          <div className={styles.settingsActions}>
            <button type="button">Manage Variants</button>
            <button type="button">Update Policies</button>
            <button type="button">Escalation Rules</button>
          </div>
        </div>

        <div className={`${styles.card} ${styles.usageMeter}`}>
          <div className={styles.cardHeader}>
            <span className={styles.pill}>Capacity</span>
            <h2>Usage Meter</h2>
          </div>
          <p>Track how much of your plan allocation has been consumed.</p>
          <div className={styles.meterTrack} aria-live="polite">
            <div className={styles.meterFill} style={{ width: '62%' }} />
          </div>
          <div className={styles.meterLabels}>
            <span>Current Plan</span>
            <span>62% Utilized</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;
