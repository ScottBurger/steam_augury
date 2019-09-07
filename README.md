# steam_augury
This is a steam tag-based recommendation system that scores games according to a user's interest level for given steam tags based on their hours of playtime

# how to use
In this pythonic instance, run *python steam_augury.py api_key steam_id* in console.

# steam api key
Available here: https://steamcommunity.com/dev/apikey

# steam id
For a given user's steam profile page, if you inspect source, you can find your 17 digit steam id key by searching for "g_rgProfileData". An example would look like:

g_rgProfileData = {"url":"https:\/\/steamcommunity.com\/profiles\/**765611________**

# outputs
The reccomendation system will list the top 10 games according to a filtering score system built in the script. The full results with more than 30,000 steam games ranked is output in a tab-separated file in the working directory. Here users can see more details about the games and see the ones that didn't meet the filter's expectations.

