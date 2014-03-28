#!/usr/bin/env python
import datetime
import json
import logging
import redis
import sys
import os
import subprocess
from flask.ext.assets import ManageAssets
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager, Shell, Server
from webassets.script import CommandLineEnvironment
from j4hr.app import assets_env, mongo
from j4hr.evetools import EveTools
from j4hr.main import app

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets_env))


def _make_context():
    '''Return context dict for a shell session so you can access
    app, db, and models by default.
    '''
    return {'app': app}


@manager.command
def update_corporations():
    """Update corporations from alliance list."""
    corporations = []
    api = EveTools(app.config['EVE']['ALLIANCE_KEY_ID'],
                   app.config['EVE']['ALLIANCE_KEY_VCODE'], cache=True)
    app.logger.info('Starting updating of alliance\'s corporations')
    alliances = api.client.eve.AllianceList().alliances
    # Looking for our alliance
    for api_alliance in alliances:
        if api_alliance.allianceID == app.config['EVE']['ALLIANCE_ID']:
            alliance = api_alliance
            break
    else:
        raise Exception('Alliance not found')
    app.logger.info(
        'Alliance "{alliance}" found, updating corporations"'.format(
            alliance=alliance.name))
    for member_corporation in alliance.memberCorporations:
        corporation_sheet = api.client.corp.CorporationSheet(
            corporationID=member_corporation.corporationID)
        corporation = dict(
            corporation_id=corporation_sheet.corporationID,
            name=corporation_sheet.corporationName,
            ticker=corporation_sheet.ticker,
            members=corporation_sheet.memberCount,
            reddit=False,
            active=True)
        if member_corporation.corporationID in app.config['EVE'][
            'DISABLED_CORPORATIONS']:
            corporation['active'] = False
        if app.config['REDDIT']['ENABLED']:
            if member_corporation.corporationID in app.config['REDDIT']['CORPORATIONS']:
                corporation['reddit'] = True
        app.logger.info('Adding {}'.format(corporation['name']))
        corporations.append(corporation)
    with app.app_context():
        mongo.db.corporations.update({}, {'$set': {'active': False}}, multi=True)
        for corporation in corporations:
            mongo.db.corporations.update({'corporation_id': corporation['corporation_id']}, corporation, upsert=True)
    app.logger.info('Corporations updated with success !')

@manager.command
def update_outposts():
    '''Update Conquerable stations amd Outposts from Eve API'''
    api = EveTools()
    api_stations = api.client.eve.ConquerableStationList()
    stations = {}
    for station in api_stations.outposts:
        stations[str(station.stationID)] = station.stationName + \
            ' (%s)' % station.corporationName
    r = redis.StrictRedis(host=app.config['REDIS'])
    r.set('eve.stations', json.dumps(stations))


@manager.command
def clean_activities():
    with app.app_context():
        until = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        mongo.db.activities.remove({'created_at': {'$lt': until}})
    app.logger.info('Activities cleaned !')



manager.add_command("runserver",
                    Server(host='0.0.0.0', port=os.getenv('PORT', 5000),
                           debug=True))
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
