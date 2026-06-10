import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly loginUsername: Locator;
  readonly loginAlertAlertSuccess: Locator;
  readonly loginPassword: Locator;
  readonly loginResult: Locator;
  readonly loginAlertAlertError: Locator;
  readonly formAuthentication: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = page.locator('#login-btn');
    this.loginUsername = page.locator('#login-username');
    this.loginAlertAlertSuccess = page.locator('#login-alert .alert-success');
    this.loginPassword = page.locator('#login-password');
    this.loginResult = page.locator('#login-result');
    this.loginAlertAlertError = page.locator('#login-alert .alert-error');
    this.formAuthentication = page.locator('text=Form Authentication');
  }

  async login(username: string, password: string) {
    await this.loginUsername.fill(username);
    await this.loginPassword.fill(password);
    await this.loginBtn.click();
  }
}