/**
 * Mock License Service
 * 
 * Simulates backend license validation API calls.
 */

export const validateLicense = (licenseKey) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Simulate simple validation logic
            // Valid format: TRIVYA-XXXX-XXXX-XXXX
            const cleanKey = licenseKey.trim().toUpperCase();

            if (!cleanKey) {
                reject({ message: 'License key is required.' });
                return;
            }

            // Mock valid keys
            const validKeys = [
                'TRIVYA-GOLD-2024-KEY1',
                'TRIVYA-ENTR-2024-KEY2',
                'TRIVYA-TEST-1234-5678'
            ];

            if (validKeys.includes(cleanKey)) {
                resolve({
                    isValid: true,
                    type: cleanKey.includes('GOLD') ? 'Gold' : 'Enterprise',
                    expiryDate: '2025-12-31',
                    features: ['advanced_analytics', 'priority_support', 'custom_branding']
                });
            } else if (cleanKey.startsWith('TRIVYA-EXPD')) {
                reject({
                    message: 'This license key has expired. Please renew your subscription.'
                });
            } else {
                reject({
                    message: 'Invalid license key. Please check and try again.'
                });
            }
        }, 1500); // Simulate 1.5 second network delay
    });
};

export default {
    validateLicense
};
