#!/usr/bin/python
#Import packages
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
import json
import numpy as np
import re
import requests
import sys
import warnings

global TConKey
global TConSec
global TAccTok
global TAccSec
global BKey

TConKey = input("\nPlease enter your \x1B[3mTwitter\x1B[23m API Consumer Key: ")
TConSec = input("\nPlease enter your \x1B[3mTwitter\x1B[23m API Consumer Secret: ")
TAccTok = input("\nPlease enter your \x1B[3mTwitter\x1B[23m API Access Token: ")
TAccSec =  input("\nPlease enter your \x1B[3mTwitter\x1B[23m API Access Secret: ")
BKey = input("\nPlease enter your \x1B[3mBarchart\x1B[23m API Consumer Key: ")


#Try importing packages outside of Anaconda library
try:
    import twitter
    from textblob import TextBlob
except ModuleNotFoundError:
    print("Program requires user to install 'python-twitter' and 'textblob' packages.",
          "\nUse pip install on command line to download this funcationality")
    sys.exit()

#Master class for NASDAQ-100 Direcotry
class NASDAQDirectory:
    #Fetch current NASDAQ-100 components page
    url = "https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx"
    
    #Handle if no Internet connection
    try:
        r = requests.get(url).text
    except:
        raise ("Package requests cannot execute.",
        "Verify it is installed and that an Internet connection is active.")

    soup = BeautifulSoup(r, "html.parser")

    x = soup.find('div', attrs={'id': 'main-content-div'})
    comp = re.compile("\[(\[.+\])\];var", re.DOTALL)
    component_table = comp.search(x.text.strip())

    #Primary directory of components and names
    def __init__(self):
        """Class to create dictionary of NASDAQ-100 components"""
        self.directory = dict()
        for item in NASDAQDirectory.component_table.group(1).split('],'):
                self.directory.update({re.sub('\[|\]|\"', '', item).split(',')[0].strip(): 
                                       re.sub('\[|\]|\"', '', item).split(',')[1].strip()})
                
    def print_directory(self):
        """Returns a list of current NASDAQ-100 component companies and ticker symbols"""
        #Header for output
        print('{:<53} {:<10}'.format('\033[4m'+'Company:'+'\033[0m', '\033[4m'+'Ticker:'+'\033[0m'))
        
        #Output ticker symbol and company name
        for key, value in self.directory.items():
            print('{:<45} {:<10}'.format(value, key))

#Parent class for Twitter API authentication
class TwitterAPI:
    #Inialize API connection
    def __init__(self):
        #Authentication Keys
        consumer_key =  TConKey
        consumer_secret = TConSec
        access_token =  TAccTok
        access_token_secret = TAccSec

        #Inialize and test API connection
        try:
            self.api= twitter.Api(consumer_key, 
                                  consumer_secret, 
                                  access_token, 
                                  access_token_secret
                                  )
            
            self.api.VerifyCredentials()
        except:
            print("Error: Could not authenticate.  Check Twitter keys or Internet connection then try again.")
            exit()
            
#Sub class for Twitter API use
class TwitterDog(TwitterAPI):
    def __init__(self):
        """Class to collect last week's tweet and sentiment data for given term."""
        TwitterAPI.__init__(self)
        
    def clean(self, tweet):
        """Removes links and special characters"""
        return ' '.join(re.sub("(https:\/\/t.co\/[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(@[A-Za-z0-9]+)", 
                               " ", tweet).split())
    
    def fetch_sentiment(self, tweet):
        """Applies TextBlob's sentiment analysis to evaluate tweets"""
        return TextBlob(self.clean(tweet)).sentiment.polarity
    
    def analyze_tweets(self, company, count = 20):
        """Fetches tweet sentiment for selected company by day for last week.
        API limited to last week of data."""
        if count == 0 or count != round(count):
            return "Invalid entry for count.  Please enter a positive integer."
        else:
            tweets = list()
            self.count = count
            self.company = '@' + company
            self.total = 0 
            self.tot_analyzed = 0
            #Intialize data dictionaries
            self.sentiments = dict()
            start = datetime.today() - timedelta(7)
            end = datetime.today() + timedelta(1)
            try:
                #Loop through days in last week
                for d in range((end - start).days):
                    #Grab sample of tweets from day (default 20); rate limits may apply if extended too far
                    s = start + timedelta(d)
                    e = start + timedelta(d + 1)
                    fetched_tweets = self.api.GetSearch(term = self.company, 
                                                        since = s.strftime('%Y-%m-%d'), 
                                                        until = e.strftime('%Y-%m-%d'), 
                                                        count=self.count, 
                                                        lang='en')

                    sentiment = 0
                    temp_count = 0
                    for tweet in fetched_tweets:
                        #Add text, sentiment to dictionary
                        parsed_tweet = dict()
                        parsed_tweet['text'] = self.clean(tweet.text)
                        parsed_tweet['sentiment'] = self.fetch_sentiment(tweet.text)
                        self.total += 1
                        
                        # appending parsed tweet to tweets list
                        if tweet.retweet_count > 0:
                            # if tweet has retweets, ensure that it is appended only once
                            if parsed_tweet not in tweets:
                                tweets.append(parsed_tweet)
                                sentiment += parsed_tweet['sentiment']
                                self.tot_analyzed += 1
                                temp_count += 1
                        else:
                            sentiment += parsed_tweet['sentiment']
                            self.tot_analyzed +=1 
                            temp_count += 1
                    if temp_count == 0:
                        sentiment = np.nan
                    self.sentiments.update({s.strftime('%Y-%m-%d'): sentiment})

                #Return tweet data
                print('\n\033[4m' + 'Sentiment Data for', self.company + ':\033[0m')
                for key, value in self.sentiments.items():
                    print(key, ":", round(value, 4))
                print("Total tweets available:", self.total)
                print("Total tweets analyzed:", self.tot_analyzed)

            #Handle if error
            except (Exception) as e:
                raise "Error : " + str(e)
            
    def last_tweet(self, company):
        """Prints last Tweet @company and #company"""
        if company == "":
            pass
        else:
            self.company = '@' + company
            tweet = self.api.GetSearch(term = self.company, count=1, lang='en')
            for t in tweet:
                print("\nSearch term: " + self.company, "\nTweet: " + re.sub("(https:\/\/t.co\/[A-Za-z0-9]+)", "",t.text), "\nCreated: " + t.created_at, end="\n")
             
            self.company = '#' + company
            tweet = self.api.GetSearch(term = self.company, count=1, lang='en')
            for t in tweet:
                print("\nSearch term: " + self.company, "\nTweet: " + re.sub("(https:\/\/t.co\/[A-Za-z0-9]+)", "",t.text), "\nCreated: " + t.created_at, end="\n")
        
#Parent class for Barchart API authentication and data fetch
class BarchartDog:
    Start = datetime.today() - timedelta(7)
    Key = BKey

    def __init__(self):
        """Class to collect stock trade information"""
        self.prices = dict()
        self.volumes = dict()
       
    def fetch_trading(self, company):
        """Collects price and volume data from barchart.com for last week"""
        url = ("https://marketdata.websol.barchart.com/getHistory.json?" + 
               "apikey=" + BarchartDog.Key + 
               "&symbol=" + company.upper() + 
               "&type=daily" + 
               "&startDate=" + BarchartDog.Start.strftime('%Y-%m-%d'))


        try:    
            json_file = requests.get(url).text
            json_loads = json.loads(json_file)

        #Handle if invalid credentials 
        except:
            print("Error: Could not authenticate.  Check Barchart keys or Internet connection then try again.")
            exit()
      
        #Collect data from Barchart API
        try:
            #loop through daily data
            for day in json_loads['results']:
                self.prices.update({day['tradingDay']: day['close']})
                self.volumes.update({day['tradingDay']: day['volume']})
                
            #return trade data
            print('\n\033[4m' + 'Price Data:' +'\033[0m')
            for key, value in self.prices.items():
                print(key, ":", value)
            print('\n\033[4m' + 'Volume Data:' +'\033[0m')
            for key, value in self.volumes.items():
                print(key, ":", value)
                
        #Handle if user selects unlisted equity
        except TypeError:
            print("Error: Equity not listed.")
        #Handle if issue with API access (e.g. rate limit)
        except Exception as e:
            print("Error: Issue with API.  Please try again latter. " + str(e))
            
    def get_info(self, company):
        """Collects Equity information from barchart.com for last week"""
        url = ("https://marketdata.websol.barchart.com/getQuote.json?" + 
               "apikey=" + BarchartDog.Key + 
               "&symbols=" + company.upper() + 
               "&fields=" + "exDividendDate" + "%2C" + 
               "dividendRateAnnual" + "%2C" + 
               "dividendYieldAnnual" + "%2C" + 
               "sharesOutstanding" + "%2C" + 
               "avgVolume" + "%2C" + 
               "fiftyTwoWkLow" + "%2C" + 
               "fiftyTwoWkHigh")
        try:                      
            json_file = requests.get(url).text
            json_loads = json.loads(json_file)
        #Handle if invalid credentials 
        except:
            print("Error: Could not authenticate.  Check Barchart keys or Internet connection then try again.")
            exit()
       
        #Collect info from Barchart API
        try:
            self.exchange = json_loads['results'][0]['exchange']
            self.avgVolume = json_loads['results'][0]['avgVolume']
            self.fiftyTwoWkLow = json_loads['results'][0]['fiftyTwoWkLow']
            self.fiftyTwoWkHigh = json_loads['results'][0]['fiftyTwoWkHigh']
            self.exdiv_date = json_loads['results'][0]['exDividendDate']
            self.divyield = json_loads['results'][0]['dividendYieldAnnual']
            self.divrate = json_loads['results'][0]['dividendRateAnnual']

            #Return trade data
            print('\n\033[4m'+'Equity Info:'+'\033[0m')
            print("Stock exchange:", self.exchange, 
                 "\nAverage volume:", self.avgVolume,
                 "\n52-week low:", self.fiftyTwoWkLow,
                 "\n52-week high:", self.fiftyTwoWkLow,
                 "\nex-Dividend date:", self.exdiv_date,
                 "\nDividend yield:", self.divyield,
                 "\nAnnual dividend rate:", self.divrate)
            
        #Handle if user selects unlisted equity
        except TypeError:
            print("Error: Equity not listed.")
        #Handle if issue with API access (e.g. rate limit)
        except Exception as e:
            print("Error: Issue with API.  Please try again later. " + str(e))

#Primary class to run analysis    
class PriceSentimentAnalyzer(NASDAQDirectory, BarchartDog, TwitterDog):
    def __init__(self):
        """Class to return stock price and volume data, Twiiter social media sentiment, 
        and run correlation between daily price changes and sentiment changes."""
        super(PriceSentimentAnalyzer, self).__init__()
        #Initialize parent classes
        NASDAQDirectory.__init__(self)
        BarchartDog.__init__(self)
        TwitterDog.__init__(self)
    
    def create_twitter_term(self, term):
        """Makes term a more Twitter-searchable."""
        if term is not None:
            return re.sub(" Inc\.$| Plc$| plc$| Ltd\.$| N\.V\.$| |,|\.", "", term).lower()
        else:
            pass
    
    def find_fullname(self, term):
        """Verifies ticker in NASDAQ-100 and find full company name."""
        #Handle if ticker not in NASDAQ-100
        try:
            self.directory[term]
            return self.directory[term]
        except (KeyError, Exception):
            print("Error: equity not listed in NASDAQ-100.",
                  "Please access enter 1 for list of valid ticker symbols.")
            return ""
         
    #Secondary function to return latest tweet @ and # for company
    def get_tweets(self, selection):
        company_name = self.find_fullname(selection)
        print(company_name)
        twitter_search_term = self.create_twitter_term(company_name)
        return self.last_tweet(twitter_search_term)
  
    #Primary function to return data and run correlation
    def analyze_company(self, selection, num_tweets=20):
        """Returns social media, price, and volume data and correlation for user-selected ticker"""
        if num_tweets == 0 or num_tweets != round(num_tweets):
            return "Invalid entry for count.  Please enter a positive integer."
        else:
            #Verify selection in NASDAQ-100
            company_name = self.find_fullname(selection)
            if company_name == None:
                pass
            else:
                self.selection = selection
                self.num_tweets = num_tweets

                #Print user selection and company
                print("\nYou selected: ", self.selection, "which is " + company_name, 
                      "\nCollecting equity and social media data...")

                #Add clean company name for Twitter search
                twitter_search_term = self.create_twitter_term(company_name)

                #Access and Print API data through parent methods
                self.fetch_trading(self.selection)
                self.analyze_tweets(twitter_search_term, self.num_tweets)

                #Prepare data lists to correlate
                dlist1 = list()
                dlist2 = list()
                last1 = None
                last2 = None

                #Loop through daily prices
                for key, value in self.prices.items():
                    y, m, d = (int(i) for i in key.split('-'))
                    day = date(y, m , d)
                    #Analyze only prices from weekdays (i.e., days when active trading)
                    if day.weekday() < 5: 
                        #Identify previous data values for calculation of daily change
                        if last1 is None:
                            last1 = value
                            last2 = self.sentiments[key]
                            continue 

                    #Price change
                    dlist1.append(value - last1)
                    #Twitter sentiment change
                    dlist2.append(self.sentiments[key] - last2) 

                #Run correlation 
                with warnings.catch_warnings():
                    warnings.filterwarnings('error')
                    #NUMPY returns warning if divide by zero error occurs in correlation calculation
                    try:
                        ans = round(np.corrcoef(dlist1, dlist2)[1,0],4)
                    #Handle divide by zero error
                    except Warning:
                        return "Error: Correlation cannot be calculated.  Divide by zero error."
                    if np.isnan(ans):
                         return "Error: Correlation cannot be calculated.  Missing data."
                       

                    #Return correlation to user if calculated
                    print("\nThe correlation coefficient of " + company_name + "'s (" + selection + ")",
                          "daily price and sentiment changes",
                          "for week of " + (datetime.today() - timedelta(7)).strftime('%Y-%m-%d') + 
                          " is:", ans)

class Menu(PriceSentimentAnalyzer):
    """Packages functionality into a user-friendly menu."""
    def __init__(self):
        print("Welcome to the equity sentiment analyzer.  Please wait a moment while the program loads.")
        super(Menu, self).__init__()
        #Initialize parent classes
        PriceSentimentAnalyzer.__init__(self)

    def print_menu(self):
        #Make methods dictionary-accessible
        self.options = {
        "1": self.print_directory, 
        "2": self.get_info, 
        "3": self.get_tweets, 
        "4": self.analyze_company,
        }

        print("_____________________________________________________"
            "\nPlease selecect from one of the following options:\n",
            "Enter 1 for: Directory of a NASDAQ-100 Components\n", 
            "Enter 2 for: Return Basic Trading Information on Component\n", 
            "Enter 3 for: Print a sample of @ and # Tweets for Given Component\n",
            "Enter 4 for: Calculate Correlation of Change in Daily Stock Prices and Twitter Sentiment\n",
            "Enter Q for: Terminate the Program\n")

#Run from terminal
x = Menu()
quit = False
while quit == False:
    x.print_menu()
    inp1 = input("\nWhat would you like to do? ").upper()
    while inp1 not in("1", "2", "3", "4", "Q"):
        inp1 = input("Invalid selection.  Please select from the options above: ").upper()
    if inp1 == "1":
        x.options[inp1]()
    elif inp1 in("2", "3"):
        inp2 = input("Please select NASDAQ-100 component: ").upper()
        x.options[inp1](inp2)
    elif inp1 == "4":
        inp2 = input("Please select NASDAQ-100 component: ").upper()
        try:
            inp3 = int(input("Please select the number of daily tweets to analyze: "))
            x.options[inp1](inp2, inp3) 
        except ValueError:
            print("Invalid entry. Proceeding with default number of daily tweets (20).")
            x.options[inp1](inp2)       
    elif inp1 == "Q":
        quit = True
print("Thank you for using the equity sentiment analyzer.  Goodbye!")
sys.exit()
