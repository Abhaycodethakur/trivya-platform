import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import { Slider, Typography, Button, Table, TableBody, TableCell, TableContainer, TableRow, Paper, Box } from '@mui/material';

// Animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
`;

// Styled Components
const Container = styled.div`
  background: #0A0A0B;
  border-radius: 16px;
  padding: 2rem;
  max-width: 1000px;
  margin: 2rem auto;
  border: 1px solid #1E1E24;
  animation: ${fadeIn} 0.5s ease-out;
`;

const Title = styled.h2`
  color: #E0E0E0;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  background: linear-gradient(90deg, #D4AF37, #00D4FF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const SliderContainer = styled.div`
  padding: 1rem 2rem;
  margin: 2rem 0;
  background: rgba(30, 30, 36, 0.7);
  border-radius: 12px;
`;

const SliderLabel = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: #E0E0E0;
`;

const BundleContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
  margin: 2rem 0;
`;

const BundleCard = styled(motion.div)`
  background: #1E1E24;
  border-radius: 12px;
  padding: 1.5rem;
  flex: 1;
  min-width: 280px;
  max-width: 320px;
  border: 2px solid ${({ isRecommended }) => isRecommended ? '#00D4FF' : 'transparent'};
  box-shadow: ${({ isRecommended }) => isRecommended ? '0 0 20px rgba(0, 212, 255, 0.3)' : 'none'};
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }
`;

const BundleTitle = styled.h3`
  color: #E0E0E0;
  font-size: 1.5rem;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Price = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #D4AF37;
  margin: 1rem 0;
`;

const FeatureList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 1rem 0;
`;

const FeatureItem = styled.li`
  color: #E0E0E0;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &::before {
    content: '✓';
    color: #00D4FF;
    font-weight: bold;
  }
`;

const Badge = styled.span`
  background: ${({ type }) => type === 'recommended' ? '#00D4FF' : '#D4AF37'};
  color: #0A0A0B;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-left: 0.5rem;
`;

const ComparisonButton = styled(Button)`
  margin: 1rem 0;
  background: linear-gradient(135deg, #00D4FF 0%, #0066FF 100%);
  color: #0A0A0B;
  font-weight: 600;
  text-transform: none;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  
  &:hover {
    background: linear-gradient(135deg, #00C4EB 0%, #0055D9 100%);
  }
`;

const ComparisonTable = styled(TableContainer)`
  margin: 2rem 0;
  background: #1E1E24;
  border-radius: 12px;
  overflow: hidden;
  animation: ${fadeIn} 0.3s ease-out;
`;

const TableHeader = styled(TableCell)`
  background: #2A2A35 !important;
  color: #E0E0E0 !important;
  font-weight: 600 !important;
  border-bottom: 2px solid #3A3A45 !important;
`;

const TableCellStyled = styled(TableCell)`
  color: #E0E0E0 !important;
  border-bottom: 1px solid #3A3A45 !important;
`;

const HighlightCell = styled(TableCell)`
  color: #00D4FF !important;
  font-weight: 600 !important;
  border-bottom: 1px solid #3A3A45 !important;
`;

// Bundle configurations
const BUNDLES = {
  mini: {
    id: 'mini',
    name: 'Mini Trivya',
    price: 1000,
    capacity: 200,
    managerTime: 4,
    features: [
      'Handles up to 200 tickets/day',
      'Basic automation',
      'Email & chat support',
      '8/5 availability'
    ]
  },
  trivya: {
    id: 'trivya',
    name: 'Trivya',
    price: 2500,
    capacity: 400,
    managerTime: 0.5,
    features: [
      'Handles up to 400 tickets/day',
      'Advanced automation',
      'Multi-channel support',
      '24/7 availability',
      'Pattern learning',
      'Basic analytics'
    ]
  },
  trivyaHigh: {
    id: 'trivyaHigh',
    name: 'Trivya High',
    price: 4000,
    capacity: 1000,
    managerTime: 0.25,
    features: [
      'Handles 1000+ tickets/day',
      'Premium automation',
      'Omni-channel support',
      '24/7 availability',
      'Advanced AI learning',
      'Comprehensive analytics',
      'Dedicated account manager'
    ]
  }
};

const SmartBundleVisualizer = () => {
  const [ticketVolume, setTicketVolume] = useState(200);
  const [recommendedBundle, setRecommendedBundle] = useState('mini');
  const [showComparison, setShowComparison] = useState(false);

  // Calculate recommended bundle based on ticket volume
  useEffect(() => {
    if (ticketVolume <= 200) {
      setRecommendedBundle('mini');
    } else if (ticketVolume <= 400) {
      setRecommendedBundle('trivya');
    } else {
      setRecommendedBundle('trivyaHigh');
    }
  }, [ticketVolume]);

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Get bundles to display based on ticket volume
  const getDisplayBundles = () => {
    if (ticketVolume <= 200) {
      return [BUNDLES.mini, BUNDLES.trivya];
    } else if (ticketVolume <= 400) {
      return [BUNDLES.mini, BUNDLES.trivya];
    } else {
      return [BUNDLES.trivya, BUNDLES.trivyaHigh];
    }
  };

  // Calculate savings
  const calculateSavings = (bundle1, bundle2) => {
    const ticketsPerBundle1 = Math.ceil(ticketVolume / bundle1.capacity);
    const ticketsPerBundle2 = Math.ceil(ticketVolume / bundle2.capacity);
    const cost1 = bundle1.price * ticketsPerBundle1;
    const cost2 = bundle2.price * ticketsPerBundle2;
    return Math.abs(cost1 - cost2);
  };

  const displayBundles = getDisplayBundles();
  const bundle1 = displayBundles[0];
  const bundle2 = displayBundles[1];
  const showSavings = ticketVolume > 200;
  const savings = showSavings ? calculateSavings(bundle1, bundle2) : 0;

  return (
    <Container>
      <Title>Smart Bundle Visualizer</Title>
      
      <SliderContainer>
        <SliderLabel>
          <span>Estimated Daily Ticket Volume: <strong>{ticketVolume}</strong></span>
          <span>Recommended: <strong>{BUNDLES[recommendedBundle].name}</strong></span>
        </SliderLabel>
        <Slider
          value={ticketVolume}
          onChange={(e, newValue) => setTicketVolume(newValue)}
          min={50}
          max={1000}
          step={10}
          valueLabelDisplay="auto"
          aria-labelledby="ticket-volume-slider"
          sx={{
            color: '#00D4FF',
            '& .MuiSlider-thumb': {
              '&:hover, &.Mui-focusVisible': {
                boxShadow: '0 0 0 8px rgba(0, 212, 255, 0.16)',
              },
            },
            '& .MuiSlider-rail': {
              backgroundColor: '#3A3A45',
            },
            '& .MuiSlider-track': {
              background: 'linear-gradient(90deg, #D4AF37, #00D4FF)',
            },
          }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span style={{ color: '#A0A0A0' }}>50</span>
          <span style={{ color: '#A0A0A0' }}>1000+</span>
        </div>
      </SliderContainer>

      {showSavings && (
        <div style={{ 
          textAlign: 'center', 
          margin: '1rem 0',
          padding: '1rem',
          background: 'rgba(0, 212, 255, 0.1)',
          borderRadius: '8px',
          borderLeft: '4px solid #00D4FF'
        }}>
          <Typography variant="body1" style={{ color: '#00D4FF' }}>
            You could save up to {formatCurrency(savings)}/month by choosing {BUNDLES[recommendedBundle].name} for your volume!
          </Typography>
        </div>
      )}

      <BundleContainer>
        {displayBundles.map((bundle) => (
          <BundleCard 
            key={bundle.id}
            isRecommended={bundle.id === recommendedBundle}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <BundleTitle>
              {bundle.name}
              {bundle.id === recommendedBundle && (
                <Badge type="recommended">Recommended</Badge>
              )}
            </BundleTitle>
            
            <Price>{formatCurrency(bundle.price)}<small style={{ fontSize: '1rem', opacity: 0.8 }}>/month</small></Price>
            
            <FeatureList>
              {bundle.features.map((feature, index) => (
                <FeatureItem key={index}>{feature}</FeatureItem>
              ))}
            </FeatureList>
            
            <div style={{ 
              marginTop: '1rem',
              padding: '0.75rem',
              background: 'rgba(212, 175, 55, 0.1)',
              borderRadius: '8px',
              borderLeft: '3px solid #D4AF37'
            }}>
              <Typography variant="body2" style={{ color: '#D4AF37' }}>
                <strong>Manager Time:</strong> ~{bundle.managerTime} hrs/day
              </Typography>
            </div>
            
            <div style={{ 
              marginTop: '1rem',
              padding: '0.75rem',
              background: 'rgba(0, 212, 255, 0.1)',
              borderRadius: '8px',
              borderLeft: '3px solid #00D4FF'
            }}>
              <Typography variant="body2" style={{ color: '#00D4FF' }}>
                <strong>Capacity:</strong> Up to {bundle.capacity} tickets/day
              </Typography>
            </div>
          </BundleCard>
        ))}
      </BundleContainer>

      <div style={{ textAlign: 'center', margin: '2rem 0' }}>
        <ComparisonButton 
          variant="contained" 
          onClick={() => setShowComparison(!showComparison)}
        >
          {showComparison ? 'Hide Comparison' : 'Compare Bundles'}
        </ComparisonButton>
      </div>

      {showComparison && (
        <ComparisonTable component={Paper}>
          <Table>
            <TableBody>
              <TableRow>
                <TableHeader>Feature</TableHeader>
                <TableHeader align="right">{bundle1.name}</TableHeader>
                <TableHeader align="right">{bundle2.name}</TableHeader>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Monthly Cost</TableCellStyled>
                <TableCellStyled align="right">{formatCurrency(bundle1.price)}</TableCellStyled>
                <TableCellStyled align="right">{formatCurrency(bundle2.price)}</TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Daily Capacity</TableCellStyled>
                <TableCellStyled align="right">{bundle1.capacity} tickets</TableCellStyled>
                <TableCellStyled align="right">{bundle2.capacity} tickets</TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Manager Time</TableCellStyled>
                <TableCellStyled align="right">{bundle1.managerTime} hrs/day</TableCellStyled>
                <TableCellStyled align="right">{bundle2.managerTime} hrs/day</TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Support</TableCellStyled>
                <TableCellStyled align="right">
                  {bundle1.features.includes('24/7 availability') ? '24/7' : 'Business Hours'}
                </TableCellStyled>
                <TableCellStyled align="right">
                  {bundle2.features.includes('24/7 availability') ? '24/7' : 'Business Hours'}
                </TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>AI Learning</TableCellStyled>
                <TableCellStyled align="right">
                  {bundle1.features.includes('Pattern learning') ? 'Basic' : 'Limited'}
                </TableCellStyled>
                <TableCellStyled align="right">
                  {bundle2.features.includes('Advanced AI learning') ? 'Advanced' : 
                   bundle2.features.includes('Pattern learning') ? 'Standard' : 'Basic'}
                </TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Best For</TableCellStyled>
                <TableCellStyled align="right">
                  {bundle1.id === 'mini' ? 'Small businesses' : 
                   bundle1.id === 'trivya' ? 'Growing businesses' : 'Enterprises'}
                </TableCellStyled>
                <TableCellStyled align="right">
                  {bundle2.id === 'trivya' ? 'Growing businesses' : 'Enterprises'}
                </TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Estimated Monthly Cost</TableCellStyled>
                <TableCellStyled align="right">
                  {formatCurrency(Math.ceil(ticketVolume / bundle1.capacity) * bundle1.price)}
                  <div style={{ fontSize: '0.8rem', color: '#A0A0A0' }}>
                    ({Math.ceil(ticketVolume / bundle1.capacity)} × {formatCurrency(bundle1.price)})
                  </div>
                </TableCellStyled>
                <TableCellStyled align="right">
                  {formatCurrency(Math.ceil(ticketVolume / bundle2.capacity) * bundle2.price)}
                  <div style={{ fontSize: '0.8rem', color: '#A0A0A0' }}>
                    ({Math.ceil(ticketVolume / bundle2.capacity)} × {formatCurrency(bundle2.price)})
                  </div>
                </TableCellStyled>
              </TableRow>
              
              <TableRow>
                <TableCellStyled>Savings</TableCellStyled>
                <TableCellStyled colSpan={2} align="center" style={{ color: '#D4AF37', fontWeight: 'bold' }}>
                  {formatCurrency(savings)} {savings > 0 ? 'savings with ' + (bundle1.price < bundle2.price ? bundle1.name : bundle2.name) : 'No significant savings'}
                </TableCellStyled>
              </TableRow>
            </TableBody>
          </Table>
        </ComparisonTable>
      )}
      
      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <Typography variant="body2" style={{ color: '#A0A0A0' }}>
          * All prices are estimates. Contact us for a custom quote based on your specific needs.
        </Typography>
      </div>
    </Container>
  );
};

export default SmartBundleVisualizer;
