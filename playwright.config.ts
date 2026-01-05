import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  
  // Timeout for each test in milliseconds
  timeout: 60 * 1000, // 60 seconds
  
  // Retry on failure for CI environments
  retries: process.env.CI ? 2 : 0,
  
  // Number of workers to use when running tests in parallel
  workers: process.env.CI ? 2 : undefined,
  
  // Reporter to use. See https://playwright.dev/docs/test-reporters
  reporter: 'html',
  
  use: {
    // Base URL to use in actions like `await page.goto('/')`.
    baseURL: 'http://localhost:3000', // Assuming Next.js app runs on this port
    
    // Collect trace when retrying the first time.
    trace: 'on-first-retry',
    
    // Capture screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video recording
    video: 'on-first-retry'
  },
  
  // Configure projects for different browsers
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } }
  ],
  
  // Start a dev server before running the tests
  webServer: {
    command: 'npm run dev', // Command to start your Next.js development server
    port: 3000,
    timeout: 120 * 1000, // 120 seconds for the server to start
    reuseExistingServer: !process.env.CI, // Reuse server if not in CI
  }
});
