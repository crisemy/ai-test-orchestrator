import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly loginUsername: Locator;
  readonly loginAlertAlertError: Locator;
  readonly formAuthentication: Locator;
  readonly loginResult: Locator;
  readonly loginBtn: Locator;
  readonly loginPassword: Locator;
  readonly loginAlertAlertSuccess: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginUsername = page.locator('#login-username');
    this.loginAlertAlertError = page.locator('#login-alert .alert-error');
    this.formAuthentication = page.locator('text=Form Authentication');
    this.loginResult = page.locator('#login-result');
    this.loginBtn = page.locator('#login-btn');
    this.loginPassword = page.locator('#login-password');
    this.loginAlertAlertSuccess = page.locator('#login-alert .alert-success');
  }

  async login(username: string, password: string) {
    await this.loginUsername.fill(username);
    await this.loginPassword.fill(password);
    await this.loginBtn.click();
  }
}