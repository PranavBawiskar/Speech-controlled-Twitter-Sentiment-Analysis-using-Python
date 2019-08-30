import re
import os
import speech_recognition as sr
import string
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from gtts import gTTS

r = sr.Recognizer()
mic = sr.Microphone()


positive = "percentage of positive Tweets"
negative = "percentage of negative Tweets"

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'etJIyIfap2vpvh6msXJzDXWB6'
        consumer_secret = 'UB0u0VmS1khnkYWQlg86m6ducx6H9aomVNNtKoHiTxQAi8wwZT'
        access_token = '955354170944471040-ymf4CdfobcpphzMXnFxVU81bpOK36HU'
        access_token_secret = 'tYgOYOvkVAk0K15DCpsnH3yYEp5sF0YgZ8A9udrG4IedV'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count = 10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

def main():
    # creating object of TwitterClient Class
    api = TwitterClient()

    try:
        print("Please wait calibrating the microphone, pleasebe silent")
        with mic as source: r.adjust_for_ambient_noise(source,duration=5)
        print("Set min energy threshold value to {}".format(r.energy_threshold))
        print("====================================================")
        while True:
            with mic as source:
                try:
		    print("Let's check if we are good to go! please speak something!")
                    audio = r.listen(source,timeout = None)
                    print("Wait! I am Analysing...")
                    message = str(r.recognize_google(audio))
                    print("======================================")
                    print("Got it! you said: -"+message)
                    print("======================================")
                    print("Please speak the hashtag")
                    audio = r.listen(source,timeout = None)
                    print("Gathering your hashtag...")
                    hashtag = str(r.recognize_google(audio))
                    print("Your hashtag was: "+hashtag)
                    #calling function to get tweets for hashtag
                    tweets = api.get_tweets(query = hashtag,count = 200)
                    print("positive, negative or neutral ?")
                    audio = r.listen(source,timeout = None)
                    print("Wait I am Analysing your choice...")
                    choice = str(r.recognize_google(audio))
                    print("====================================")
                    print("GOT IT YOU WANT "+choice+" tweet data")
                    if choice=='positive':
                        tts=gTTS(text="Okay! Showing you the results for positive tweet percentage",lang='en')
                        tts.save("pcvoice.mp3")
                        os.system("mpg321 pcvoice.mp3")

                        # picking positive tweets from tweets
                        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
                        # percentage of positive tweets
                        print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
                        # printing first 5 positive tweets
                        print("\n\nPositive tweets:")
                        for tweet in ptweets[:10]:
                            print(tweet['text'])

                    elif choice=='negative':
                        tts=gTTS(text="Okay! Showing you the results for negative tweet percentage",lang='en')
                        tts.save("pcv3")
                        os.system("mpg321 pcvoice.mp3")

                        # picking negative tweets from tweets
                        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
                        # percentage of negative tweets
                        print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
                        # printing first 5 negative tweets
                        print("\n\nNegative tweets:")
                        for tweet in ntweets[:10]:
                            print(tweet['text'])
		    elif choice=='neutral':
			tts=gTTS(text="Okay! Showing you the results for the neutral tweet percentage",lang='en')
			tts.save("pcvoice.mp3")
			os.system("mpg321 pcvoice.mp3")

			#picking neutral tweets from tweets

                except sr.UnknownValueError:
                    print("Didn't Catch")

    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    # calling main function
    main()
