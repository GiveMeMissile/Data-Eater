from bs4 import BeautifulSoup
import constants as c

############################################
# 1: Determine if a page has data to be harvested (Judge). 
# 2: Get Text samples (Use Wikipedia, Hacker News, and Quotes to Scrape to test this)
# 3: Filter out useless Text Data (Headers, Web Page Name, Info, ect...)
# 4: Get Good

class Parser:
    # Class which contain tools which will parse messy HTML into organized data.
    num_text_samples = 0

    def __init__(self, min_length=50):
        self.min_length = min_length

    def get_raw_text(self, html):
        soup = BeautifulSoup(html, "lxml")
        return soup.text
    
    def get_text_samples(self, html):
        # Function will be improved upon later.

        text = self.get_raw_text(html)
        text = text.split("\n")
        samples = []
        for part in text:
            if len(part) >= self.min_length and not "{\\" in part:
                samples.append(part)

        return samples
    
    def parse_through_quotes(self, html, url):
        # Test function which will be used later. 

        soup = BeautifulSoup(html, "lxml")
        quotes_html = soup.find_all("div", class_="quote")
        quotes = []
        for quote_html in quotes_html:
            quote_text = quote_html.find("span", class_="text").text
            quote_author = quote_html.find("small", class_="author").text
            quotes.append((quote_text, quote_author))
        try:
            url += (soup.find("li", class_="next").a["href"]).replace("/", "", 1)
        except Exception:
            url = None
        return quotes, url


class Judge(Parser):

    unwanted_url_stuff = [
        "login",
        "password",
        "authentication",
        "checkout",
        "signup",
        "register",
        "cart",
        "privacy",
        "terms",
        "cookie",
        "advertise",
        "contact",
        "about"
    ]

    wanted_url_stuff = [
        "fourms",
        "wikipedia",
        "article",
        "post",
        "story",
        "blog",
        "news",
        "thread",
        "discussion"
    ]

    def __init__(self, words=[]):
        for word in words:
            self.wanted_url_stuff.append(word)
        

    def check_url(self, url):
        url = url.lower()
        score = 0
        for part in self.unwanted_url_stuff:
            if part in url:
                score -= c.JUDGE_SCORE_CHANGE

        for part in self.wanted_url_stuff:
            if part in url:
                score += c.JUDGE_SCORE_CHANGE
            
        return score

    def check_text_ratio(self, html):
        text = self.get_raw_text(html)
        html_length = len(html)
        text_length = len(text)

        ratio = text_length/html_length
        ratio -= c.TEXT_LOSS_THRESHOLD

        return ratio * 10
    
    def get_score(self, url, html):
        return self.check_url(url) + self.check_text_ratio(html)
    
    def is_valid(self, url, html):
        # Determines if the website is worth scraping (work in progress/needs improvements)

        score = 0
        score += self.check_url(url)
        score += self.check_text_ratio(html)
        if score >= 0:
            return True
        return False

