from bson.objectid import ObjectId
import datetime
from time import sleep
from j4hr.app import app, api_oauth, mongo
from j4hr.evetools import EveTools


def make_report(report_id):
    with app.app_context():
        report = original = mongo.db.reports.find_one({'_id': ObjectId(report_id)})
    # if report.get('generating', False) is True:
    #     raise Exception('Report #{report_id} already generating, aborting...'.format(report_id=report_id))

    try:
        if 'api' in report:
            report = application_report(report)
        else:
            report = auth_report(report)
    except Exception as e:
        app.logger.exception(e)
        report['errors'] = [e.message]

    report['generating'] = False
    report['finished_at'] = datetime.datetime.utcnow()

    with app.app_context():
        try:
            mongo.db.reports.save(report)
        except Exception as e:
            app.logger.exception(e)
            original['errors'] = [e.message]
            mongo.db.reports.save(original)


def application_report(report):
    """
    Report that use the api given during the application process
    """

    # Creating EveTools object
    eve = EveTools(key_id=report['api']['key_id'], vcode=report['api']['vcode'])

    # Resetting report
    report['characters'] = []
    report['errors'] = []

    # Let's start by checking the api key
    try:
        eve.check_key()
    except Exception as e:
        app.logger.exception(e)
        report['errors'].append(e.message)

    # Get full character info
    for eve_character in eve.get_characters():
        character = EveTools.auto_to_dict(eve_character)
        character['history'] = []
        for eve_corporation in eve_character.employmentHistory:
            corporation = EveTools.auto_to_dict(eve.safe_request('corp/CorporationSheet', True, {'corporationID': eve_corporation.corporationID}))
            sleep(0.5)
            character['history'].append({
                'corporation_id': corporation['corporationID'],
                'corporation_name': corporation['corporationName'],
                'ticker': 'BR',
                'alliance_id': corporation['allianceID'] if 'allianceID' in corporation else None,
                'alliance_name': corporation['allianceName'] if 'allianceName' in corporation else None,
                'start_date': datetime.datetime.utcfromtimestamp(eve_corporation.startDate)
            })

        # Contact list
        character['contacts'] = []
        contacts = eve.safe_request('char/ContactList', False, {'characterID': character['characterID']}).contactList
        for contact in contacts:
            if contact.contactID > 3020000:
                character['contacts'].append(EveTools.auto_to_dict(contact))

        # Standings
        standings = eve.safe_request('char/Standings', False, {'characterID': character['characterID']})
        character['standings'] = EveTools.auto_to_dict(standings.characterNPCStandings)

        # Wallet
        character['wallet'] = EveTools.auto_to_dict(eve.safe_request('char/WalletJournal', False, {'characterID': character['characterID'], 'rowCount': 2560}).transactions)

        # Assets time !
        assets = eve.safe_request('char/AssetList', False, {'characterID': character['characterID']}).assets
        character['assets'] = EveTools.parse_assets(EveTools.auto_to_dict(assets))

        report['characters'].append(character)

    return report


def auth_report(report):
    """
    Report that use the J4OAuth API to generate the report
    """

    eve = EveTools()

    # Resetting report
    report['characters'] = []
    report['errors'] = []
    # Get full character info
    auth_info = api_oauth.get('{base}user/{username}'.format(
        base=app.config['J4OAUTH']['base_url'],
        username=report['user_id']
    )).json()['user']
    if auth_info['auth_status'] != 'Internal':
        raise Exception('User {user} is not a current member of the alliance, aborting...'.format(user=report['user_id']))

    for eve_character in auth_info['characters']:
        character = api_oauth.get('{base}user/{username}/{character_id}/sheet'.format(
            base=app.config['J4OAUTH']['base_url'],
            username=report['user_id'],
            character_id=eve_character['character_id']
        )).json()['sheet']
        character['history'] = []
        for eve_corporation in character['employmentHistory']:
            corporation = EveTools.auto_to_dict(eve.safe_request('corp/CorporationSheet', True, {'corporationID': eve_corporation['corporationID']}))
            sleep(1)
            character['history'].append({
                'corporation_id': corporation['corporationID'],
                'corporation_name': corporation['corporationName'],
                'ticker': 'BR',
                'alliance_id': corporation['allianceID'] if 'allianceID' in corporation else None,
                'alliance_name': corporation['allianceName'] if 'allianceName' in corporation else None,
                'start_date': datetime.datetime.utcfromtimestamp(eve_corporation['startDate'])
            })

        # Contact list
        contacts = api_oauth.get('{base}user/{username}/{character_id}/contacts'.format(
            base=app.config['J4OAUTH']['base_url'],
            username=report['user_id'],
            character_id=character['characterID']
        )).json()['contacts']
        character['contacts'] = [contact for contact in contacts
                                 if contact['contactID'] > 3020000]

        # Standings
        character['standings'] = api_oauth.get('{base}user/{username}/{character_id}/standings'.format(
            base=app.config['J4OAUTH']['base_url'],
            username=report['user_id'],
            character_id=character['characterID']
        )).json()['standings']

        # Wallet
        character['wallet'] = api_oauth.get('{base}user/{username}/{character_id}/wallet'.format(
            base=app.config['J4OAUTH']['base_url'],
            username=report['user_id'],
            character_id=character['characterID']
        )).json()['wallet']

        # Assets time !
        assets = api_oauth.get('{base}user/{username}/{character_id}/assets'.format(
            base=app.config['J4OAUTH']['base_url'],
            username=report['user_id'],
            character_id=character['characterID']
        )).json()['assets']
        character['assets'] = EveTools.parse_assets(assets)

        report['characters'].append(character)

    return report
