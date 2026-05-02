"""Playwright-based bid form filler for the Fiverr Job Automation Tool."""

from typing import Optional

from .models import JobOpportunity


class PlaywrightBidSubmitter:
    """Uses Playwright to navigate to a Fiverr bid page, fill in the form,
    and submit a bid.

    This is a skeleton implementation — actual browser automation requires
    a running browser instance and proper selectors for the Fiverr UI.
    """

    def __init__(self, browser_type: str = "chromium"):
        """Initialize the Playwright submitter.

        Args:
            browser_type: Browser type to use ('chromium', 'firefox', 'webkit').
        """
        self.browser_type = browser_type
        self._browser = None
        self._context = None
        self._page = None

    def _ensure_browser(self) -> None:
        """Ensure a browser instance is running."""
        if self._page is None:
            from playwright.sync_api import sync_playwright

            playwright = sync_playwright().start()
            browser_cls = getattr(playwright, self.browser_type)
            self._browser = browser_cls().launch()
            self._context = self._browser.new_context()
            self._page = self._context.new_page()

    def fill_bid_form(
        self, job: JobOpportunity, proposal: str, page=None
    ) -> bool:
        """Navigate to the bid page, fill in title/description fields, and click submit.

        Args:
            job: The JobOpportunity to submit for.
            proposal: The proposal text.
            page: Optional Playwright page object. If None, uses internal page.

        Returns:
            True if the form was filled and submitted successfully.
        """
        target_page = page or self._page
        if target_page is None:
            raise RuntimeError("No page available. Call _ensure_browser() first.")

        # Navigate to the bid page (URL pattern for Fiverr)
        bid_url = f"https://www.fiverr.com/submit_bid/{job.id}"
        target_page.goto(bid_url, wait_until="domcontentloaded")

        # Fill in the bid title
        title_selector = 'input[name="title"], [data-testid="bid-title"]'
        target_page.fill(title_selector, job.title)

        # Fill in the bid description/proposal
        desc_selector = 'textarea[name="description"], [data-testid="bid-description"]'
        target_page.fill(desc_selector, proposal)

        # Click the submit button
        submit_selector = 'button[type="submit"], [data-testid="submit-bid"]'
        target_page.click(submit_selector)

        return True

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self._browser:
            self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
