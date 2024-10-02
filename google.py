from pytrends.request import TrendReq
pytrend = TrendReq()

# Get the top 20 trending Google searches for a given country (default: USA)
def get_google_trends(cn='united_states'):
    return pytrend.trending_searches(pn=cn)[0].values.tolist()
