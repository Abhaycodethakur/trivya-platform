module.exports = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
    roots: ['<rootDir>', '<rootDir>/../../frontend/src'],
    modulePaths: ['<rootDir>', '<rootDir>/../../frontend/src'],
    moduleDirectories: ['node_modules', '<rootDir>/../../frontend/src'],
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/$1',
        '\\.module\\.css$': 'identity-obj-proxy',
        '\\.css$': '<rootDir>/__mocks__/styleMock.js',
    },
    testMatch: [
        '**/__tests__/**/*.[jt]s?(x)',
        '**/?(*.)+(spec|test).[jt]s?(x)'
    ],
    collectCoverageFrom: [
        'components/**/*.{js,jsx}',
        'hooks/**/*.{js,jsx}',
        '!**/*.d.ts',
        '!**/node_modules/**',
    ],
    transform: {
        '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
    },
};
