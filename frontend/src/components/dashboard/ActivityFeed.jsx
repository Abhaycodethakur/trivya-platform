import React from 'react';
import styles from './ActivityFeed.module.css';

/**
 * ActivityFeed Component
 * 
 * Displays recent activity and events in the system.
 * Features luxury theme with real-time updates.
 */
const ActivityFeed = () => {
    const activities = [
        {
            id: 1,
            type: 'success',
            icon: '✅',
            title: 'Ticket Resolved',
            description: 'AI Agent resolved ticket #1234',
            time: '2 minutes ago',
        },
        {
            id: 2,
            type: 'info',
            icon: '📚',
            title: 'Knowledge Updated',
            description: 'New FAQ added to knowledge base',
            time: '15 minutes ago',
        },
        {
            id: 3,
            type: 'warning',
            icon: '⚠️',
            title: 'High Priority',
            description: 'Ticket #5678 escalated to human',
            time: '1 hour ago',
        },
        {
            id: 4,
            type: 'success',
            icon: '🤖',
            title: 'Agent Deployed',
            description: 'Mini Trivya agent activated',
            time: '2 hours ago',
        },
        {
            id: 5,
            type: 'info',
            icon: '📊',
            title: 'Report Generated',
            description: 'Weekly analytics report ready',
            time: '3 hours ago',
        },
    ];

    return (
        <div className={styles.activityFeed}>
            <h3 className={styles.title}>Recent Activity</h3>
            <div className={styles.feedList}>
                {activities.map((activity) => (
                    <div key={activity.id} className={`${styles.activityItem} ${styles[activity.type]}`}>
                        <div className={styles.iconContainer}>
                            <span className={styles.icon}>{activity.icon}</span>
                        </div>
                        <div className={styles.content}>
                            <h4 className={styles.activityTitle}>{activity.title}</h4>
                            <p className={styles.description}>{activity.description}</p>
                            <span className={styles.time}>{activity.time}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ActivityFeed;
