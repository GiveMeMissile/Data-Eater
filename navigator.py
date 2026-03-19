import playwright.async_api as async_playwright

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page):
        self.page = page
        # self.original_url = page.url()

    # Function which uses playwright to access static html
    async def get_html(self):
        await self.page.wait_for_load_state("domcontentloaded")
        html = await self.page.content()
        return html
    
    async def goto(self, url):
        await self.page.goto(url)

    async def return_to_original(self):
        await self.page.goto(self.original_url)