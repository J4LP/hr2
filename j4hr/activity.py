import datetime
from enum import Enum
from j4hr.app import mongo


class Action(Enum):
    new_note = 'added a note to {applicant}\'s application'
    new_auth_note = 'added a note to {user_id}\'s profile'
    accepted_app = 'accepted {applicant}\'s application'
    rejected_app = 'rejected {applicant}\'s application'


class Activity(object):

    @classmethod
    def new(cls, author, action, save=False, **kwargs):
        activity = cls()
        activity.author_id = author['user_id']
        activity.author = author['main_character']
        activity.character_id = author['main_character_id']
        activity.action = action.value.format(**kwargs)
        activity.link = kwargs['link'] if 'link' in kwargs else '#'
        activity.created_at = datetime.datetime.now()
        if save:
            activity.save()
        return activity

    def save(self):
        self._id = mongo.db.activities.save(self.to_dict())

    def to_dict(self):
        return {
            'author_id': self.author_id,
            'author': self.author,
            'character_id': self.character_id,
            'action': self.action,
            'link': self.link,
            'created_at': self.created_at
        }
