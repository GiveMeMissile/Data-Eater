from Scraper.parser import Judge, Parser
import constants as c
import asyncio
import time

##########################################################################
# Defining what will be added:  
# 1: Button Prioritization (based on name) ✓
# 2: Link Prioritization ✓
# 3: Location rework + update usage ✓
# 4: Check for Dead ✓
# 5: Save Websites Scores (from Judge) ✓
# 6: Add Capabilities to handle search bars (Not yet, maybe later)
# 7: Add Abilities to return to the previous website with the best score ✓
# 8: Add the ability to get samples from website ✓
# 9: Add the Ability to get info about the website via exploring ✓
# 10: Update how click all works ✓
# 11: Create a core function which collects samples ✓
# 12: Test everything to make sure it actually works 
# 13: Implement these changes into main file

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page, process):

        self.page = page
        self.pages = {"Page": []}
        if self.page.url != "about:blank":
            self.pages["Page"].append(self.page.url)
        self.page.on("request", self.update_request_time)
        self.window_start = time.time()
        self.num_requests = 0
        self.delay = False
        self.process = process
        print(self.process)

    async def update_request_time(self):
        # Tracks the number of request being made to ensure it does not go over the rate limit

        self.num_requests += 1
        # print(f"Num Requests: {self.num_requests} | Time Window: {time.time() - self.window_start}")
        if self.num_requests >= c.REQUEST_LIMIT:
            await self.wait_for_reset()

        await self.request_reset()

    async def request_reset(self):
        # Function Which resets the request counter when the time runs out

        if time.time() - self.window_start < c.LIMIT_WINDOW:
            return

        self.num_requests = 0
        self.window_start = time.time() - ((time.time() - self.window_start) - c.LIMIT_WINDOW)
    
    async def wait_for_reset(self):
        # Function which waits until the current time window ends, stopping all requests until a new window has started
        print("Sleeping, zzzzzzzzzzzzzzzzz")
        self.delay = True
        self.process[2] = True
        await asyncio.sleep(c.LIMIT_WINDOW - (time.time() - self.window_start))
        self.process[2] = False
        self.delay = False

    # Function which uses playwright to access static html
    async def get_html(self):
        # Loads the dom content of a page when the page has loaded its dom content

        await self.page.wait_for_load_state("domcontentloaded")
        html = await self.page.content()
        return html
    
    async def wait_for_delay(self):
        # Function used to have every other function to wait until the rate delay is over

        if not self.delay:
            return
        while self.delay:
            await asyncio.sleep(0.2)
    
    async def goto(self, url):
        # Goes to a new url, saving the url to the locations list
        w = await self.wait_for_delay()
        try: 
            await self.page.goto(url)
        except Exception as e:
            return False, False
        if not await self.page_already_saved(url):
            return True, False
        return True, True

    async def mouse_scroll(self, length):
        # Uses the mouse from playwright in order to scroll down a page length pixels
        move_len = length // c.NUM_MOUSE_SCROLLS
        for _ in range(c.NUM_MOUSE_SCROLLS):
            w = await self.wait_for_delay()
            await self.page.mouse.wheel(0, move_len)
            await asyncio.sleep(0.1)

    async def instant_scroll(self):
        # Instantly scrolls down to the bottom of a page.
        w = await self.wait_for_delay()
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def infinite_scroll(self, max_scrolls=c.MAX_SCROLLS):
        # Scrolls an infinite scrolling page until it reaches the bottom or max scrolls is reached.
        # Note: This function has yet to be tested due to a lack of any site to test yet.
        # It will be tested on a later date (whenever I feel like it)

        old_height = await self.page.evaluate("document.body.scrollHeight")
        new_height = old_height
        scroll_length = await self.page.evaluate("window.innerHeight") * 2
        num_scrolls = 0
        no_count = 0

        # Scrolls the entire height of the webpage once so content is ensured to load.
        await self.mouse_scroll(old_height)
        await asyncio.sleep(1)

        while True:
            await self.mouse_scroll(scroll_length * 2)
            num_scrolls += 1
            await asyncio.sleep(1)
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height ==  old_height:
                no_count += 1
                if no_count >= 2:
                    break
            if not max_scrolls == -1:
                if max_scrolls < num_scrolls:
                    break
            old_height = new_height

    async def return_to_idx(self, idx):
        # Returns the page to a previous url based off of its location in the locations list
        # print(idx)
        await self.goto(self.pages["Page"][idx])

    async def get_all_buttons(self):
        # Returns a list of all the buttons contained within the page.
        buttons = await self.page.get_by_role("button").all()
        return buttons

    async def get_all_links(self):
        # Returns a list of all the links contained within the page.
        links = await self.page.get_by_role("link").all()
        return links
    
    async def page_already_saved(self, url):
        # Checks if a page has already been saved...
        for page_url in self.pages["Page"]:
            if page_url == url:
                return True
        return False
    
    async def get_current_idx(self):
        for i in range(len(self.pages["Page"])):
            if self.pages["Page"][i] == self.page.url:
                return i
        return None
    
    async def click_on_clickable(self, clickable):
        w = await self.wait_for_delay()
        previous_page = self.page.url
        # print(previous_page)
        await clickable.click()
        return previous_page
    
    async def save_page_score(self, url, alread_exists):
        if alread_exists:
            return
        
        self.pages["Page"].append(url)


class Analyzer(Navigator):
    # This class is focused on getting information about the page

    def __init__(self, page, process, words, samples):
        super().__init__(page, process)
        self.judge = Judge()
        self.samples = []
        for part in samples:
            self.samples += part.split(" ")
        self.words = words
        self.pages["scraping"] = []
        self.pages["exploration"] = []

    async def get_all_buttons(self):
        # Gets all links and counts the exploration score from links

        score = 0
        buttons = await super().get_all_buttons()
        prioritized_list = []
        for button in buttons:
            name = await button.inner_text()
            if any(priority in name.lower() for priority in (c.MAX_PRIORITY + self.words)):
                prioritized_list.append(button)
                score += 0.1
        
        for button in buttons:
            name = await button.inner_text()
            if any(priority in name.lower() for priority in (c.NORMAL_PRIORITY + self.samples)):
                prioritized_list.append(button)
                score += 0.05
        
        for button in buttons:
            if any(button == b for b in prioritized_list):
                continue
            name = await button.inner_text()
            if not any(reject in name.lower() for reject in c.REJECT):
                prioritized_list.append(button)
                score += 0.025

        return prioritized_list, score
    
    async def get_all_links(self):
        # Gets all links and counts the exploration score from links
        start = time.time()
        score = 0
        links = await super().get_all_links()
        prioritized_list = []
        for link in links:
            text = await link.inner_text()
            if any(priority in text.lower() for priority in (c.MAX_PRIORITY + self.words)):
                prioritized_list.append(link)
                score += 0.1
        
        for link in links:
            text = await link.inner_text()
            if any(priority in text.lower() for priority in (c.NORMAL_PRIORITY + self.samples)):
                prioritized_list.append(link)
                score += 0.05
        
        for link in links:
            if any(link == b for b in prioritized_list):
                continue
            text = await link.inner_text()
            if not any(reject in text.lower() for reject in c.REJECT):
                prioritized_list.append(link)
                score += 0.025

        urls = []
        for link in prioritized_list:
            urls.append(await link.get_attribute("href"))
        repeats = []
        for i in range(len(urls)):
            for j in range(i + 1, len(urls)):
                if urls[i] == urls[j]:
                    repeats.append(j)
        final_links = []
        for i in range(len(prioritized_list)):
            if not any(i == j for j in repeats):
                final_links.append(prioritized_list[i])

        end = time.time()
        print(f"Time Taken: {end - start}")

        return final_links, score

    async def check_infinite_scroll(self):
        # Checks if a page is infinitely scrollable. 

        old_height = await self.page.evaluate("document.body.scrollHeight")
        await self.mouse_scroll(old_height)
        new_height = await self.page.evaluate("document.body.scrollHeight")
        await asyncio.sleep(0.5)
        if new_height > old_height:
            return True
        return False
    
    async def goto(self, url):
        # Go to a different page and saves its exploration and scraping score. 

        exists, already_exists = await super().goto(url)
        if not exists:
            return exists
        await asyncio.sleep(0.25)
        await self.save_page_score(url, already_exists)
        return exists
    
    async def save_page_score(self, url, alread_exists):
        # Saves important information for each page
        await super().save_page_score(url, alread_exists)

        if alread_exists:
            return

        self.pages["scraping"].append(self.judge.get_score(url, await self.get_html()))
        _, score_1 = await self.get_all_buttons()
        _, score_2 = await self.get_all_links()
        self.pages["exploration"].append(score_1 + score_2)
    
    async def is_dead_end(self):
        # Checks if a page has no links/buttons to use to navigate to other pages.

        _, score_1 = await self.get_all_buttons()
        _, score_2 = await self.get_all_links()
        if score_1 + score_2 == 0:
            return True
        return False


class Explorer(Analyzer):
    def __init__(self, page, process ,words, samples):
        super().__init__(page, process, words, samples)
        self.pages["scraped"] = []
        self.pages["explored"] = []
        if self.page.url != "about:blank":
            self.pages["scraped"].append(False)
            self.pages["explored"].append(False)
        self.parser = Parser()

    async def save_page_score(self, url, alread_exists):
        await super().save_page_score(url, alread_exists)
        if not alread_exists:
            self.pages["scraped"].append(False)
            self.pages["explored"].append(False)

    async def scrape_page(self, idx=None):
        # Scrapes the page, that bout it...

        if idx is None:
            idx = len(self.pages["scraped"]) - 1
        else:
            await self.return_to_idx(idx)
        if self.pages["scraped"][idx]:
            print("Failed because it has been scraped")
            return None
        print(f"Idx: {idx}")
        self.pages["scraped"][idx] = True
        if not self.judge.is_valid(self.page.url, await self.get_html()):
            print("Failed Because it has a low score")
            print(f"Score: {self.judge.get_score(self.page.url, await self.get_html())}")
            return None
        if await self.check_infinite_scroll():
            await self.infinite_scroll()
        return self.parser.get_text_samples(await self.get_html())
    
    async def explore_page(self, idx=None):
        if idx is None:
            idx = len(self.pages["explored"]) - 1
        else:
            await self.return_to_idx(idx)
        if self.pages["explored"][idx]:
            return None
        self.pages["explored"][idx] = True
        if self.pages["exploration"][idx] < c.MIN_EXPLORATION_SCORE:
            return None
        await self.click_all(button=True)
        await self.click_all(button=False)
        
    async def click_on_clickable(self, clickable):
        previous = await super().click_on_clickable(clickable)
        await asyncio.sleep(1)
        if previous != self.page.url:
            await self.save_page_score(self.page.url, await self.page_already_saved(self.page.url))
            return True
        return False
    
    async def click_all(self, button=True):
        # Clicks on all of the buttons or links and checks for the changes in the website.
        idx = await self.get_current_idx()
        w = await self.wait_for_delay()
        if button:
            clickables, _ = await self.get_all_buttons()
        else:
            clickables, _ = await self.get_all_links()
        # print("Got All Clickables")

        for clickable in clickables:
            new_page_loaded = await self.click_on_clickable(clickable)
            # print("Clicked")
            if new_page_loaded:
                await self.return_to_idx(idx)
                # print("Returned")
                await asyncio.sleep(1)

    async def get_samples(self, num_samples):
        samples = []
        while len(samples) <= num_samples:
            self.process[0] = True
            for i in range(len(self.pages["Page"])):
                print("Scraping")
                if self.pages["scraped"][i] or self.pages["scraping"][i] <= 0:
                    print("Scraping Cancelled")
                    continue
                await self.goto(self.pages["Page"][i])
                await asyncio.sleep(1)
                s = await self.scrape_page(idx=i)
                if s is not None:
                    samples += s
                print(f"Samples: {len(samples)}")
                if len(samples) >= num_samples:
                    return samples, False
            self.process[0] = False
            count = 0
            explored = False
            e_list = self.pages["exploration"].copy()
            self.process[1] = True
            while count < len(self.pages["Page"]) and not explored:
                m_idx = self.pages["exploration"].index(max(e_list))
                if self.pages["explored"][m_idx] or self.pages["exploration"][m_idx] < c.MIN_EXPLORATION_SCORE:
                    e_list.remove(e_list)
                    count += 1
                    continue
                print("Exploring")
                await self.goto(self.pages["Page"][m_idx])
                await asyncio.sleep(1)
                await self.explore_page()
                explored = True
            self.process[1] = False
            if not explored:
                return samples, True
            print("Again it goes")

        return samples, False

