module.exports = (grunt) ->
  require("matchdep").filterDev("grunt-*").forEach(grunt.loadNpmTasks);
  grunt.initConfig
    pkg: '<json:package.json>'
    ngtemplates: {
      hrApp: {
        cwd: 'j4hr',
        src: 'templates/angular/**.html',
        dest: 'j4hr/static/js/templates.js'
      }
    }
    coffee: {
      compile: {
        files: {
          'j4hr/static/js/application.js': 'j4hr/static/js/application.coffee'
        }
      }
    }
    less: {
      prod: {
        files: {
          'j4hr/static/css/style.css': 'j4hr/static/css/style.less'
        }
      }
    }
    protractor: {
      options: {
        args: {
          framework: 'mocha'
          specs: ['tests/karma/*.js']
        }
      }
    }
    watch: {
      html: {
        files: ['j4hr/templates/angular/**.html'],
        tasks: ['ngtemplates'],
        options: {
          livereload: true,
        }
      },
      coffee: {
        files: ['j4hr/static/js/**.coffee', 'tests/protractor/**.coffee'],
        tasks: ['coffee'],
        options: {
          livereload: true,
        }
      }
      less: {
        files: ['j4hr/static/css/**.less'],
        tasks: ['less'],
        options: {
          livereload: true,
        }
      }
    }
  grunt.registerTask('default', ['less', 'ngtemplates', 'coffee'])
