// Mock useAuth hook
export const useAuth = () => ({
    user: null,
    isAuthenticated: false,
    login: async () => { },
    logout: async () => { },
    loading: false,
});
