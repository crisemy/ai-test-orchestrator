import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly loginAlertAlertSuccess: Locator;
  readonly formAuthentication: Locator;
  readonly loginAlertAlertError: Locator;
  readonly loginUsername: Locator;
  readonly loginPassword: Locator;
  readonly loginResult: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = page.locator('#login-btn');
    this.loginAlertAlertSuccess = page.locator('#login-alert .alert-success');
    this.formAuthentication = page.locator('text=Form Authentication');
    this.loginAlertAlertError = page.locator('#login-alert .alert-error');
    this.loginUsername = page.locator('#login-username');
    this.loginPassword = page.locator('#login-password');
    this.loginResult = page.locator('#login-result');
  }

  async login(username: string, password: string) {
    await this.loginUsername.fill(username);
    await this.loginPassword.fill(password);
    await this.loginBtn.click();
  }
}