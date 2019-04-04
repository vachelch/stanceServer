# stanceServer
## Description
`stanceServer` is an online Chinese news stance analysis tool, it realize state-of-the-art stance analysis performance. In details, it provides a window for query, when people search in the query window, the news (Taiwan) will be crawled from google news. Then, news are processed automatically and the stance relationship between query and news will be shown. What's more, people can see the trend of news about the query change over time. You may also help us when you use it, by rectifying the results to teach the machine to train better classifier.

## Functions
* Real Time Google News Crawler
* Opinion Mining
* Visualization
* Feedback

## File Structure
```ascii
-<src>\
  -<app>\
    -<static>\
    -<templates>\
  -<NewsCrawler>\
    -GoogleNews.py
    -NewsCrawler.py
  -<OpinionAnalysis>
    -<bert>\
    -<dict>\
    -Analysis.py
    -GetOpinion.py
  -<OpinionDB>
    -opinionDB.py
    -opinion.db
  -opinionManager.py
  -server.py
  -global_set.py
```

## Start server
```bash
$python3 src/server.py
```

## About
`stanceServer` crawl the news from [google news](https://www.google.com.tw/), and the stance classification are basically from BERT, or Bidirectional Encoder Representations from Transformers. It is a new method of pre-training language representations which obtains state-of-the-art results on a wide array of Natural Language Processing (NLP) tasks.  
More information:
* [BERT](https://github.com/google-research/bert)
