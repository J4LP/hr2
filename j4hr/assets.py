# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle

common_css = Bundle(
    "../bower_components/bootstrap/dist/css/bootstrap.min.css",
    "../bower_components/animate.css/animate.min.css",
    "css/style.css",
    filters="cssmin",
    output="public/css/common.css"
)

application_js = Bundle(
    "../bower_components/jquery/jquery.min.js",
    "../bower_components/angular/angular.js",
    "../bower_components/angular-route/angular-route.js",
    "../bower_components/angular-bootstrap/ui-bootstrap.js",
    "../bower_components/angular-bootstrap/ui-bootstrap-tpls.js",
    "../bower_components/bootstrap/dist/js/bootstrap.min.js",
    Bundle(
        "js/application.js",
        "js/templates.js",
        #filters="jsmin"
    ),
    output="public/js/application.js"
)

home_js = Bundle(
    "../bower_components/jquery/jquery.min.js",
    "../bower_components/angular/angular.js",
    "../bower_components/bootstrap/dist/js/bootstrap.min.js",
    output="public/js/home.js"
)

admin_js = Bundle(
    "../bower_components/jquery/jquery.min.js",
    "../bower_components/angular/angular.js",
    "../bower_components/bootstrap/dist/js/bootstrap.min.js",
    "../bower_components/datatables/media/js/jquery.dataTables.js",
    "../bower_components/datatables-bootstrap3/BS3/assets/js/datatables.js",
    "../bower_components/bootbox/bootbox.js",
    output="public/js/admin.js"
)

admin_css = Bundle(
    "../bower_components/datatables-bootstrap3/BS3/assets/css/datatables.css",
    filters="cssmin",
    output="public/css/admin.css"
)
