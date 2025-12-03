import React from 'react';

import Layout from '../components/layout/Layout';
import styles from './VariantsPage.module.scss';

/**
 * VariantsPage Component
 *
 * Presents the available Trivya AI workforce tiers inside the primary layout,
 * using premium placeholder cards until full data integrations are complete.
 */
const VariantsPage = () => {
  const variantCards = [
    {
      id: 'mini',
      title: 'Mini Trivya',
      subtitle: 'The 24/7 Trainee',
      label: 'Mini Trivya Card',
    },
    {
      id: 'trivya',
      title: 'Trivya',
      subtitle: 'The Autonomous Junior',
      label: 'Trivya Card',
    },
    {
      id: 'trivya-high',
      title: 'Trivya High',
      subtitle: 'The Elite Strategist',
      label: 'Trivya High Card',
    },
  ];

  return (
    <Layout>
      <section className={styles.variantsPage} aria-label="Variants overview">
        <header className={styles.header}>
          <p className={styles.eyebrow}>AI Workforce Catalog</p>
          <h1>Choose Your AI Workforce</h1>
          <p className={styles.subcopy}>
            Compare tiers, preview capabilities, and tailor the workforce that fits
            your customer operations.
          </p>
        </header>

        <div className={styles.cardsWrapper}>
          {variantCards.map((card) => (
            <article key={card.id} className={`${styles.card} ${styles[card.id]}`}>
              <span className={styles.placeholderLabel}>{card.label}</span>
              <h2>{card.title}</h2>
              <p>{card.subtitle}</p>
              <button type="button">See Full Details</button>
            </article>
          ))}
        </div>
      </section>
    </Layout>
  );
};

export default VariantsPage;
