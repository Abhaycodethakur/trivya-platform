/**
 * Mock Auth Service
 * 
 * Simulates backend authentication API calls.
 */

export const login = (email, password) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Simulate simple validation
            if (email === 'test@example.com' && password === 'password') {
                resolve({
                    id: 1,
                    name: 'Test User',
                    email: 'test@example.com',
                    token: 'fake-jwt-token-123456'
                });
            } else {
                reject({
                    message: 'Invalid credentials. Please check your email and password.'
                });
            }
        }, 1000); // Simulate 1 second network delay
    });
};

export const signup = (name, email, password) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Simulate simple validation
            if (email === 'exists@example.com') {
                reject({
                    message: 'Email already exists. Please use a different email.'
                });
            } else {
                resolve({
                    id: Math.floor(Math.random() * 1000),
                    name: name,
                    email: email,
                    token: 'fake-jwt-token-' + Date.now()
                });
            }
        }, 1500); // Simulate 1.5 second network delay for signup
    });
};

export default {
    login,
    signup
};
