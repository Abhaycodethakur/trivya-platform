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
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
  }
  50% { 
    background-position: 100% 100%;
    box-shadow: 0 0 25px rgba(0, 212, 255, 0.3);
  }
  100% { 
    background-position: 0% 0%;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
  }
`;

const Card = styled(motion.article)`
  background: #0A0A0B;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 420px;
  position: relative;
  overflow: hidden;
  border: 1px solid ${({ isSelected }) => isSelected ? '#00D4FF' : '#1E1E24'};
  transition: all 0.3s ease;
  animation: ${fadeIn} 0.5s ease-out;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #D4AF37, #F5D76E, #D4AF37);
    background-size: 200% 100%;
    animation: ${liquidMetal} 3s ease-in-out infinite;
  }

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
`;

const Title = styled.h3`
  font-size: 2rem;
  color: #D4AF37;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
`;

const Subtitle = styled.p`
  color: #00D4FF;
  font-size: 1.25rem;
  margin: 0 0 1.5rem 0;
  font-weight: 500;
`;

const ValueProp = styled.p`
  color: #E0E0E0;
  font-size: 1.1rem;
  text-align: center;
  margin: 0 0 1.5rem 0;
  font-weight: 500;
  line-height: 1.5;
`;

const FeatureList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem 0;
`;

const FeatureItem = styled.li`
  color: #E0E0E0;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  font-size: 1rem;
  
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
    }
  }
`;

const Advantage = styled.div`
  background: rgba(0, 212, 255, 0.1);
  padding: 1rem;
  border-radius: 8px;
  margin: 1.5rem 0;
`;

const AdvantageText = styled.p`
  color: #00D4FF;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  text-align: center;
`;

const Price = styled.div`
  text-align: center;
  margin: 2rem 0 1.5rem;
`;

const Amount = styled.div`
  font-size: 2.75rem;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.2;
`;

const Subtext = styled.p`
  color: #A0A0A0;
  font-size: 0.9rem;
  margin: 0.5rem 0 0 0;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #00D4FF 0%, #0066FF 100%);
  color: #0A0A0B;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  width: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const Savings = styled.div`
  background: rgba(212, 175, 55, 0.1);
  padding: 0.75rem;
  border-radius: 8px;
  margin: 1.5rem 0;
  text-align: center;
`;

const SavingsText = styled.p`
  color: #D4AF37;
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
`;

const TrivyaCard = ({ className, onSeeDetails, isSelected = false }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card 
      className={className}
      isSelected={isSelected}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      animate={isHovered ? { y: -5 } : { y: 0 }}
      transition={{ type: 'spring', stiffness: 300 }}
      role="article"
      aria-labelledby="trivya-card-title"
    >
      <Header>
        <Title id="trivya-card-title">Trivya</Title>
        <Subtitle>The Junior Agent</Subtitle>
        
        <motion.div
          initial={{ scale: 0.9, opacity: 0.8 }}
          animate={{ scale: isHovered ? 1 : 0.9, opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={{ margin: '1.5rem 0' }}
        >
          <svg width="140" height="140" viewBox="0 0 140 140" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="70" cy="70" r="65" fill="#1E1E24" />
            <circle cx="70" cy="50" r="20" fill="#00D4FF" />
            <path d="M70 85C85 85 100 92 107 105H33C40 92 55 85 70 85Z" fill="#00D4FF" />
            
            {/* Channel Icons */}
            <g transform="translate(70, 70)">
              <g transform="rotate(0) translate(0, -55)">
                <rect x="-10" y="-10" width="20" height="20" rx="4" fill="#D4AF37" />
                <text x="0" y="6" textAnchor="middle" fill="#0A0A0B" fontSize="12" fontWeight="bold">✉️</text>
              </g>
              <g transform="rotate(90) translate(0, -55)">
                <rect x="-10" y="-10" width="20" height="20" rx="4" fill="#D4AF37" />
                <text x="0" y="6" textAnchor="middle" fill="#0A0A0B" fontSize="12" fontWeight="bold">💬</text>
              </g>
              <g transform="rotate(180) translate(0, -55)">
                <rect x="-10" y="-10" width="20" height="20" rx="4" fill="#D4AF37" />
                <text x="0" y="6" textAnchor="middle" fill="#0A0A0B" fontSize="12" fontWeight="bold">📱</text>
              </g>
              <g transform="rotate(270) translate(0, -55)">
                <rect x="-10" y="-10" width="20" height="20" rx="4" fill="#D4AF37" />
                <text x="0" y="6" textAnchor="middle" fill="#0A0A0B" fontSize="12" fontWeight="bold">📞</text>
              </g>
              <g transform="rotate(45) translate(0, -55)">
                <rect x="-10" y="-10" width="20" height="20" rx="4" fill="#00D4FF" />
                <text x="0" y="6" textAnchor="middle" fill="#0A0A0B" fontSize="12" fontWeight="bold">🧠</text>
              </g>
            </g>
          </svg>
        </motion.div>
      </Header>

      <ValueProp>Replaces 3 junior agents—resolves 70% of issues without you</ValueProp>

      <FeatureList>
        <FeatureItem>Everything Mini does</FeatureItem>
        <FeatureItem className="highlight">3 simultaneous calls</FeatureItem>
        <FeatureItem className="highlight">"Thinks for you"</FeatureItem>
      </FeatureList>

      <Advantage>
        <AdvantageText>
          Detects patterns, suggests KB updates, cuts review time by 80%
        </AdvantageText>
      </Advantage>

      <Savings>
        <SavingsText>Auto-saves you: ~$18,000/month in junior agent salaries</SavingsText>
      </Savings>

      <Price>
        <Amount>$2,500<small style={{ fontSize: '1rem', opacity: 0.8 }}>/month</small></Amount>
        <Subtext>(Custom quote after assessment)</Subtext>
      </Price>

      <Button 
        onClick={onSeeDetails}
        aria-label="See full details of Trivya plan"
      >
        See Full Details
      </Button>
    </Card>
  );
};

export default TrivyaCard;
