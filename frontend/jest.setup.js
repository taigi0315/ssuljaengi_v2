import '@testing-library/jest-dom';

// Polyfill for Next.js API routes in Jest
global.Request = global.Request || require('node-fetch').Request;
global.Response = global.Response || require('node-fetch').Response;
global.Headers = global.Headers || require('node-fetch').Headers;
global.fetch = global.fetch || require('node-fetch');

// Mock AbortController if not available
if (!global.AbortController) {
  global.AbortController = class AbortController {
    signal = {
      aborted: false,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    };
    abort = jest.fn(() => {
      this.signal.aborted = true;
    });
  };
}
