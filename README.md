# steam_augury
This is a steam tag-based recommendation system that scores games according to a user's interest level for given steam tags based on their hours of playtime

## how to use
In this python version, run *python steam_augury.py api_key steam_id* in console.

## steam api key
Available here: https://steamcommunity.com/dev/apikey

## steam id
For a given user's steam profile page, if you inspect source, you can find your 17 digit steam id key by searching for "g_rgProfileData". An example would look like:

g_rgProfileData = {"url":"https:\/\/steamcommunity.com\/profiles\/**765611________**

## outputs
The reccomendation system will list the top 10 games according to a filtering score system built in the script. The full results with more than 30,000 steam games ranked is output in a tab-separated file in the working directory. Here users can see more details about the games and see the ones that didn't meet the filter's expectations.

The python version of this takes about 4-5 minutes to run, pending optimizations. A neat little console progress bar will tell you how far along it is, but please be patient while the magic happens!

## about the data
There are 3 pre-downloaded datasets used in this system:
 * all_app_details: appid, name, type, categories, genres, release_date, last_updated
 * app_reviews: appid, positive_reviews, total_reviews, last_updated
 * app_tags: appid, tag_data, last_updated
 
Normally, I'd get these datasets from the Steam API, but both the reviews and tag data doesn't exist there. So there are two web scrapers written in R (porting to python pending): app_data_downloader.R which hits the Steam API for a list of all apps, filters to only games, and pulls associated metadata. The other, steam_tags_and_recs_downloader.R, takes the curated list of games and pulls the review and tag data for them.
