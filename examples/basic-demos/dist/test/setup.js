"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.resetMocks = exports.mockConsole = void 0;
const globals_1 = require("@jest/globals");
// Mock console methods for cleaner test output
global.console = {
    ...console,
    log: globals_1.jest.fn(),
    error: globals_1.jest.fn(),
    warn: globals_1.jest.fn(),
    info: globals_1.jest.fn(),
    debug: globals_1.jest.fn(),
};
// Setup test environment
process.env.NODE_ENV = 'test';
// Export test utilities
exports.mockConsole = global.console;
const resetMocks = () => {
    globals_1.jest.clearAllMocks();
};
exports.resetMocks = resetMocks;
//# sourceMappingURL=setup.js.map