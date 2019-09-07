library(jsonlite)

# this script will hit the steam api for a complete list of all apps, what type they are
# (game vs app vs dlc, etc), and metadata like release dates



#
# get list of all steam appids to loop over
#

steam_apps <- data.frame(fromJSON("http://api.steampowered.com/ISteamApps/GetAppList/v0001/"))
names(steam_apps) <- c("appid", "name")
steam_apps <- steam_apps[with(steam_apps, order(appid)),]  



#
# known games list from previous runs
#


known_games <- read.table("steam_all_playtimes.txt", header=T, sep="\t")
known_games <- known_games[-1,]
unknown_games <- steam_apps[steam_apps$appid > max(known_games$response.games.appid),]
list_to_update <- rbind(known_games$response.games.appid, unknown_games$appid)
list_to_update <- unique(sort(list_to_update))





#
# all steam app data collector
#


all_app_details <- data.frame(NULL)

start_time <- Sys.time()

#i in list_to_update[which(list_to_update > 280040)] #checkpoint in case of http 503 errors
for (i in list_to_update){
  
  steam_app_details = tryCatch({
       fromJSON(sprintf("http://store.steampowered.com/api/appdetails/?appids=%i&l=english&cc=US", i))
     }, error = function(e) {
       Sys.sleep(60)
       fromJSON(sprintf("http://store.steampowered.com/api/appdetails/?appids=%i&l=english&cc=US", i))
     })
     
     
     
     names(steam_app_details) <- "results"
   
   if(steam_app_details$results$success){
     steam_app_df <- data.frame(
       
       "appid" = steam_app_details$results$data$steam_appid
       ,"name" = steam_app_details$results$data$name
       ,"type" = steam_app_details$results$data$type
       ,"categories" = I(list(steam_app_details$results$data$categories$description))  #note the I() inhibitor function to keep the list from expanding row-wise
       ,"genres" = I(list(steam_app_details$results$data$genres$description))
       ,"release_date" = steam_app_details$results$data$release_date$date
       ,"last_updated" = Sys.Date()
     )
     
     all_app_details <- rbind(all_app_details, steam_app_df)    
   }
     
   Sys.sleep(1.75)
   
   write.table(all_app_details, file = "all_app_details.txt", sep = "\t", row.names = FALSE, quote = FALSE)
   
   percent_complete <- nrow(all_app_details) / length(list_to_update)
   time_left <- start_time + ((length(list_to_update) - nrow(all_app_details)) * 1.75)
   print(sprintf("%i is done. %g percent complete, eta: %s", i, percent_complete, time_left))
  
  
}



all_game_details <- subset(all_app_details, subset = (type == 'game'))
write.table(all_game_details, "all_app_details.txt", sep = "\t", row.names = FALSE, quote = FALSE)











