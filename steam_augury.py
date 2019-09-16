import pandas as pd
import requests
import json
import os
from progressbar import ProgressBar
import sys




#checking user arguments for steam api key and valid steam id
api_key = sys.argv[1]
steam_id = sys.argv[2]


#instantiating sigmoid function for user fingerprint analysis
def sigmoid(x):
    return 1/(1+2.718281**(-x))


#loading up tag data
tags_df = pd.read_csv("data\\app_tags_20190724.txt", sep = "\t")
tags_df = tags_df.drop_duplicates()  #remove duplicates
tags_df = tags_df[tags_df['tag_data'].apply(len) > 2]  #filtering for games that don't have tag data yet


#downloading user stats from steam API
user_url = ("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json&include_played_free_games=1&include_appinfo=1".format(api_key, steam_id))

api_data = requests.get(user_url).json()
user_data = pd.DataFrame.from_dict(api_data['response']['games'])
user_data = user_data[['appid','name', 'playtime_forever']]
user_data['playtime_hours'] = user_data['playtime_forever']/60
user_data = user_data[user_data['playtime_hours'] > 0]
user_data['personal_sigmoid'] = (user_data['playtime_hours'] - user_data['playtime_hours'].median()).apply(sigmoid)


#this is because the tags list is incomplete and the loop will error if trying an app i haven't gotten the tag data for yet
user_apps_to_search = user_data[user_data['appid'].isin(tags_df['appid'])]['appid']

fingerprint_df = pd.DataFrame()

for i in user_apps_to_search:
    
  # for each game in user's library with nonzero playtime
  # apply the user's sigmoid value (ie engagement level) to the tag distrubiton
  # sum up tag distributions to get final score per tag
    
  user_interest_value = user_data[user_data['appid']==i].iloc[0,4]
  
  # find the tag dictionary related to the appid and convert dictionary to dataframe
  app_tags_converted = pd.DataFrame(json.loads(tags_df[tags_df['appid']==i].iloc[0,1]))
  app_tags_converted['tag_percent'] = app_tags_converted['count'] / sum(app_tags_converted['count'])
  
  # apply sigmoid value proportionally to the tags
  fingerprint_df_temp = pd.DataFrame({
          'name': app_tags_converted['name'],
          'normalized_sigmoid_value' : app_tags_converted['tag_percent'] * user_interest_value
          })
  
  fingerprint_df = fingerprint_df.append(fingerprint_df_temp)

fingerprint_df_grouped = fingerprint_df.groupby('name').sum()
fingerprint_df_grouped = fingerprint_df_grouped.reset_index()

  
#great so now we have the user's tag fingerprint, where the higher the score, the more likely they'll enjoy a game with that tag

#for each game in the tag list,
# apply fingerprint to game's tag list to get overall score for game (essentially a dot product but we have to unnest the dictionary first)
# sort games from tag list by score descending


app_scores = pd.DataFrame()

tag_search = tags_df[~tags_df['appid'].isin(user_data['appid'])]['appid']
tag_search = tag_search.tolist()


pbar = ProgressBar()

for i in pbar(tag_search):
  
  #same procedure as before with dictionary conversion
  app_tags_converted = pd.DataFrame(json.loads(tags_df[tags_df['appid']==i].iloc[0,1]))
  app_tags_converted['tag_percent'] = app_tags_converted['count'] / sum(app_tags_converted['count'])
  
  
  relevant_fingerprint = fingerprint_df_grouped[fingerprint_df_grouped['name'].isin(app_tags_converted['name'])]
  #relevant_fingerprint = relevant_fingerprint.reset_index()
  
  #inner join here removes NAs from game tags I haven't played yet (ie: dinosaurs tag)
  app_tags_converted_join = pd.merge(app_tags_converted, relevant_fingerprint, on='name')
  app_tags_converted_join['tag_score'] = app_tags_converted_join['tag_percent'] * app_tags_converted_join['normalized_sigmoid_value']
 
    
  df_dict = {
          'appid': i,
          'score': sum(app_tags_converted_join['tag_score']),
          'num_tags' : len(app_tags_converted_join),
          'total_tag_votes' : sum(app_tags_converted_join['count'])
          }
  
  app_scores_temp = pd.DataFrame([df_dict])
    
  app_scores = app_scores.append(app_scores_temp)
  

  
#above loop likely to have some optimization done on it.
#currently 3.6x slower than the equivalent R script  


app_scores = app_scores.reset_index()


app_details = pd.read_csv("data\\all_app_details_20190719.txt", sep = "\t", encoding = 'unicode_escape')
app_details = app_details.drop_duplicates()

app_reviews = pd.read_csv("data\\app_reviews_20190724.txt", sep = "\t", encoding = 'unicode_escape')
app_reviews = app_reviews.drop_duplicates()

app_scores_joined = pd.merge(app_scores, app_details, on='appid', how='left')
app_scores_joined = pd.merge(app_scores_joined, app_reviews, on='appid', how='left')

app_scores_joined = app_scores_joined[['appid', 'score', 'num_tags', 'total_tag_votes', 'name', 'release_date', 'positive_reviews', 'total_reviews']]
#app_scores_joined['review_rating'] = app_scores_joined['positive_reviews'] / app_scores_joined['total_reviews']

app_scores_joined['review_rating'] = app_scores_joined['positive_reviews'].div(app_scores_joined['total_reviews'].where(app_scores_joined['total_reviews'] != 0 , 0))
app_scores_joined['review_rating'] = app_scores_joined['review_rating'].fillna(0)

num_tags_median = app_scores_joined['num_tags'].median()
tag_votes_median = app_scores_joined['total_tag_votes'].median()
total_reviews_median = app_scores_joined['total_reviews'].median()
review_rating_median = app_scores_joined['review_rating'].median()

#default recommendation flags
#users can sort from the output file based on raw data
def rec_flag(row):
    if (row['num_tags'] >= num_tags_median and
        row['total_tag_votes'] >= tag_votes_median and
        row['total_reviews'] >= total_reviews_median and
        row['review_rating'] >= review_rating_median
        ):
        val = 1
    else:
        val = 0
    return val

app_scores_joined['rec_flag'] = app_scores_joined.apply(rec_flag, axis=1)
app_scores_joined = app_scores_joined.sort_values(['rec_flag', 'score'], ascending=False)


#write final data to file for user to play with
#default is current working directory
app_scores_joined.to_csv('app_scores.txt', sep='\t', index = False)

print('\n')
print("The top 10 games you should check out are:")
print('\n')
print(app_scores_joined['name'][0:9])
print('\n')
print('For more info, see the app_scores.txt file in directory {}'.format(os.getcwd()))
print('\n')





















  
  
