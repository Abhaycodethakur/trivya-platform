import React from 'react';

import styles from './MetricsPanel.module.scss';

/**
 * MetricsPanel Component
 *
 * Highlights key KPIs for the Trivya AI workforce using premium placeholder
 * data until backend integrations are complete.
 */
const MetricsPanel = () => {
  const metrics = [
    {
      id: 'tickets',
      label: 'Tickets Resolved',
      value: '1,248',
      trend: '+12%',
      trendLabel: 'up',
    },
    {
      id: 'response',
      label: 'Avg. Response Time',
      value: '45s',
      trend: '-8%',
      trendLabel: 'down',
    },
    {
      id: 'csat',
      label: 'Customer Satisfaction',
      value: '98.5%',
      trend: '+2%',
      trendLabel: 'up',
    },
    {
      id: 'savings',
      label: 'Monthly Cost Savings',
      value: '$4,250',
      trend: '+19%',
      trendLabel: 'up',
    },
  ];

  return (
    <section className={styles.metricsPanel} aria-label="Performance metrics">
      <header className={styles.header}>
        <p className={styles.eyebrow}>Signals</p>
        <h2>Performance Metrics</h2>
        <p className={styles.subcopy}>
          These indicators summarize how your AI workforce is performing right
          now across speed, satisfaction, and cost.
        </p>
      </header>

      <div className={styles.metricsGrid}>
        {metrics.map((metric) => (
          <article
            key={metric.id}
            className={styles.metricCard}
            data-testid="metric-card"
          >
            <div className={styles.metricLabel}>{metric.label}</div>
            <div className={styles.metricValue}>{metric.value}</div>
            <div
              className={`${styles.metricTrend} ${styles[metric.trendLabel]}`}
              data-testid="metric-trend"
            >
              {metric.trendLabel === 'up' ? '▲' : '▼'} {metric.trend}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};

export default MetricsPanel;
