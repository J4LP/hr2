import base64
import cPickle
from bson.objectid import ObjectId
from enum import Enum
from flask import abort, Blueprint, flash, redirect, render_template, request, session, url_for
import datetime
import pytz
from j4hr.activity import Action, Activity
from j4hr.app import app, hr_oauth, mongo, rQueue, api_oauth
from j4hr.report import make_report
from j4hr.utils import login_required

admin = Blueprint('admin', __name__, template_folder='templates/admin')


class Status(Enum):
    Pending = 1
    Accepted = 2
    Rejected = 3


@hr_oauth.tokengetter
def get_oauth_token(token=None):
    return session.get('j4oauth_token')


@admin.route('/')
@login_required
def index():
    pending_apps = mongo.db.applications.find({'status': Status.Pending.value})
    activities = mongo.db.activities.find()
    return render_template('index.html', pending_apps=pending_apps, activities=activities)


@admin.route('/application/<application_id>')
@login_required
def view_application(application_id):
    application = mongo.db.applications.find_one({'_id': ObjectId(application_id)})
    if application is None:
        abort(404)
    report = mongo.db.reports.find_one({'user_id': application['applicant']['user_id']})
    generated_time_limit = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(minutes=15)
    if report and report['started_at'] < generated_time_limit and report['generating'] is True:
        app.logger.info("Report for {} has been deleted because it exceeded its time limit.".format(application_id))
        mongo.db.reports.remove(report)
        report = None
    return render_template('view_application.html',
                           application=application,
                           Status=Status,
                           report=report)


@admin.route('/report/<report_id>')
@login_required
def view_report(report_id):
    report = mongo.db.reports.find_one({'_id': ObjectId(report_id)})
    if report is None:
        abort(404)
    return render_template('report.html', report=report)


@admin.route('/application/<application_id>/generate_report')
@admin.route('/users/<user_id>/generate_report', endpoint='generate_auth_report')
@login_required
def generate_application_report(application_id=None, user_id=None):
    if not user_id:
        application = mongo.db.applications.find_one({'_id': ObjectId(application_id)})
        if application is None:
            abort(404)
    report = mongo.db.reports.find_one({'user_id': user_id if user_id else application['applicant']['user_id']})
    if report is not None:
        if report.get('generating', False) is True:
            flash('Report is already generating', 'warning')
            if user_id:
                return redirect(url_for('.user_view', user_id=user_id))
            return redirect(url_for('.view_application', application_id=application_id))
        else:
            report['started_at'] = datetime.datetime.utcnow()
            report['generating'] = True
    else:
        if user_id:
            report = {
                'user_id': user_id,
                'started_at': datetime.datetime.utcnow(),
                'generating': True
            }
        else:
            report = {
                'user_id': application['applicant']['user_id'],
                'main_character': application['applicant']['character_name'],
                'started_at': datetime.datetime.utcnow(),
                'api': {
                    'key_id': application['applicant']['key_id'],
                    'vcode': application['applicant']['vcode'],
                },
                'generating': True
            }
    report_id = mongo.db.reports.save(report)
    rQueue.enqueue(make_report, str(report_id))
    flash('Report added to the queue, it will be generated soon !', 'success')
    if user_id:
        return redirect(url_for('.user_view', user_id=user_id))
    return redirect(url_for('.view_application', application_id=application_id))


@admin.route('/application/<application_id>/note', methods=['POST'])
@admin.route('/users/<user_id>/note', endpoint='add_note_auth', methods=['POST'])
@login_required
def add_note_application(application_id=None, user_id=None):
    if request.form.get('note', '') is '':
        flash('You can\'t add an empty note !', 'danger')
        if user_id:
            return redirect(url_for('.user_view', user_id=user_id))
        return redirect(url_for('.view_application', application_id=application_id))

    if user_id:
        user_notes = mongo.db.notes.find_one({'user_id': user_id})
        if user_notes is None:
            user_notes = {
                'user_id': user_id,
                'notes': []
            }
    else:
        application = mongo.db.applications.find_one({'_id': ObjectId(application_id)})
        if application is None:
            abort(404)

    note = {
        'by': session.get('current_user')['main_character'],
        'user_id': session.get('current_user')['user_id'],
        'note': request.form.get('note', 'Empty note'),
        'added_at': datetime.datetime.utcnow()
    }

    if user_id:
        user_notes['notes'].append(note)
        mongo.db.notes.save(user_notes)
        Activity.new(
            session.get('current_user'),
            Action.new_auth_note, save=True,
            link=url_for('.user_view', user_id=user_id),
            user_id=user_id)
    else:
        if 'notes' not in application:
            application['notes'] = [note]
        else:
            application['notes'].append(note)
        application['updated_at'] = datetime.datetime.utcnow()
        mongo.db.applications.save(application)
        Activity.new(
            session.get('current_user'),
            Action.new_note, save=True,
            link=url_for('.view_application', application_id=application_id),
            applicant=application['applicant']['character_name'])

    flash('Note added !', 'success')
    if user_id:
        return redirect(url_for('.user_view', user_id=user_id))
    return redirect(url_for('.view_application', application_id=application_id))


@admin.route('/application/<application_id>/accept', methods=['POST'])
@login_required
def accept_application(application_id):
    application = mongo.db.applications.find_one({'_id': ObjectId(application_id)})
    if application is None:
        abort(404)
    application['status'] = Status.Accepted.value
    application['decided_by'] = session.get('current_user')['main_character']
    application['updated_at'] = datetime.datetime.utcnow()
    Activity.new(
        session.get('current_user'),
        Action.accepted_app, save=True,
        applicant=application['applicant']['character_name'],
        link=url_for('.view_application', application_id=application_id)
    )
    mongo.db.applications.save(application)
    flash('Application accepted !', 'success')
    # TODO : Dispatch email
    return redirect(url_for('.view_application', application_id=application_id))


@admin.route('/application/<application_id>/reject', methods=['POST'])
@login_required
def reject_application(application_id):
    application = mongo.db.applications.find_one({'_id': ObjectId(application_id)})
    if application is None:
        abort(404)
    application['status'] = Status.Rejected.value
    application['decided_by'] = session.get('current_user')['main_character']
    application['reason'] = request.form.get('reason')
    application['updated_at'] = datetime.datetime.utcnow()
    Activity.new(
        session.get('current_user'),
        Action.rejected_app, save=True,
        applicant=application['applicant']['character_name'],
        link=url_for('.view_application', application_id=application_id)
    )
    flash('Application rejected !', 'success')
    mongo.db.applications.save(application)
    # TODO : Dispatch email
    return redirect(url_for('.view_application', application_id=application_id))


@admin.route('/users')
@login_required
def users():
    user = session.get('current_user')
    users = api_oauth.get('{}corporation/{}/users'.format(
                app.config['J4OAUTH']['base_url'],
                user['corporation']))
    return render_template('users.html', users=users.json()['users'])


@admin.route('/users/<user_id>')
@login_required
def user_view(user_id):
    current_user = session.get('current_user')
    user = api_oauth.get('{base}user/{user_id}'.format(
        base=app.config['J4OAUTH']['base_url'],
        user_id=user_id
    )).json()['user']
    if user['corporation'] != current_user['corporation'] or not session['admin']:
        flash('You are not authorized to view this user', 'danger')
        app.logger.error('Unauthorize access to {user}\'s profile by {by}'.format(
            user=user_id,
            by=current_user['user_id']
        ))
        return redirect('admin.index')
    report = mongo.db.reports.find_one({'user_id': user_id})
    generated_time_limit = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(minutes=15)
    if report and report['started_at'] < generated_time_limit and report['generating'] is True:
        mongo.db.reports.remove(report)
        app.logger.info("Report for {} has been deleted because it exceeded its time limit.".format(user_id))
        report = None
    user_notes = mongo.db.notes.find_one({'user_id': user_id})
    return render_template(
        'auth_user.html',
        user=user,
        report=report,
        user_notes=user_notes
    )


@admin.route('/login')
def login():
    state = {'next': request.args.get('next') or request.referrer or url_for('home', _external=True)}
    state = base64.b64encode(cPickle.dumps(state))
    return hr_oauth.authorize(
        callback=url_for('.authorize', _external=True),
        state=state,
        _external=True
    )


@admin.route('/authorize')
@hr_oauth.authorized_handler
def authorize(resp):
    try:
        state = base64.b64decode(request.args.get('state'))
        state = cPickle.loads(state)
    except cPickle.PickleError:
        state = {'next': url_for('home', _external=True)}
    if 'access_token' in resp:
        groups = hr_oauth.get('auth_groups', token=(resp['access_token'],)).data['groups']
        if not any([x in groups for x in app.config['HR_GROUPS']]):
            flash('You are not authorized to access this application.', 'danger')
            return redirect(url_for('home'))
        session['j4oauth_token'] = (resp['access_token'], '')
        session['current_user'] = hr_oauth.get('auth_user').data['user']
        session['admin'] = False
        if any([x in groups for x in app.config['ADMIN_GROUPS']]):
            session['admin'] = True
        flash('Welcome back {}!'.format(
            session['current_user']['main_character']), 'success')
        return redirect(state['next'] if 'next' in state else url_for('home'))
    else:
        flash('There was an error logging you in', 'danger')
        return redirect(url_for('home'))
