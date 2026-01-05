import { test, expect } from '@playwright/test';

test.describe('AI Insight Sidebar', () => {
  test('should allow user to query and receive AI insights', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="ai-insight-sidebar"]')).toBeVisible();

    const chatInput = page.locator('[data-testid="ai-chat-input"]');
    const sendButton = page.locator('[data-testid="ai-chat-send-button"]');
    const chatMessages = page.locator('[data-testid="ai-chat-messages"]');

    await expect(chatInput).toBeVisible();
    await expect(sendButton).toBeVisible();

    // Simulate user asking a question
    const question = 'Why did sales dip in Q3?';
    await chatInput.fill(question);
    await sendButton.click();

    // Expect the user's question to appear in the chat history
    await expect(chatMessages.locator('.user-message')).toContainText(question);

    // Expect an AI response to appear (might take some time)
    // The AI response should contain some relevant data, not just a placeholder
    await expect(chatMessages.locator('.ai-response')).toContainText(/sales dip/i);
    await expect(chatMessages.locator('.ai-response')).toContainText(/Q3/);
  });

  test('should handle empty query gracefully', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="ai-insight-sidebar"]')).toBeVisible();

    const chatInput = page.locator('[data-testid="ai-chat-input"]');
    const sendButton = page.locator('[data-testid="ai-chat-send-button"]');
    const chatMessages = page.locator('[data-testid="ai-chat-messages"]');

    await expect(chatInput).toBeVisible();
    await expect(sendButton).toBeVisible();

    // Click send without typing
    await sendButton.click();

    // Expect no new user message and possibly a validation error or no action
    await expect(chatMessages.locator('.user-message')).toBeHidden();
    // Depending on implementation, an error message might appear or nothing happens
    // For this test, we expect no critical crash.
    await expect(page.locator('[data-testid="ai-chat-error"]')).toBeHidden(); // No error for empty input (if handled client-side)
  });
});
