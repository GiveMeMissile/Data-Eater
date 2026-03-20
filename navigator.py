import constants as c
import asyncio

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page):
        self.page = page
        self.original_url = page.url

    # Function which uses playwright to access static html
    async def get_html(self):
        await self.page.wait_for_load_state("domcontentloaded")
        html = await self.page.content()
        return html
    
    async def goto(self, url):
        await self.page.goto(url)

    async def return_to_original(self):
        await self.page.goto(self.original_url)

    async def harvest_data(self, parser):
        # This Function will be altered in order to work for multiple websites

        total_data = []

        collecting_data = True
        while collecting_data:
            html = await self.get_html()
            data, new_url = parser.parse_through_quotes(html, self.original_url)
            if new_url is None:
                collecting_data = False
            else:
                await self.goto(new_url)
            if len(total_data) > c.BATCH_SIZE:
                collecting_data = False
            total_data += data

        return total_data
