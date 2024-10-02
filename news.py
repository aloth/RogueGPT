from datetime import datetime
from datetime import timedelta
import requests

from google import get_google_trends

key = 'c0a7fb769ee4458cb4ec3fcc53e89dd7'
# https://newsapi.org/docs/get-started

# Get the news for a given keyword and a particular day (default: yesterday's date)
def get_news(
        keyword,
        date=(datetime.today() - timedelta(days = 1)).strftime('%Y-%m-%d'),
        source='bbc-news',
):
    print(f"Getting news from {date} for {keyword} from source {source}")
    url = ('https://newsapi.org/v2/everything?'
           f'q={keyword}&'
           f'from={date}&'
           'sortBy=popularity&'
           f'sources={source}&'
           f'apiKey={key}')
    response = requests.get(url)
    return response.json()

google_trend = get_google_trends().values[1][0]
print(get_news(google_trend, source='cnn')['articles'][0]['content'])
