import React from 'react';
import ActivityFeed from './ActivityFeed';
import MetricsPanel from './MetricsPanel';
import styles from './Dashboard.module.css';

/**
 * Dashboard Component
 * 
 * Main dashboard view displaying metrics, activity feed, and key insights.
 * Features luxury theme with real-time data visualization.
 */
const Dashboard = () => {
    return (
        <div className={styles.dashboard}>
            <div className={styles.header}>
                <h1 className={styles.title}>Welcome to Trivya</h1>
                <p className={styles.subtitle}>AI-Powered Customer Support Platform</p>
            </div>

            <div className={styles.grid}>
                <div className={styles.metricsSection}>
                    <MetricsPanel />
                </div>

                <div className={styles.activitySection}>
                    <ActivityFeed />
                </div>

                <div className={styles.quickActions}>
                    <h3 className={styles.sectionTitle}>Quick Actions</h3>
                    <div className={styles.actionGrid}>
                        <button className={styles.actionCard}>
                            <span className={styles.actionIcon}>🤖</span>
                            <span className={styles.actionLabel}>Deploy AI Agent</span>
                        </button>
                        <button className={styles.actionCard}>
                            <span className={styles.actionIcon}>📚</span>
                            <span className={styles.actionLabel}>Add Knowledge</span>
                        </button>
                        <button className={styles.actionCard}>
                            <span className={styles.actionIcon}>📊</span>
                            <span className={styles.actionLabel}>View Analytics</span>
                        </button>
                        <button className={styles.actionCard}>
                            <span className={styles.actionIcon}>⚙️</span>
                            <span className={styles.actionLabel}>Settings</span>
                        </button>
                    </div>
                </div>

                <div className={styles.insights}>
                    <h3 className={styles.sectionTitle}>AI Insights</h3>
                    <div className={styles.insightCard}>
                        <div className={styles.insightIcon}>💡</div>
                        <div className={styles.insightContent}>
                            <h4>Efficiency Boost</h4>
                            <p>Your AI agents resolved 87% of tickets automatically this week.</p>
                        </div>
                    </div>
                    <div className={styles.insightCard}>
                        <div className={styles.insightIcon}>⚡</div>
                        <div className={styles.insightContent}>
                            <h4>Response Time</h4>
                            <p>Average response time decreased by 45% compared to last month.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
