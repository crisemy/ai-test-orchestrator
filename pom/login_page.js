class LoginPage {
  constructor(page) {
    this.page = page;
    this.password = page.locator('#password');
    this.buttonbtn = page.locator('button[type=');
    this.flash = page.locator('#flash');
    this.username = page.locator('#username');
  }

  async login(username, password) {
    await this.username.fill(username);
    await this.password.fill(password);
    await this.login.click();
  }
}

module.exports = { LoginPage };