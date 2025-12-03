import React from 'react';

import styles from './SettingsPanel.module.scss';

/**
 * SettingsPanel Component
 *
 * Provides quick access to essential AI workforce configuration areas with
 * premium placeholder actions until backend wiring is complete.
 */
const SettingsPanel = () => {
  const settings = [
    {
      id: 'general',
      icon: '⚙️',
      title: 'General Settings',
      description: 'Configure brand, contact, and authentication preferences.',
    },
    {
      id: 'team',
      icon: '👥',
      title: 'Team Management',
      description: 'Invite, remove, and manage agent and admin roles.',
    },
    {
      id: 'notifications',
      icon: '🔔',
      title: 'Notification Preferences',
      description: 'Control real-time alerts, escalations, and summaries.',
    },
    {
      id: 'compliance',
      icon: '🛡️',
      title: 'Compliance & Escalations',
      description: 'Adjust safety policies, escalation paths, and audits.',
    },
  ];

  return (
    <section className={styles.settingsPanel} aria-label="Quick settings">
      <header className={styles.header}>
        <p className={styles.eyebrow}>Controls</p>
        <h2>Quick Settings</h2>
        <p className={styles.subcopy}>
          Fine-tune how Trivya behaves across teams, notifications, and
          compliance without leaving the dashboard.
        </p>
      </header>

      <div className={styles.settingsList}>
        {settings.map((setting) => (
          <button
            key={setting.id}
            type="button"
            className={styles.settingItem}
            data-testid="setting-option"
          >
            <span className={styles.icon} aria-hidden="true">
              {setting.icon}
            </span>
            <div className={styles.copy}>
              <span className={styles.title}>{setting.title}</span>
              <span className={styles.description}>{setting.description}</span>
            </div>
            <span className={styles.chevron} aria-hidden="true">
              ↗
            </span>
          </button>
        ))}
      </div>
    </section>
  );
};

export default SettingsPanel;
