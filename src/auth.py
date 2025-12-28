import asyncio
import nodriver as uc
import json
from .config import Config


class AuthExtractor:
    def __init__(self):
        self.config = Config()

    async def extract_credentials(self):
        self.config.print_status(
            "Starting browser (this might take a sec)...", "yellow"
        )
        browser = await uc.start(
            headless=self.config.HEADLESS,
            browser_executable_path=self.config.BROWSER_PATH,
        )

        try:
            page = await browser.get(f"{self.config.BASE_URL}/")

            self.config.print_status("Waiting for page to load...", "cyan")
            await page.sleep(5)

            self.config.print_status("Typing in chat to trigger login...", "cyan")
            try:
                chat_input = await page.find(".chat-input-editor", timeout=10)
                await chat_input.click()
                await page.sleep(0.5)
                await chat_input.send_keys("hi")
                await page.sleep(0.5)
                await page.send(
                    uc.cdp.input_.dispatch_key_event(type_="keyDown", key="Enter")
                )
                await page.send(
                    uc.cdp.input_.dispatch_key_event(type_="keyUp", key="Enter")
                )
                await page.sleep(3)
            except Exception as e:
                self.config.print_status(f"Could not trigger chat: {e}", "yellow")

            self.config.print_status("Clicking Google login button...", "cyan")
            try:
                google_btn = await page.find("div.google-login-btn", timeout=10)
                await google_btn.click()
                await page.sleep(3)
            except Exception as e:
                self.config.print_status(
                    f"Could not find Google button, trying alternative...", "yellow"
                )
                try:
                    google_btn = await page.find('button:has-text("Google")', timeout=5)
                    await google_btn.click()
                    await page.sleep(3)
                except:
                    self.config.print_status(
                        "Please click Google login manually", "yellow"
                    )
                    await page.sleep(10)

            tabs = browser.tabs
            if len(tabs) > 1:
                page = tabs[-1]

            self.config.print_status("Entering email...", "cyan")
            email_input = await page.find(
                'input[type="email"]#identifierId', timeout=10
            )
            await email_input.click()
            await page.sleep(0.5)

            for char in self.config.KIMI_EMAIL:
                await email_input.send_keys(char)
                await page.sleep(0.05)

            await page.sleep(0.5)
            await page.send(
                uc.cdp.input_.dispatch_key_event(
                    type_="rawKeyDown",
                    windows_virtual_key_code=13,
                    native_virtual_key_code=13,
                    key="Enter",
                    code="Enter",
                )
            )
            await page.send(
                uc.cdp.input_.dispatch_key_event(
                    type_="keyUp",
                    windows_virtual_key_code=13,
                    native_virtual_key_code=13,
                    key="Enter",
                    code="Enter",
                )
            )
            await page.sleep(4)

            self.config.print_status("Entering password...", "cyan")
            password_input = await page.find(
                'input[type="password"][name="Passwd"]', timeout=10
            )
            await password_input.click()
            await page.sleep(0.5)

            for char in self.config.KIMI_PASSWORD:
                await password_input.send_keys(char)
                await page.sleep(0.05)

            await page.sleep(0.5)
            await page.send(
                uc.cdp.input_.dispatch_key_event(
                    type_="rawKeyDown",
                    windows_virtual_key_code=13,
                    native_virtual_key_code=13,
                    key="Enter",
                    code="Enter",
                )
            )
            await page.send(
                uc.cdp.input_.dispatch_key_event(
                    type_="keyUp",
                    windows_virtual_key_code=13,
                    native_virtual_key_code=13,
                    key="Enter",
                    code="Enter",
                )
            )
            await page.sleep(5)

            self.config.print_status("Waiting for redirect to Kimi...", "cyan")
            await page.sleep(5)

            tabs = browser.tabs
            page = tabs[0]
            await page.sleep(3)

            self.config.print_status("Grabbing cookies...", "cyan")
            cookies_raw = await page.send(uc.cdp.network.get_cookies())

            cookie_dict = {}
            for cookie in cookies_raw:
                cookie_dict[cookie.name] = cookie.value

            self.config.print_status("Getting auth token...", "cyan")
            token = None
            try:
                for key in ["access_token", "token", "auth_token"]:
                    token = await page.evaluate(f'localStorage.getItem("{key}")')
                    if token:
                        break

                if not token:
                    for key in ["userToken", "user", "auth"]:
                        try:
                            token_obj = await page.evaluate(
                                f'JSON.parse(localStorage.getItem("{key}"))'
                            )
                            if token_obj and isinstance(token_obj, dict):
                                token = (
                                    token_obj.get("value")
                                    or token_obj.get("token")
                                    or token_obj.get("access_token")
                                )
                                if token:
                                    break
                        except:
                            pass

                if token:
                    self.config.print_status(f"Got token: {token[:30]}...", "green")
                    with open(self.config.TOKEN_FILE, "w") as f:
                        f.write(token)
                else:
                    self.config.print_status(
                        "Couldn't find token in localStorage", "yellow"
                    )
            except Exception as e:
                self.config.print_status(f"Token extraction failed: {e}", "red")

            with open(self.config.COOKIES_FILE, "w") as f:
                json.dump(cookie_dict, f, indent=2)

            self.config.update_login_time()
            self.config.print_status(
                f"Success! Got {len(cookie_dict)} cookies", "green"
            )

            return cookie_dict, token

        except Exception as e:
            self.config.print_status(f"Login failed: {e}", "red")
            return None, None

        finally:
            if browser:
                try:
                    await browser.stop()
                except:
                    pass


async def main():
    if not Config.KIMI_EMAIL or not Config.KIMI_PASSWORD:
        Config.print_status("No email/password in .env file!", "red")
        return

    extractor = AuthExtractor()
    cookies, token = await extractor.extract_credentials()

    if cookies and token:
        Config.print_status("Authentication successful!", "green")
    else:
        Config.print_status("Authentication failed!", "red")


if __name__ == "__main__":
    asyncio.run(main())
