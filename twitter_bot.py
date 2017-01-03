from neural_chat_bot import NeuralChatBot
import tweepy
import re

CK=""
CS=""
AT=""
AS=""

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)
api2 = tweepy.API(auth)
print("I am %s %s" % (api.me().name, api.me().screen_name))
chatbot = NeuralChatBot('ja_model/vocab.txt', 'ja_model')

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        text = status.text
        tid = status.id
        screen_name = status.entities['user_mentions'][0]['screen_name']
        retweeted = status.retweeted
        source_name = status.user.screen_name
        source_id = status.user.id

        if source_name == api.me().screen_name:
            return

        core_msg = re.sub('@\S+\s*', '', text)
        reply = chatbot.reply(core_msg)
        try:
            reply_text = '@%s %s' % (source_name, reply.decode('utf-8'))
            print '%s -> %s' % (text, reply_text)
            api2.update_status(reply_text, tid)
            api2.create_friendship(source_id)
        except tweepy.TweepError as e:
            print e

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['neural_chatbot'])
