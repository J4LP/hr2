import cPickle
import datetime
import eveapi
import json
import redis
import time
from j4hr.app import app, eve_db

r = redis.StrictRedis(host=app.config['REDIS'])


class EveException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RedisEveAPICacheHandler(object):

    def __init__(self, debug=False):
        self.debug = debug
        self.r = redis.StrictRedis(host=app.config['REDIS'])

    def log(self, what):
        if self.debug:
            print "[%s] %s" % (datetime.datetime.now().isoformat(), what)

    def retrieve(self, host, path, params):
        key = hash((host, path, frozenset(params.items())))

        cached = self.r.get(key)
        if cached is None:
            self.log("%s: not cached, fetching from server..." % path)
            return None
        else:
            cached = cPickle.loads(cached)
            if time.time() < cached[0]:
                self.log("%s: returning cached document" % path)
                return cached[1]
            self.log("%s: cache expired, purging !" % path)
            self.r.delete(key)

    def store(self, host, path, params, doc, obj):
        key = hash((host, path, frozenset(params.items())))

        cachedFor = (obj.cachedUntil - obj.currentTime) * 2
        if cachedFor:
            self.log("%s: cached (%d seconds)" % (path, cachedFor))

            cachedUntil = time.time() + cachedFor
            self.r.set(key, cPickle.dumps((cachedUntil, doc), -1))


def get_character_id(character_name=None):
    if character_name is None:
        raise Exception('No character name provided')
    character_id = r.get('eve:name_id:{}'.format(character_name))
    if character_id is None:
        client = eveapi.EVEAPIConnection(
            cacheHandler=RedisEveAPICacheHandler(debug=app.config['DEBUG']))
        character_id = client.eve.CharacterID(
            names=[character_name]).characters[0]['characterID']
        r.set('eve:name_id:{}'.format(character_name), character_id)
    return character_id


class EveTools(object):

    def __init__(self, key_id=None, vcode=None, cache=True):
        if cache:
            self.client = self.public_client = eveapi.EVEAPIConnection(
                cacheHandler=RedisEveAPICacheHandler(
                    debug=app.config['DEBUG']))
        else:
            self.client = self.public_client = eveapi.EVEAPIConnection()
        if key_id and vcode:
            self.auth(key_id, vcode)

    def auth(self, key_id, vcode):
        self.key_id = key_id
        self.vcode = vcode
        self.client = self.client.auth(keyID=key_id, vCode=vcode)
        self.authed = True

    def safe_request(self, request, public=False, kwargs=None):
        try:
            if public:
                req = getattr(self.public_client, request)
            else:
                req = getattr(self.client, request)
            if kwargs is not None:
                results = req(**kwargs)
            else:
                results = req()
        except eveapi.Error as e:
            app.logger.exception(e)
            raise EveException('API Error, {}'.format(e.message))
        except RuntimeError as e:
            app.logger.exception(e)
            raise EveException('CCP Server Error, {}'.format(e.message))
        except Exception as e:
            app.logger.exception(e)
            raise EveException('System error, our team has been notified !')
        return results

    def check_key(self):
        key_info = self.safe_request('account/APIKeyInfo')
        access_mask, key_type, expires = key_info.key.accessMask, key_info.key.type, key_info.key.expires
        if access_mask != 65544538:
            raise Exception('Invalid access mask, got: {}'.format(access_mask))
        if key_type not in ['Character', 'Account']:
            raise Exception('Invalid key type, got: {}'.format(key_type))
        if expires != "":
            raise Exception('Expiration detected on key, got: {}'.format(expires))
        return True

    def get_characters(self, public=False):
        key_info = self.safe_request('account/APIKeyInfo')
        characters = []
        for character in key_info.key.characters:
            characters.append(self.safe_request('eve/CharacterInfo', public, {'characterID': character['characterID']}))
        return characters

    @staticmethod
    def rowset_to_dict(rowset):
        """
        This method assume it receives a eveapi.Rowset or eveapi.IndexRowset
        and will convert it to a dict for easy serialization.
        """
        result = []
        for row in rowset:
            result.append(EveTools.row_to_dict(row))
        return result


    @staticmethod
    def row_to_dict(row):
        """
        This method assume it receives an eveapi.Row and will convert it
        to a dict for easy serialization.
        """
        result = {}
        for index, key in enumerate(row.__dict__['_cols']):
            if index < len(row.__dict__['_row']):
                if isinstance(row.__dict__['_row'][index], eveapi.IndexRowset):
                    result[key] = EveTools.rowset_to_dict(row.__dict__['_row'][index])
                else:
                    result[key] = row.__dict__['_row'][index]
        return result

    @staticmethod
    def element_to_dict(element):
        """
        This method assume it receives an eveapi.Element and will convert it to
        a dict for easy serialization.
        """
        result = {}
        for key, value in element.__dict__.iteritems():
            if isinstance(value, eveapi.Rowset) or isinstance(
                    value, eveapi.IndexRowset):
                result[key] = EveTools.rowset_to_dict(value)
            else:
                if key not in ('_meta', '_name', '_isrow'):
                    result[key] = value
        return result

    @staticmethod
    def auto_to_dict(resource):
        """
        Easy mode method to detect and convert to dict an eveapi.Resource
        """
        if isinstance(resource, eveapi.Element):
            return EveTools.element_to_dict(resource)
        elif isinstance(resource, eveapi.Row):
            return EveTools.row_to_dict(resource)
        elif isinstance(resource, eveapi.Rowset) \
                or isinstance(resource, eveapi.IndexRowset):
            return EveTools.rowset_to_dict(resource)
        else:
            return None

    @staticmethod
    def parse_assets(api_assets):
        """
        Recursive function to parse a list of assets
        """
        assets = []
        for asset in api_assets:
            item_type = EveTools.get_type_name(asset['typeID'])
            if 'locationID' in asset:
                asset['location_name'] = EveTools.get_location_name(asset['locationID'])
            asset['item_name'] = item_type['name']
            try:
                asset['base_price'] = item_type['base_price']
            except KeyError:
                asset['base_price'] = 0
            asset['group_name'] = item_type['group_name']
            assets.append(asset)
            if 'contents' in asset:
                assets += EveTools.parse_assets(asset['contents'])
        return assets

    @staticmethod
    def get_type_name(type_id):
        query = 'SELECT invTypes.typeID, invTypes.typeName, invTypes.basePrice, invGroups.groupName FROM invTypes JOIN invGroups ON invTypes.groupID=invGroups.groupID WHERE invTypes.typeID = :type_id'
        result = eve_db.engine.execute(query, type_id=type_id)
        item = {'type_id': None, 'name': None, 'group_name': None}
        for row in result:
            item['type_id'] = row[0]
            item['name'] = row[1]
            item['base_price'] = row[2]
            item['group_name'] = row[3]
            break
        return item

    @staticmethod
    def get_location_name(location_id):
        outposts = r.get('eve.stations')
        if outposts is None:
            outposts = []
        else:
            outposts = json.loads(outposts)
        location = None
        if 66000000 < location_id < 66014933:
            query = 'SELECT stationName FROM staStations WHERE stationID=:location_id;'
            result = eve_db.engine.execute(
                query, location_id=location_id - 6000001)
            for row in result:
                location = row[0]
                break
        if 66014934 < location_id < 67999999:
            location = outposts[str(location_id - 6000000)]
        if 60014861 < location_id < 60014928:
            location = outposts[str(location_id)]
        if 60000000 < location_id < 61000000:
            query = 'SELECT stationName FROM staStations WHERE stationID=:location_id;'
            result = eve_db.engine.execute(query, location_id=location_id)
            for row in result:
                location = row[0]
                break
        if location_id >= 61000000:
            location = outposts[str(location_id)]
        else:
            query = 'SELECT itemName FROM mapDenormalize WHERE itemID=:location_id;'
            result = eve_db.engine.execute(query, location_id=location_id)
            for row in result:
                location = row[0]
                break
        return location
