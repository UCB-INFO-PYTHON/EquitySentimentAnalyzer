
# EquitySentimentAnalyzer
<br>_Author_: Bobby Calzaretta<br>
_Contact_: rcalzaretta@ischool.berkeley.edu<br>
_Note_: Developed for MIDS Introduction to Python Programming Fall 2018.<br>

## Overview
The goal of this project was to create a utility with which to gauge the correlation between a given equity’s stock price performance and popular sentiment.  The project collects data on a user-selected publicly traded company within the NASDAQ-100, provide certain attributes back to the user upon request, and conduct a correlation analysis between the equity’s stock price and Twitter sentiment.  The project incorporates six separate classes to achieve this functionality.  

The first class of this project, NASDAQDirectory, collects information on the active components of the NASDAQ-100 from the index’s web page.  These components (ticker symbols and company names) are stored in a dictionary.  A table of the components ticket symbols and company names will be returned to the user via the print_directory method.  

The second and third class of the project interface with the Twitter API to collect and analyze tweets of a specified company.  The class TwitterAPI verifies and establishes access to the API.  The class TwitterDog inherits TwitterAPI’s functionality to fetch and analyze Twitter data for the past week.  It includes functions to clean tweets and gauge tweet sentiment.  The primary method, analyze_tweets, takes a search term and a count number (default 20), queries the Twitter API, and loops through each day of the past week.  As the program loops through each day, it collects the specified number of tweets at the company (e.g., “@Facebook”), employs the cleaning function, gauges the sentiment of each tweet using TextBlob’s algorithm which assigns a number between -1.0 (most negative sentiment) and 1.0 (most positive sentiment) to the text of the tweet, and calculates a total sentiment for the given date.  The program ignores retweets when calculating sentiment. 
    
The fourth class, BarchartDog, interfaces with the Bartchart API to collect trading data and basic company information.  The method fetch_trading returns daily closing price and volume data for a selected ticker symbol for the last week.  The method get_info returns basic company information for the selected ticker, including: the stock exchange the company is traded, the average trading volume, 52-week low, 52-week high, ex-dividend date, dividend yield, and annual dividend rate.  
    
The fifth and primary class inherits the aforementioned parent class methods to ultimately return a correlation coefficient between changes in a company’s price and changes in a company’s sentiment.  This class, PriceSentimentAnalyzer, employs functions to verify the user has selected a valid ticker from the NASDAQ-100 and to generate a clean term from the relevant company name to search for on Twitter.  It also includes a method, get_tweets, to return tweet examples for a specified company: a “@[company]” tweet and a “#[company]” tweet.  The primary method, analyze_company, takes a specified ticker symbol, verifies it is in the list of NASDAQ-100 components, cleans the company name to search for using the Twitter API, and calls the fetch_trading and analyze_tweets methods from its parent classes.  It then calculates the daily changes in price and sentiment before ultimately calculating a correlation coefficient for these two pieces of data.  
    
The last class, Menu, rolls the preceding functionalities into a user-friendly menu.  


## Challenges in Development
Initially, the project was planned to allow a user to collect equity and Twitter data over a user-selected period of time.  Unfortunately, both the Twitter API and Barchart API that this project relies upon restrict certain data to premium accounts.   For instance, the Twitter API limits data on tweets to those made within a week from the day of a query.  Therefore, the project had to be modified to collect and analyze daily data for this duration of time.  Given the inherently short data period by which this project is bounded, the feature of allowing user-specified time periods has been abandoned in favor of returning all data on a daily-basis for the past week.  Other information, such as a company’s industry, sector, and earnings release date was also found to be unavailable via the Barchart API.  

Other challenges included ensuring inheritance was conflict free in the PriceSentimentAnalyzer class.  For instance, the project required certain methods or attributes are not being overwritten within the child class. 


## Requirements and Dependencies
In order to run the Equity Sentiment Analyzer users must register for API credentials from Twitter and Barchart.  The Twitter registration page is located here: https://developer.twitter.com/en/apply-for-access.html.  The Barchart API is avilable here: https://www.barchart.com/ondemand/free-market-data-api.  API access is free upon registration.  

This project requires two packages outside of the standard Anaconda library.  These packages are “python-twitter” and “TextBlob.”  The former is a listed under Twitter's list of API libraries for Python.  The latter is a well referenced tool for text analysis.  Both can be simply and quickly installed using PIP.  The user can install these packages via the command line using the commands:
> pip install python-twitter <br>
> pip install textblob

Additional packages relied upon include: datetime, bs4, json, numpy, re, requests, sys, and warnings.


## Guidance for Implementation
The project can be fully accessed via the command line.  This program has a menu of options once launched via the terminal.  <br>Please access the application as follows:
> python ESA.py
