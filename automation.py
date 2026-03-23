import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from willhaben_bot.willhaben_bot.config import WILLHABEN_EMAIL, WILLHABEN_PASSWORD

Path("debug").mkdir(exist_ok=True)

def snap(page: Page, name: str):
    page.screenshot(path=f"debug/{name}.png", full_page=True)
    print("📸", f"debug/{name}.png", "| URL:", page.url)

def accept_cookies(page: Page):
    try:
        page.get_by_role("button", name=re.compile("Annehmen", re.I)).click(timeout=3000)
    except Exception:
        pass

def login(page: Page):
    page.goto("https://www.willhaben.at/iad", wait_until="domcontentloaded")
    accept_cookies(page)

    # Login öffnen (falls schon eingeloggt, kann der Link fehlen)
    try:
        page.get_by_test_id("main-header").get_by_role("link", name="Einloggen").click(timeout=4000)
    except Exception:
        print("ℹ️ 'Einloggen' Link nicht gefunden – evtl. schon eingeloggt.")
        return

    page.get_by_test_id("username-input").fill(WILLHABEN_EMAIL)
    page.get_by_test_id("password-input").fill(WILLHABEN_PASSWORD)

    # Codegen hatte login-button testid – behalten wir
    page.get_by_test_id("login-button").click()

    # Falls Captcha kommt: manuell lösen, dann ENTER
    print("➡️ Wenn CAPTCHA/2FA kommt: im Browser lösen.")
    input("➡️ Wenn du eingeloggt bist, ENTER drücken...")

def create_listing(page: Page, title: str):
    page.goto("https://www.willhaben.at/iad", wait_until="domcontentloaded")
    accept_cookies(page)

    # Codegen: "Neue Anzeige aufgeben" (bitte kein dblclick)
    page.get_by_role("link", name="Neue Anzeige aufgeben").click()

    # Codegen Flow:
    page.get_by_test_id("new-ad-67").click()
    page.get_by_test_id("price-input").fill("1")
    page.get_by_test_id("heading-input").fill(title)
    desc = page.locator(".ql-editor").first
    desc.wait_for(state="visible", timeout=10000)
    desc.click()
    desc.press("Control+A")  # auf Mac: "Meta+A"
    desc.type("schulprojekt headless browser", delay=20)

    page.get_by_test_id("send-button").click()
    page.get_by_test_id("select-category").click()
    page.get_by_role("button", name="Computer / Software").click()
    page.get_by_role("button", name="Computer / Tablets").click()
    page.get_by_role("button", name="PCs").click()
    page.get_by_test_id("send-button").click()

    # Marke auswählen (HP)
    page.get_by_test_id("BRAND_COMPUTER_TABLETS-input-HP-label").click()
    page.get_by_test_id("send-button").click()

    # "Überspringen" (vermutlich Bilder/Extras)
    page.get_by_test_id("submitButton").click()
    page.get_by_test_id("submit-button").click()

    print("✅ Veröffentlicht:", title)
    input("➡️ Inserat ist veröffentlicht. ENTER drücken um mit Löschen fortzufahren...")

    page.get_by_role("button", name="Überspringen").click()

    # Publish
    page.get_by_test_id("submitButton").click()
    page.get_by_test_id("submit-button").click()
    page.get_by_test_id("submit-button").click()

    print("✅ Inserat erstellt:", title)

def go_to_my_ads(page: Page):
    page.get_by_role("button", name="Mein Willhaben Menü").click()
    page.get_by_test_id("verticalMenuItem-myadverts").click()
    page.wait_for_load_state("domcontentloaded")

import re
from playwright.sync_api import Page

def delete_listing_by_title(page: Page, title: str):
    go_to_my_ads(page)
    page.wait_for_timeout(1200)

    # 1) Titel finden
    t = page.get_by_text(title, exact=False).first
    try:
        t.wait_for(timeout=15000)
    except Exception:
        snap(page, "delete_title_not_found")
        raise RuntimeError(f"Titel nicht gefunden in 'Meine Anzeigen': {title}")

    # 2) "Row/Card" um den Titel greifen (mehrere Versuche)
    #   - artikel/card
    #   - parent div
    card = t.locator("xpath=ancestor::*[self::article or self::li or @role='listitem'][1]")
    if card.count() == 0:
        card = t.locator("xpath=ancestor::div[1]")

    # 3) Variante A: data-testid endet auf -delete-button (dein alter codegen-style)
    try:
        btn = card.locator("[data-testid$='-delete-button']").first
        if btn.count() > 0:
            btn.click(timeout=4000)
        else:
            raise Exception("no -delete-button in card")
    except Exception:
        # 4) Variante B: direkter Button "Löschen" in der Card
        try:
            card.get_by_role("button", name=re.compile("löschen", re.I)).first.click(timeout=4000)
        except Exception:
            # 5) Variante C: 3-Punkte Menü (… / Mehr / Aktionen) öffnen und dann "Löschen" klicken
            try:
                # Häufige Patterns: "Mehr", "Aktionen", "Optionen", "Menu"
                menu_btn = card.get_by_role("button", name=re.compile(r"(mehr|optionen|aktionen|menü|menu|\.\.\.)", re.I)).first
                menu_btn.click(timeout=4000)

                # Im geöffneten Menü/Popover den Punkt "Löschen" klicken
                page.get_by_role("menuitem", name=re.compile("löschen", re.I)).click(timeout=4000)
            except Exception:
                snap(page, "delete_no_control_found")
                raise RuntimeError("Konnte keinen Lösch-Button / Menü in der Inserat-Karte finden.")

    # 6) Bestätigungsmodal
    try:
        page.get_by_test_id("delete-modal-confirm-button").click(timeout=6000)
    except Exception:
        # Fallback falls anderes Modal-UI
        try:
            page.get_by_role("button", name=re.compile("bestätigen|löschen|ja", re.I)).click(timeout=6000)
        except Exception:
            snap(page, "delete_confirm_missing")
            raise RuntimeError("Delete-Confirm Button nicht gefunden.")

    # 7) Grund auswählen (dein bisheriger testid)
    try:
        page.get_by_test_id("deleteReason-input-group-deleteReason-input-radio-10-label").click(timeout=4000)
    except Exception:
        try:
            page.locator("[data-testid*='deleteReason-input-group']").first.click(timeout=4000)
        except Exception:
            # manchmal ist Grund optional – dann egal
            pass

    # 8) Final bestätigen
    try:
        page.get_by_test_id("delete-modal-confirm-button").click(timeout=6000)
    except Exception:
        try:
            page.get_by_role("button", name=re.compile("bestätigen|löschen|ja", re.I)).click(timeout=6000)
        except Exception:
            snap(page, "delete_final_confirm_missing")
            raise RuntimeError("Finales Bestätigen nicht gefunden.")

    print("✅ Gelöscht:", title)

    def main(title_prefix="dummy_projekt"):
        ...


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=120)
        context = browser.new_context(locale="de-AT", viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            login(page)
            create_listing(page, title)
            delete_listing_by_title(page, title)
        except Exception as e:
            print("❌ ERROR:", repr(e))

            snap(page, "failed")
            raise
        finally:
            context.close()
            browser.close()

        print("🏁 Alles in einem Durchlauf erledigt.")

def main_flow(title_prefix="dummy_projekt"):
    main(title_prefix)


if __name__ == "__main__":
    main()