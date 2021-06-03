import tweepy

auth = tweepy.OAuthHandler('c7nf0odpA7Xmoq8eREdZFx5e1', 'zzy3k40GWtyPsq5kv2HV9RSx4s8449mB9YIVdnVM5CeRmGx3PQ')
auth.set_access_token('1337349594544369666-0LbUymtwlOeNwC4B9zVGfBgKJ7S8ws', '0TTb5uIZOvda6CEVt0XUM0wbovZ8GMm617cbn79QoIiuM')

api = tweepy.API(auth)
public_tweets = api.search_full_archive(environment_name='prod',query='"Proximal Algorithms"')
for tweet in public_tweets:
    print(tweet._json['id'])
