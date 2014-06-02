# -*- coding: utf-8 -*-

import arrow
from flask import render_template, session, redirect, url_for
from jinja2 import Markup
from j4hr.admin import admin
from j4hr.api import api
from j4hr.app import app

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api')

if app.config['REDDIT']['ENABLED']:
    from reddit import reddit
    app.register_blueprint(reddit, url_prefix='/reddit')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/apply', defaults={'path': ''})
@app.route('/apply/<path:path>')
def apply(path):
    return render_template('apply.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.context_processor
def inject_icon():
    """
    Handy template method for quick icons
    """
    def icon(icon_name):
        return Markup('<i class="fa fa-{icon}"></i>'.format(icon=icon_name))
    return dict(icon=icon)


@app.template_filter('humanize')
def humanize_filter(datetime):
    """
    Use arrow to humanize a date, ex: 2 minutes ago
    """
    return arrow.get(datetime).humanize()


@app.template_filter('date')
def date_filter(datetime):
    """
    Use arrow to format properly a date
    """
    return arrow.get(datetime).format('DD MMMM YYYY')


@app.template_filter('datetime')
def datetime_filter(datetime):
    """
    Use arrow to format properly a date
    """
    return arrow.get(datetime).format('DD MMMM YYYY - H:mm UTC')


@app.template_filter('timestamp')
def timestamp_filter(datetime):
    """
    Use arrow to format properly a date
    """
    return arrow.get(datetime).format('X')


@app.context_processor
def inject_globals():
    return dict(
        APPLICATION_ROOT=app.config['APPLICATION_ROOT'],
        ALLIANCE_ID=app.config['EVE']['ALLIANCE_ID']
    )
