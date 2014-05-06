import datetime
from flask import Blueprint, jsonify, request
import redis
from werkzeug.datastructures import MultiDict
from j4hr.admin import Status
from j4hr.app import app, mongo
from j4hr.evetools import EveTools, EveException
from j4hr.forms import ApplicationForm

api = Blueprint('api', __name__)


@api.route('/check_key', methods=['POST'])
def check_key():
    """
    Check the API Key supplied
    """
    key_id, vcode = request.json['key_id'], request.json['vcode']
    try:
        key_id = int(key_id)
    except ValueError as e:
        return jsonify(error='Invalid Key ID'), 400
    if len(vcode) != 64:
        return jsonify(error='Invalid vCode'), 400
    eve = EveTools(key_id=key_id, vcode=vcode, cache=True)
    try:
        eve.check_key()
    except EveException as e:
        return jsonify(error=e.value), 500
    except Exception as e:
        return jsonify(error=e.message), 400
    return jsonify(valid=True)


@api.route('/characters/<int:key_id>/<vcode>', methods=['GET'])
def get_characters(key_id, vcode):
    """
    Return all the user's characters
    """
    if len(vcode) != 64:
        return jsonify(error='Invalid vCode'), 400
    eve = EveTools(key_id=key_id, vcode=vcode, cache=True)
    try:
        characters = eve.get_characters(public=True)
    except EveException as e:
        return jsonify(error=e.value), 500
    except Exception as e:
        return jsonify(error=e.message), 400
    return jsonify(
        characters=[EveTools.element_to_dict(character)
                    for character in characters])


@api.route('/corporations', methods=['GET'])
def get_corporations():
    """
    Return all active corporations and if they need reddit
    """
    corporations = mongo.db.corporations.find({'active': True})
    return jsonify(corporations=[{
        'id': corporation['corporation_id'],
        'name': corporation['name'],
        'reddit': corporation['reddit']
    } for corporation in corporations])


@api.route('/application', methods=['POST'])
def new_application():
    """
    Create the new application
    """
    form_data = request.get_json()
    application_form = ApplicationForm(MultiDict(form_data))
    if not application_form.validate():
        return jsonify(error='Validation error, '
                             'we could not validate your application.'), 400

    # Form is valid, let's check everything is valid
    eve = EveTools(key_id=application_form.key_id.data,
                   vcode=application_form.vcode.data, cache=True)
    try:
        eve.check_key()
        characters = eve.get_characters(public=True)
        for character in characters:
            if character.characterID == application_form.character_id.data:
                character_sheet = character
                break
        else:
            raise Exception('Character not found with provided API Key')
        corporation = mongo.db.corporations.find_one({'corporation_id': application_form.corporation_id.data})
        if corporation is None or corporation['active'] is False:
            raise Exception('You cannot apply to this corporation')
    except EveException as e:
        return jsonify(error=e.value), 500
    except Exception as e:
        app.logger.exception(e)
        return jsonify(error=e.message), 400

    # Do we have a reddit key ?
    if all(['reddit_key' in form_data, 'reddit_username' in form_data]):
        r = redis.StrictRedis(host=app.config['REDIS'])
        reddit_username = r.get('hr2:reddit:{}'.format(form_data['reddit_key']))
        if reddit_username != form_data['reddit_username']:
            return jsonify(error='Invalid Reddit token, '
                                 'maybe it has expired ?'), 403

    # Well, everything looks alright, let's create the application !
    user_id = application_form.character_name.data.replace(" ", "_").lower()
    application = {
        'applicant': {
            'user_id': user_id,
            'character_id': application_form.character_id.data,
            'character_name': application_form.character_name.data,
            'email': application_form.email.data,
            'key_id': application_form.key_id.data,
            'vcode': application_form.vcode.data,
            'reddit_username': form_data.get('reddit_username', None),
            'corporation_id': character_sheet.corporationID,
            'corporation_name': character_sheet.corporation,
            'alliance_id': character_sheet.__dict__.get('allianceID', None),
            'alliance_name': character_sheet.__dict__.get('alliance', None)
        },
        'corporation': {
            'corporation_id': application_form.corporation_id.data,
            'corporation_name': application_form.corporation_name.data
        },
        'motivation': application_form.motivation.data,
        'status': Status.Pending.value,
        'created_at': datetime.datetime.utcnow()
    }
    mongo.db.applications.insert(application)
    return jsonify(result='success'), 200
