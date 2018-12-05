# Chinese Discovery News
Google News Crawler, Opinion Mining and Visualization

# Directory Structure
```
-src\
  -NewsCrawler\
    -GoogleNews.py
    -NewsCrawler.py
  -OpinionAnalysis
    -CopeOpi\ (Sentiment Analysis Tool from Lun-Wei Ku)
    -data\
	-dict\ (Dictonary for Jieba Segmentation, NTUSD)
    -StanfordPosTagger\
    -Analysis.py
  -OpinionDB
    -opinionDB.py
  -opinionManager.py
  -server.py
```

# Quick Start
```
$python3 src/server.py
```

# To-do List
* OpinionAnalysis
  - Correctable Learning Algorithm
  - Better Stance Classfication
* User Interface
  - Loading Bar
  - Date range
