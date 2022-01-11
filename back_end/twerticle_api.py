from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import json
import requests

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_twerticle(twitter_user: str):


    def get_tweet(search):
        '''
        pass through function the info user wants to look up.
        so tweet user handle, tweet url, or hashtag

        return the tweet user name, tweet text, and hashtags if they have any
        '''

        if "@" in search:
            search = search[1:]

        url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={search}&count=2"

        response = requests.request("GET", url, auth=bearer_oauth)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )

        json_response = response.json()

        id_int = json.dumps(json_response[1]["user"]["id"], indent=4, sort_keys=True)
        name = json.dumps(json_response[1]["user"]["name"], indent=4, sort_keys=True)
        text = json.dumps(json_response[1]["text"], indent=4, sort_keys=True)

        try:
            hashtags = json.dumps(json_response[1]["entities"]["hashtags"][0]["text"], indent=4, sort_keys=True)
        except IndexError:
            hashtags = search

        return [id_int, name, text, hashtags] # return tweet info (name, text, hashtags)


    def get_article(twitter_user):
        '''
        Use the hashtags or some other key to look up research articles

        return the article url, title, and abstract
        '''
        BASE = "https://doaj.org/api/"
        article_dict = {}

        search_query = get_tweet(twitter_user)
        print(search_query[3])

        response = requests.get(BASE + f"search/articles/{search_query[1]}?pageSize=5")

        json_response = response.json()

        for i in range(0,5):

            article_url = json.dumps(json_response["results"][i]["bibjson"]["link"][0]["url"], indent=4)
            article_title = json.dumps(json_response["results"][i]["bibjson"]["title"], indent=4)
            article_abstract = json.dumps(json_response["results"][i]["bibjson"]["abstract"], indent=4)


            article_url = remove_double_quotes(article_url)
            article_title = remove_double_quotes(article_title)
            article_abstract = remove_double_quotes(article_abstract)

            article_dict[(i+1)] = [article_title, article_abstract, article_url]

        # return article info (title, abstract, url) and tweet info
        return article_dict,search_query



    def bearer_oauth(r):
        bearer_token ='AAAAAAAAAAAAAAAAAAAAANPtUwEAAAAAdUNnfFkHlZdjtQXosgguwDpclZg%3DYDwGNCZmT69qXI8rIep2gF7uxQAMagfXfn2YWxhHt2VVyti3Kr'

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2TweetLookupPython"
        return r


    def remove_double_quotes(variable):
        '''
        removes the double quotes that is inserted when calling json.dumps
        '''
        new_variable = []
        for i in variable:
            if i not in '"':
                new_variable.append(i)
        new_variable = ''.join(new_variable)
        return new_variable

    twerticle = get_article(twitter_user)

    return (twerticle)