import re
from playwright.sync_api import Page

class WillhabenLogin:
    def __init__(self, page: Page):
        self.page = page

    def accept_cookies(self) -> None:
        try:
            self.page.get_by_role("button", name=re.compile("Annehmen", re.I)).click(timeout=4000)
        except Exception:
            pass

    def login(self, email: str, password: str) -> None:
        self.page.goto("https://www.willhaben.at/iad", wait_until="domcontentloaded")
        self.accept_cookies()

        self.page.get_by_test_id("main-header").get_by_role("link", name="Einloggen").click()
        self.page.get_by_test_id("username-input").fill(email)
        self.page.get_by_test_id("password-input").fill(password)
        self.page.get_by_role("button", name=re.compile(r"^Einloggen$", re.I)).click()

        # Wenn Captcha/2FA kommt: du machst es, dann ENTER -> weiter
        print("➡️ Wenn CAPTCHA/2FA kommt: im Browser lösen.")
        input("➡️ Wenn du eingeloggt bist, ENTER drücken...")

        # kleiner Check
        try:
            self.page.get_by_test_id("main-header").get_by_role("link", name="Einloggen").wait_for(
                state="detached", timeout=15000
            )
        except Exception:
            pass


    def do_login_until_manual_step(self, email: str, password: str) -> None:
        self.page.goto("https://www.willhaben.at/iad", wait_until="domcontentloaded")
        self.accept_cookies()

        # Login öffnen
        self.page.get_by_test_id("main-header").get_by_role("link", name="Einloggen").click()

        # Felder füllen
        self.page.get_by_test_id("username-input").fill(email)
        self.page.get_by_test_id("password-input").fill(password)

        # ✅ Login klicken (richtiger Button)
        self.page.get_by_role("button", name="Einloggen").click()

        # ✅ Falls reCAPTCHA/2FA kommt -> du machst es manuell
        print("➡️ Falls reCAPTCHA/2FA erscheint: bitte MANUELL lösen.")
        print("➡️ Danach im Inspector auf 'Resume' klicken.")
        self.page.pause()

        # ✅ Optional: nach Resume nochmal klicken, FALLS es wirklich nötig ist
        # (manchmal leitet Willhaben automatisch weiter; daher try/except)
        try:
            self.page.get_by_role("button", name="Einloggen").click(timeout=2000)
        except Exception:
            pass
