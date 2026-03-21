from bs4 import BeautifulSoup

class Parser:
    # Class which contain tools which will parse messy HTML into organized data.
    def __init__(self):
        pass

    def parse_through_quotes(self, html, url):
        soup = BeautifulSoup(html, "lxml")
        quotes_html = soup.find_all("div", class_="quote")
        quotes = []
        for quote_html in quotes_html:
            quote_text = quote_html.find("span", class_="text").text
            quote_author = quote_html.find("small", class_="author").text
            quotes.append((quote_text, quote_author))
        try:
            url += (soup.find("li", class_="next").a["href"]).replace("/", "", 1)
            print(url)
        except Exception:
            url = None
        return quotes, url
