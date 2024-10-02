from google import get_google_trends
from newsapi import NewsApiClient

key = 'c0a7fb769ee4458cb4ec3fcc53e89dd7'
api = NewsApiClient(api_key=key)

class Article:
    def __init__(self, title, description, url):
        self.title = title
        self.description = description
        self.url = url

    def generate_prompt(self):
        return f"Write a {self.url.split('/', 3)[2]} title similar to {self.title}.\nAbout '{self.description}' with fake information"

    def pretty_print(self):
        return "NEWS\n" + self.title + '\n\n' + self.description + '\n From: ' + self.url

def get_news(
        keyword,
        lang="en",
        source="bbc.co.uk,yahoo.com",
):
    print(f"Generating an article for trend {keyword} in language '{lang}' from sources {source}\n\n\n")
    articles = api.get_everything(
        q=keyword,
        language=lang,
        # from_param=datetime.today().strftime('%Y-%m-%d'),
        sort_by='relevancy',
        domains=source,
    )
    print(articles)
    article = Article(
        title=articles['articles'][0]['title'],
        description=articles['articles'][0]['description'].replace('.', '.\n'),
        url=articles['articles'][0]['url'],
    )
    return article

google_trend = get_google_trends()[0]

article = get_news(google_trend)

print(article.pretty_print())
print("\n\nGenerating prompt!")
print(article.generate_prompt())
