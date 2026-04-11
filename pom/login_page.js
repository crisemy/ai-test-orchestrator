class LoginPage {
  constructor(page) {
    this.page = page;
    this.username = page.locator('#username');
    this.buttonbtn = page.locator('button[type=');
    this.flash = page.locator('#flash');
    this.password = page.locator('#password');
  }

  async login(username, password) {
    await this.username.fill(username);
    await this.password.fill(password);
    await this.login.click();
  }
}

module.exports = { LoginPage };