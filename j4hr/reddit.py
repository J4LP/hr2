import random
from flask import abort, Blueprint, redirect, request, url_for
import praw
import redis
from app import app


reddit = Blueprint('reddit', __name__)

@reddit.route('/go')
def go_reddit():
    reddit_client = praw.Reddit('J4LP HR2 reddit verification at j4lp.com')
    reddit_client.set_oauth_app_info(
        client_id=app.config['REDDIT']['CLIENT_ID'],
        client_secret=app.config['REDDIT']['CLIENT_SECRET'],
        redirect_uri=app.config['REDDIT']['REDIRECT_URI'])
    url = reddit_client.get_authorize_url(app.config['REDDIT']['STATE'],
                                          'identity', False)
    return redirect(url)


@reddit.route('/authorize')
def authorize():
    reddit_client = praw.Reddit('J4LP HR2 reddit verification at j4lp.com')
    reddit_client.set_oauth_app_info(
        client_id=app.config['REDDIT']['CLIENT_ID'],
        client_secret=app.config['REDDIT']['CLIENT_SECRET'],
        redirect_uri=app.config['REDDIT']['REDIRECT_URI'])
    if request.args.get('state', '') != app.config['REDDIT']['STATE']:
        abort(403)
    access = reddit_client.get_access_information(request.args.get('code', ''))
    reddit_client.set_access_credentials(**access)
    reddit_user = reddit_client.get_me()
    reddit_key = "%032x" % random.getrandbits(128)
    r = redis.StrictRedis(host=app.config['REDIS'])
    r.set('hr2:reddit:{}'.format(reddit_key), reddit_user.name)
    #r.expire('hr2:reddit:{}'.format(reddit_key), 60 * 10)
    return redirect(url_for('apply') + '/reddit?key={}&reddit_username={}'.format(reddit_key, reddit_user.name))


