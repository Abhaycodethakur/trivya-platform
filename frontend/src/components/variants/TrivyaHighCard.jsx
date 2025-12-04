import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const liquidMetal = keyframes`
  0% { 
    background-position: 0% 0%;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.1), 0 0 10px rgba(212, 175, 55, 0.3);
  }
  50% { 
    background-position: 100% 100%;
    box-shadow: 0 0 25px rgba(0, 212, 255, 0.3), 0 0 20px rgba(212, 175, 55, 0.5);
  }
  100% { 
    background-position: 0% 0%;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.1), 0 0 10px rgba(212, 175, 55, 0.3);
  }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const Styled = {
  Card: styled(motion.article)`
    background: #0A0A0B;
    border-radius: 16px;
    padding: 2rem;
    width: 100%;
    max-width: 450px;
    position: relative;
    overflow: hidden;
    border: 1px solid ${({ isSelected }) => isSelected ? 'rgba(0, 212, 255, 0.7)' : '#1E1E24'};
    transition: all 0.3s ease;
    animation: ${fadeIn} 0.5s ease-out;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #D4AF37, #00D4FF, #D4AF37);
      background-size: 200% 100%;
      animation: ${liquidMetal} 3s ease-in-out infinite;
    }

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      animation: ${pulse} 2s infinite;
    }
  `,
  
  Header: styled.div`
    text-align: center;
    margin-bottom: 1.5rem;
    position: relative;
  `,
  
  Title: styled.h3`
    font-size: 2.25rem;
    background: linear-gradient(90deg, #D4AF37, #F5D76E, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  `,
  
  Subtitle: styled.p`
    color: #00D4FF;
    font-size: 1.5rem;
    margin: 0 0 1.5rem 0;
    font-weight: 600;
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  `,
  
  ValueProp: styled.p`
    color: #E0E0E0;
    font-size: 1.2rem;
    text-align: center;
    margin: 0 0 1.5rem 0;
    font-weight: 500;
    line-height: 1.5;
  `,
  
  FeatureList: styled.ul`
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem 0;
  `,
  
  FeatureItem: styled.li`
    color: #E0E0E0;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    font-size: 1.05rem;
    
    &::before {
      content: '✓';
      color: #00D4FF;
      margin-right: 0.75rem;
      font-weight: bold;
    }
    
    &.highlight {
      color: #FFFFFF;
      font-weight: 600;
      
      &::before {
        color: #D4AF37;
        content: '★';
      }
    }
  `,
  
  Advantage: styled.div`
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(212, 175, 55, 0.1));
    padding: 1rem;
    border-radius: 8px;
    margin: 1.5rem 0;
    border: 1px solid rgba(212, 175, 55, 0.2);
  `,
  
  AdvantageText: styled.p`
    color: #00D4FF;
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;
    text-align: center;
    font-weight: 500;
  `,
  
  Price: styled.div`
    text-align: center;
    margin: 2rem 0 1.5rem;
  `,
  
  Amount: styled.div`
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #D4AF37, #00D4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
  `,
  
  Subtext: styled.p`
    color: #A0A0A0;
    font-size: 0.9rem;
    margin: 0.5rem 0 0 0;
  `,
  
  Button: styled.button`
    background: linear-gradient(135deg, #00D4FF 0%, #0066FF 100%);
    color: #0A0A0B;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    width: 100%;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
    
    &::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: linear-gradient(
        to bottom right,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.1) 50%,
        rgba(255, 255, 255, 0) 100%
      );
      transform: rotate(45deg);
      transition: all 0.6s ease;
    }
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
      
      &::before {
        left: 100%;
      }
    }
    
    &:active {
      transform: translateY(0);
    }
  `,
  
  Savings: styled.div`
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.15), rgba(0, 212, 255, 0.1));
    padding: 1rem;
    border-radius: 8px;
    margin: 1.5rem 0;
    text-align: center;
    border: 1px solid rgba(212, 175, 55, 0.2);
  `,
  
  SavingsText: styled.p`
    color: #D4AF37;
    margin: 0;
    font-size: 1rem;
    font-weight: 500;
  `
};

const TrivyaHighCard = ({ className, onSeeDetails, isSelected = false }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Styled.Card 
      className={className}
      isSelected={isSelected}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      animate={isHovered ? { y: -5 } : { y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
      role="article"
      aria-labelledby="trivya-high-card-title"
    >
      <Styled.Header>
        <Styled.Title id="trivya-high-card-title">
          Trivya High <span style={{ fontSize: '1.5rem' }}>★</span>
        </Styled.Title>
        <Styled.Subtitle>The Senior Agent</Styled.Subtitle>
        
        <motion.div
          initial={{ scale: 0.9, opacity: 0.8 }}
          animate={{ 
            scale: isHovered ? 1 : 0.9, 
            opacity: 1,
            rotate: isHovered ? [0, 5, -5, 0] : 0
          }}
          transition={{ 
            duration: 0.3,
            rotate: { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
          }}
          style={{ margin: '1.5rem 0' }}
        >
          <svg width="160" height="160" viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="80" cy="80" r="75" fill="#1E1E24" />
            <circle cx="80" cy="60" r="25" fill="#00D4FF" />
            <path d="M80 100C100 100 120 108 128 120H32C40 108 60 100 80 100Z" fill="#00D4FF" />
            
            <g transform="translate(80, 80)">
              <g transform="rotate(0) translate(0, -60)">
                <rect x="-12" y="-12" width="24" height="24" rx="5" fill="#D4AF37" />
                <text x="0" y="7" textAnchor="middle" fill="#0A0A0B" fontSize="14" fontWeight="bold">✉️</text>
              </g>
              <g transform="rotate(90) translate(0, -60)">
                <rect x="-12" y="-12" width="24" height="24" rx="5" fill="#D4AF37" />
                <text x="0" y="7" textAnchor="middle" fill="#0A0A0B" fontSize="14" fontWeight="bold">💬</text>
              </g>
              <g transform="rotate(180) translate(0, -60)">
                <rect x="-12" y="-12" width="24" height="24" rx="5" fill="#D4AF37" />
                <text x="0" y="7" textAnchor="middle" fill="#0A0A0B" fontSize="14" fontWeight="bold">📱</text>
              </g>
              <g transform="rotate(270) translate(0, -60)">
                <rect x="-12" y="-12" width="24" height="24" rx="5" fill="#D4AF37" />
                <text x="0" y="7" textAnchor="middle" fill="#0A0A0B" fontSize="14" fontWeight="bold">📞</text>
              </g>
              <g transform="rotate(45) translate(0, -60)">
                <rect x="-12" y="-12" width="24" height="24" rx="5" fill="#00D4FF" />
                <text x="0" y="7" textAnchor="middle" fill="#0A0A0B" fontSize="14" fontWeight="bold">🎥</text>
              </g>
              <g transform="rotate(135) translate(0, -60)">
                <rect x="-12" y="-12" width="24" height="24" rx="5" fill="#00D4FF" />
                <text x="0" y="7" textAnchor="middle" fill="#0A0A0B" fontSize="14" fontWeight="bold">📊</text>
              </g>
            </g>
          </svg>
        </motion.div>
      </Styled.Header>

      <Styled.ValueProp>Replaces 3 senior agents—eliminates 80% of support workload</Styled.ValueProp>

      <Styled.FeatureList>
        <Styled.FeatureItem>Everything Trivya does</Styled.FeatureItem>
        <Styled.FeatureItem className="highlight">5 simultaneous calls</Styled.FeatureItem>
        <Styled.FeatureItem className="highlight">Video support</Styled.FeatureItem>
        <Styled.FeatureItem className="highlight">Strategic Intelligence</Styled.FeatureItem>
      </Styled.FeatureList>

      <Styled.Advantage>
        <Styled.AdvantageText>
          Makes decisions, predicts churn, coordinates with teams
        </Styled.AdvantageText>
      </Styled.Advantage>

      <Styled.Savings>
        <Styled.SavingsText>Auto-saves you: ~$28,000/month in senior agent salaries</Styled.SavingsText>
      </Styled.Savings>

      <Styled.Price>
        <Styled.Amount>$4,000<small style={{ fontSize: '1rem', opacity: 0.8 }}>/month</small></Styled.Amount>
        <Styled.Subtext>(Custom quote after assessment)</Styled.Subtext>
      </Styled.Price>

      <Styled.Button 
        onClick={onSeeDetails}
        aria-label="See full details of Trivya High plan"
      >
        See Full Details
      </Styled.Button>
    </Styled.Card>
  );
};

export default TrivyaHighCard;
