import os
import requests
from playwright.sync_api import sync_playwright, BrowserContext, Page
from requests.cookies import create_cookie
from undetected_playwright import stealth_sync

class BrowserInstance:
    PARENT_DIR = os.path.dirname(os.path.abspath(__file__)) 
    CONTEXT_DIR = os.path.join(PARENT_DIR, "context")
    
    def get_fresh_cookies(self, url: str, session: requests.Session, browser_type="firefox", headless=True):
        # Create the context directory if it doesn't exist

        with sync_playwright() as p:
            if browser_type == "chromium":
                context = p.chromium.launch_persistent_context(
                    self.CONTEXT_DIR,
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                )
            elif browser_type == "firefox":
                context = p.firefox.launch_persistent_context(
                    self.CONTEXT_DIR,
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                )
            elif browser_type == "webkit":
                context = p.webkit.launch_persistent_context(
                    self.CONTEXT_DIR,
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                )
            else:
                raise ValueError("Invalid browser_type. Use 'chromium', 'firefox', or 'webkit'.")

            stealth_sync(context)
            page = self.new_page(context)

            # Log in and navigate to the protected page
            page.goto(url)
            # Add your login logic here

            cookies = context.cookies()
            context.close()
            
            
        for cookie in cookies:
            cookie_object = create_cookie(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie['path'],
                expires=cookie['expires'],
                secure=cookie['secure'],
                rest={"HttpOnly": cookie["httpOnly"]},
                rfc2109=False
                
                
                # Add any other relevant cookie attributes
            )
            session.cookies.set_cookie(cookie_object)

        return session
    
    def launch_browser_for_login(self, url: str, browser_type="firefox", headless=True):
    # Create the context directory if it doesn't exist
        os.makedirs(os.path.join(self.PARENT_DIR, "context"), exist_ok=True)

        with sync_playwright() as p:
            if browser_type == "chromium":
                context = p.chromium.launch_persistent_context(
                    self.CONTEXT_DIR,
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                )
            elif browser_type == "firefox":
                context = p.firefox.launch_persistent_context(
                    self.CONTEXT_DIR,
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                )
            elif browser_type == "webkit":
                context = p.webkit.launch_persistent_context(
                    self.CONTEXT_DIR,
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                )
            else:
                raise ValueError("Invalid browser_type. Use 'chromium', 'firefox', or 'webkit'.")

            stealth_sync(context)
            page = self.new_page(context)

            # Navigate to the login page
            page.goto(url)
            print("Please log in and press Enter when finished.")
            input() # Wait for user input

            # Close the browser context
            context.close()

            # Check if the context is closed
            if context.is_closed():
                print("Browser context closed successfully.")
            else:
                print("Failed to close the browser context.")
    
    @staticmethod
    def new_page(context: BrowserContext) -> Page:
        page = context.new_page()
        page.add_init_script(
            """
                                navigator.webdriver = false
                                Object.defineProperty(navigator, 'webdriver', {
                                get: () => false
                                })
                                """
        )
        return page
