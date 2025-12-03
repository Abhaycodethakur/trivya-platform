import React from 'react';

import styles from './ActivityFeed.module.scss';

/**
 * ActivityFeed Component
 *
 * Presents a live snapshot of AI agent events with premium styling. This
 * placeholder version lists representative activities until real-time data is
 * wired in.
 */
const ActivityFeed = () => {
  const activities = [
    {
      id: 'resolved',
      status: 'success',
      label: 'AI resolved FAQ #1234',
      timestamp: '2 minutes ago',
    },
    {
      id: 'call',
      status: 'processing',
      label: 'Live call from +1-555-1234',
      timestamp: '7 minutes ago',
    },
    {
      id: 'escalated',
      status: 'warning',
      label: 'Escalated ticket #5678 to human',
      timestamp: '18 minutes ago',
    },
    {
      id: 'training',
      status: 'success',
      label: 'Mini Trivya ingested 20 new FAQs',
      timestamp: '33 minutes ago',
    },
    {
      id: 'policy',
      status: 'processing',
      label: 'Policy alignment check running for Trivya High',
      timestamp: '1 hour ago',
    },
    {
      id: 'audit',
      status: 'warning',
      label: 'Compliance audit flagged 3 conversations',
      timestamp: '2 hours ago',
    },
  ];

  return (
    <section className={styles.activityFeed} aria-label="Live activity feed">
      <header className={styles.header}>
        <p className={styles.eyebrow}>Live Stream</p>
        <h2>Activity Feed</h2>
        <p className={styles.subcopy}>
          Monitor escalations, successful resolutions, and live calls as they
          flow through your AI workforce.
        </p>
      </header>

      <div className={styles.feedList}>
        {activities.map((activity) => (
          <article
            key={activity.id}
            className={styles.activityItem}
            data-testid="activity-entry"
          >
            <span
              className={`${styles.statusDot} ${styles[activity.status]}`}
              aria-label={`${activity.status} status indicator`}
              data-testid="status-indicator"
              data-status={activity.status}
            />
            <div className={styles.entryContent}>
              <p>{activity.label}</p>
              <span>{activity.timestamp}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};

export default ActivityFeed;
