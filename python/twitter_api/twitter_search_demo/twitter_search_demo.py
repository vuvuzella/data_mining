"""
Demo for using twitter search api
"""
import urllib
import urllib2
import base64
import json


def get_bearer_token(consumer_key, consumer_secret):
    bearer_token = "{0}:{1}".format(consumer_key, consumer_secret)
    bearer_token_64 = base64.b64encode(bearer_token)
    return bearer_token_64

def create_auth_request(bearer_token):
    oauth_app_twitter = "https://api.twitter.com/oauth2/token"
    oauth_header_cont_type = "Content-Type"
    oauth_cont_type_value = "application/x-www-form-urlencoded;charset=UTF-8"
    oauth_header_auth = "Authorization"
    oauth_auth_value = "Basic {0}".format(bearer_token)
    oauth_data = "grant_type=client_credentials"
    # getting access token
    token_request = urllib2.Request(oauth_app_twitter)
    token_request.add_header(oauth_header_cont_type, oauth_cont_type_value)
    token_request.add_header(oauth_header_auth, oauth_auth_value)
    token_request.data = oauth_data
    return token_request

def get_access_token(auth_token_request):
    token_response = urllib2.urlopen(auth_token_request)
    token_contents = token_response.read()
    token_data = json.loads(token_contents)
    access_token = token_data["access_token"]
    return access_token

"""
def create_search_quesry(query_string):
    query_list = query_string.split(" ")
"""

def get_search(query, access_token):
    # query_string = {"q":"earthquake,AND,indonesia",}
    twitter_search_api = "https://api.twitter.com/1.1/search/tweets.json"
    encoded_query = urllib.quote("earthquake AND indonesia")
    # print encoded_query
    search_request = urllib2.Request("{0}?q={1}?".format(twitter_search_api,encoded_query))
    search_request.add_header("Authorization", "Bearer {0}".format(access_token))

    search_response = urllib2.urlopen(search_request)
    response_data = json.loads(search_response.read())
    return response_data

def main():
    new_file = open("response_data.txt", "w")
    consumer_key = "rnE8SzBdt3zg6f9qZSIrtKldc"
    consumer_secret = "rDxy563JCahH9T6mFcCAfyu6hyW2icJr4ZaWJITF3cJPZiCWYF"
    bearer_token = get_bearer_token(consumer_key, consumer_secret)
    auth_request = create_auth_request(bearer_token)
    access_token = get_access_token(auth_request)
    response_data = get_search("123", access_token)
    new_file.write(json.dumps(response_data) + "\n")
    # print json.dumps(response_data, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
