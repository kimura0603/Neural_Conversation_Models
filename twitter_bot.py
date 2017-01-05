from neural_chat_bot import NeuralChatBot
from collections import defaultdict
import tweepy
import time
import datetime
import re

CK="" # consumer key
CS="" # consumer secret
AT="" # access token
AS="" # access token secret

MENTION_INTERVAL = 600

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)
api_stream = tweepy.API(auth)
print("I am %s %s" % (api.me().name, api.me().screen_name))
chatbot = NeuralChatBot('ja_model/vocab.txt', 'ja_model', beam_size=100)

def print_log(msg):
    date_str = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print '%s: %s' % (date_str, msg)

def reply(text, source_name, tid):
    core_msg = re.sub('@\S+\s*', '', text)
    reply = chatbot.reply(core_msg)
    if not reply:
        return
    try:
        reply_text = '@%s %s' % (source_name, reply.decode('utf-8'))
        print_log('replying: %s -> %s' % (text, reply_text))
        api.update_status(reply_text, tid)
    except tweepy.TweepError as e:
        print_log(str(e))

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        text = status.text
        tid = status.id
        screen_name = status.entities['user_mentions'][0]['screen_name']
        retweeted = status.retweeted
        source_name = status.user.screen_name
        source_id = status.user.id

        print_log('got message: @%s %s' % (screen_name, text))

        if source_name == api_stream.me().screen_name:
            return

        reply(text, source_name, tid)
        try:
            api.create_friendship(source_id)
        except tweepy.TweepError as e:
            print_log(str(e))

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api_stream.auth, listener=myStreamListener)
myStream.filter(track=['neural_chatbot'], async=True)

last_reply = defaultdict(int)
seen_tid = set()
while True:
    try:
        my_name = api_stream.me().screen_name
        my_followers = api.followers_ids(api.me().id)
        my_friends = api.friends_ids(api.me().id)
        for user_id in set(my_followers) - set(my_friends):
            api.create_friendship(user_id)
        timeline = api.home_timeline()
    except tweepy.TweepError as e:
        print_log(str(e))
        continue
        
    t = int(time.time())
    print_log('got %d messages from timeline' % len(timeline))
    for status in timeline:
        text = status.text
        tid = status.id
        ttime = int(time.mktime(status.created_at.timetuple()))
        source_name = status.user.screen_name
#        print_log("got from timeline: %s by %s" % (status.text, status.user.screen_name))
        if status.user.screen_name == my_name:
#            print "this is my own tweet: not responding"
            continue
        if status.user.id not in my_followers:
#            print "@%s is not following me" % status.user.screen_name
            continue
        if status.in_reply_to_status_id:
#            print "this is a reply: not responding"
            continue
        if '@' in status.text:
#            print "this is a mention: not responding"
            continue
        if tid in seen_tid:
            continue
        seen_tid.add(tid)
        if t - last_reply[source_name] < MENTION_INTERVAL:
            print_log("recently replied to this user %s: not responding" % staus.user.screen_name)
            continue
        if t - ttime >= MENTION_INTERVAL:
            print_log("too old tweet (%d seconds ago, %s, %s): not responding" % (t - ttime, status.text, status.user.screen_name))
            continue
        reply(text, source_name, tid)
        last_reply[source_name] = t
        
    time.sleep(600)
