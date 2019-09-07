
# this script scrapes the steam store webpages over a list of games to get the positivity rating, number of reviews, and tag distribution for a given game


library('rvest')
library('jsonlite')
library('httr')


all_games <- read.table("all_app_details.txt", quote = "", sep="\t", header=T, as.is = T, comment.char = "")
all_game_ids <- all_games$appid


reviews_df <- NULL
tag_data_storage <- NULL



start_time <- Sys.time()
initial_eta <- start_time + (length(all_game_ids) * 1.75)
initial_eta2 <- start_time + + ((length(all_game_ids) - match(i, all_game_ids)) * 1.75)

#i in all_game_ids[which(all_game_ids > 224040)] #checkpoint in case the loop breaks
for(i in all_game_ids){
  
  
  
  #this is because the steam website sometimes returns a 500 error. if it does, wait a minute for it to catch back up again
  url <- tryCatch({
    sprintf("https://store.steampowered.com/app/%i", i)
  }, error = function(e) {
    Sys.sleep(90)
    sprintf("https://store.steampowered.com/app/%i", i)
  })
  
  
  
  #this is to set cookies to beat the mature content redirect page
  session <- html_session(url
                          ,set_cookies(
                            'wants_mature_content'='1'
                            ,'birthtime' = '189302401'
                            ,'lastagecheckage' = '1-January-1976'
                          )
  )
  
  
  webpage <- read_html(session)
  
  
  #
  # review count parser
  #
  
  
  positive_reviews <- webpage %>%
    html_nodes("div.review_ctn #review_summary_num_positive_reviews") %>%
    html_attr("value") %>%
    as.numeric()
  
  total_reviews <-   webpage %>%
      html_nodes("div.review_ctn #review_summary_num_reviews") %>%
      html_attr("value") %>%
      as.numeric()
  
  
  #check for missing data and reassign
  if(length(total_reviews) == 0){
    total_reviews = 0
    positive_reviews = 0
  }
  
  
  reviews_df_temp <- data.frame(
    "app_id" = i
    ,positive_reviews
    ,total_reviews
    ,"last_updated" = Sys.Date()
  )
  
  reviews_df <- rbind(reviews_df_temp, reviews_df)
  
  write.table(reviews_df, file = "app_reviews.txt", sep = "\t", row.names = FALSE, quote = FALSE)
  
  
  
  #
  # tag data parser
  #
  
  
  #pull all scripts running on the page
  data <- html_nodes(webpage, css = "script") %>% html_text()
  
  
  
  #from the scripts, find the one that contains "InitAppTagModal", which is the tag distribution data
  #need a tryCatch() here since if a game's been delisted from the store, it won't return any tag data. 
   
  tryCatch(
    {
      
      #find the javascript that contains the tag data
      tag_data <- data[lapply(data,function(x) length(grep("InitAppTagModal",x,value=FALSE))) == 1]
      
      
      #cleanup
      tag_data <- regmatches(tag_data, gregexpr("[?<=\\[].*?[?=\\]]", tag_data, perl=T))[[1]][1]
      tag_df <- fromJSON(tag_data)
      
      #store in data frame for writing to file
      tag_data_storage_temp <- data.frame(
        "appid" = i
        ,tag_data
        ,"last_updated" = Sys.Date()
        ,stringsAsFactors = F
      )
      
      tag_data_storage <- rbind(tag_data_storage_temp, tag_data_storage)
      
      write.table(tag_data_storage, file = "app_tags.txt", sep = "\t", row.names = FALSE, quote = FALSE)
      
    }
    ,error = function(doNothing){}
  )
  
  
  
  
  #printout monitor
  percent_complete <- match(i, all_game_ids) / length(all_game_ids) * 100
  time_left <- initial_eta + ((length(all_game_ids) - match(i, all_game_ids)) * 1.75)
  Sys.sleep(1.75)
  print(sprintf("appid %i is done at %s. %g percent complete, eta: %s", i, Sys.time(), percent_complete, time_left))
}



    
    
