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
print("I am %s" % api.me().name)
chatbot = NeuralChatBot('ja_model_attn_adam/vocab.txt', 'ja_model_attn_adam')

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        text = status.text
        tid = status.id
        screen_name = status.entities['user_mentions'][0]['screen_name']
        retweeted = status.retweeted
        source = status.user.screen_name

        core_msg = re.sub('@\S+\s*', '', text)
        reply = chatbot.reply(core_msg)
        api2.update_status('@%s %s' % (source, reply.decode('utf-8')), tid)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['neural_chatbot'])
