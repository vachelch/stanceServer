# stanceServer
## Description
`stanceServer` is an online Taiwanese news stance analysis tool, can realize state-of-the-art stance analysis performance. It provide a window for query, when people search in the query window, the news will be crawled from google news (Taiwan). Then, news are processed automatically and the stance relationship between query and news will be shown. What's more, people can see the how trend of the news change over time, you may also help us rectify the results. All in All, it concludes: Real Time Google News Crawler, Opinion Mining, Visualization and Feedback

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
`stanceServer` crawl the data from [google news](https://www.google.com.tw/), and the stance classification are basically from BERT, or Bidirectional Encoder Representations from Transformers. It is a new method of pre-training language representations which obtains state-of-the-art results on a wide array of Natural Language Processing (NLP) tasks.
More information
* [BERT](https://github.com/nodejs/node-gyp#on-macos)
