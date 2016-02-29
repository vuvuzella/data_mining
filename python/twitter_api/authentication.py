"""
OAuth usage from twitter api
    http://alanwsmith.com/using-the-twitter-api-without-3rd-party-libraries
"""
import base64
import json
import urllib2

# Credentials
consumer_key = "rnE8SzBdt3zg6f9qZSIrtKldc"
consumer_secret = "rDxy563JCahH9T6mFcCAfyu6hyW2icJr4ZaWJITF3cJPZiCWYF"

# key encoding
bearer_token = "{0}:{1}".format(consumer_key, consumer_secret)
bearer_token_64 = base64.b64encode(bearer_token)

# String constants for access token retrieval
oauth_app_twitter = "https://api.twitter.com/oauth2/token"
oauth_header_cont_type = "Content-Type"
oauth_cont_type_value = "application/x-www-form-urlencoded;charset=UTF-8"
oauth_header_auth = "Authorization"
oauth_auth_value = "Basic {0}".format(bearer_token_64)
oauth_data = "grant_type=client_credentials"

# getting access token
token_request = urllib2.Request(oauth_app_twitter)
token_request.add_header(oauth_header_cont_type, oauth_cont_type_value)
token_request.add_header(oauth_header_auth, oauth_auth_value)
token_request.data = oauth_data

token_response = urllib2.urlopen(token_request)
token_contents = token_response.read()
token_data = json.loads(token_contents)
access_token = token_data["access_token"]

# API string constants
twitter_ver_1 = "https://api.twitter.com/1.1"
users_api = "/users"
users_edge = "/show.json"
users_params = "?screen_name=TheIdOfAlan"

# Using Access token to make an API Request
timeline_request = urllib2.Request("{0}{1}{2}{3}".format(twitter_ver_1, users_api, users_edge, users_params))
timeline_request.add_header(oauth_header_auth, "Bearer {0}".format(access_token))

timeline_response = urllib2.urlopen(timeline_request)
timeline_contents = timeline_response.read()
timeline_data = json.loads(timeline_contents)

print json.dumps(timeline_data, indent=2, sort_keys=True)
