from neural_chat_bot import NeuralChatBot
from collections import defaultdict
import tweepy
import time
import datetime
import re

CK="XI6LgIYryFo3a1NBRTzMOEgIW" # consumer key
CS="gK3WskBCLaagv6qMUxCyYwOxErd5m42HfZTIrReYKRKOB2hiMg" # consumer secret
AT="816229037278314496-rl9SDPslBOyldB2WGwl51Uj8E4tkSOp" # access token
AS="RL5cuA8uJ0MpTxxn4tQsjaP9cf2KNLLFULgEc6IPiJufx" # access token secret

MENTION_INTERVAL = 60*60*24*7 # 7 days

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth, wait_on_rate_limit=True)
api_stream = tweepy.API(auth, wait_on_rate_limit=True)
chatbot = NeuralChatBot('ja_model_spm/vocab.txt', 'ja_model_spm', beam_size=100)
last_reply = defaultdict(int)
seen_tid = set()
status_ids_i_replied = set()

def get_status_ids_i_replied(api, last_reply):
    out = set()
    page = 1
    while True:
        my_tweets = api.user_timeline(api.me().id, page=page)
        cnt = 0
        for t in my_tweets:
            cnt += 1
            ttime = int(time.mktime(t.created_at.timetuple()))
            if t.in_reply_to_screen_name and last_reply[t.in_reply_to_screen_name] < ttime:
                last_reply[t.in_reply_to_screen_name] = ttime
            if t.in_reply_to_status_id:
                out.add(t.in_reply_to_status_id)
        if cnt == 0:
            break
        page += 1
    return out

def get_tweets_to_me(api):
    out = []
    max_id = None
    while True:
        tweets = api.search('@' + api.me().screen_name, max_id=max_id, count=100)
        cnt = 0
        for t in tweets:
            cnt += 1
            if not max_id or max_id > t.id:
                max_id = t.id - 1
            if t.retweeted or t.text.startswith('RT') or t.text.startswith('QT'):
                continue
            if t.author.id == api.me().id:
                # my tweet
                continue
            out.append(t)
        if cnt == 0:
            break
    return out

def get_tweets_to_reply(api, status_ids_i_replied):
    tweets_to_me = get_tweets_to_me(api)
    tweets_to_reply = filter(lambda t: t.id not in status_ids_i_replied, tweets_to_me)
    return tweets_to_reply

def print_log(msg):
    date_str = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print '%s: %s' % (date_str, msg)

def reply(api, text, source_name, tid, reply_postfix = ''):
    if tid in status_ids_i_replied:
        print_log('already replied this tweet: %s %s' % (source_name, text))
        return
    status_ids_i_replied.add(tid)
    core_msg = re.sub('@\S+\s*', '', text)
    reply = chatbot.reply(core_msg)
    cur_time = int(time.time())
    last_reply[source_name] = cur_time
    if not reply:
        return
    try:
        reply_text = '@%s %s' % (source_name, reply.decode('utf-8') + reply_postfix)
        print_log('replying: %s -> %s' % (text, reply_text))
        api.update_status(reply_text, tid)
    except tweepy.TweepError as e:
        print_log(str(e))

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            text = status.text
            tid = status.id
            screen_name = status.entities['user_mentions'][0]['screen_name']
            retweeted = status.retweeted
            source_name = status.user.screen_name
            source_id = status.user.id

            print_log('got message: @%s: %s' % (source_name, text))

            if tid in seen_tid:
                seen_tid.add(tid)
                print_log("already seen this message")
                return
        
            if source_name == api_stream.me().screen_name:
                return

            reply(api, text, source_name, tid)
            try:
                api.create_friendship(source_id)
            except tweepy.TweepError as e:
                print_log(str(e))
        except:
            pass

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api_stream.auth, listener=myStreamListener)
myStream.filter(track=['neural_chatbot'], async=True)
status_ids_i_replied = get_status_ids_i_replied(api, last_reply)

cur_time = int(time.time())
for k, v in last_reply.iteritems():
    print_log('last_reply[%s] = %d seconds ago' % (k, cur_time - v))

print_log('Ready')        

while True:
    time.sleep(60)
    catch_up = True

    try:
        tweets_to_reply = get_tweets_to_reply(api, status_ids_i_replied)
        for t in tweets_to_reply:
            print_log('got message in catch up mode: @%s %s' % (t.author.screen_name, t.text))
            cur_time = int(time.time())
            ttime = int(time.mktime(t.created_at.timetuple()))
            reply_postfix = ''
            if cur_time - ttime >= 600:
                print_log('late (%d sec) to catch up, added postfix' % (cur_time - ttime))
                reply_postfix=' [Sorry for late reply, I am catching up]'
            reply(api, t.text, t.author.screen_name, t.id, reply_postfix=reply_postfix)
    except:
        pass
    try:
        my_name = api_stream.me().screen_name
        my_followers = api.followers_ids(api.me().id)
        my_friends = api.friends_ids(api.me().id)
    except tweepy.TweepError as e:
        print_log(str(e))
        continue
    for user_id in set(my_followers) - set(my_friends):
        try:
            api.create_friendship(user_id)
        except tweepy.TweepError as e:
            print_log(str(e))
            continue
    try:        
        timeline = api.home_timeline()
    except tweepy.TweepError as e:
        print_log(str(e))
        continue
        
    cur_time = int(time.time())
    print_log('got %d messages from timeline' % len(timeline))
    for status in timeline:
        text = status.text
        tid = status.id
        ttime = int(time.mktime(status.created_at.timetuple()))
        source_name = status.user.screen_name
        if status.user.screen_name == my_name:
            continue
        if status.user.id not in my_followers:
            continue
        if status.in_reply_to_status_id:
            continue
        if '@' in status.text:
            continue
        if status.retweeted:
            print_log("retweeted (%s, %s)" % status.text, status.user.screen_name)
            continue
        if tid in seen_tid:
#            print_log("already seen this message")
            continue
        seen_tid.add(tid)
        if cur_time - last_reply[source_name] < MENTION_INTERVAL:
            print_log("recently replied to this user %s: not responding" % status.user.screen_name)
            continue
        if cur_time - ttime >= 600:
            print_log("too old tweet (%d seconds ago, %s, %s): not responding" % (cur_time - ttime, status.text, status.user.screen_name))
            continue
        reply(api, text, source_name, tid)


