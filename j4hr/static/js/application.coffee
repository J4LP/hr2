hrApp = angular.module('hrApp', ['ngRoute', 'ui.bootstrap'])

hrApp.config ($interpolateProvider) ->
    $interpolateProvider.startSymbol '{[{'
    $interpolateProvider.endSymbol '}]}'

hrApp.config ($httpProvider) ->
  $httpProvider.defaults.headers.post['X-CSRFToken'] = window.csrftoken

hrApp.constant 'config', {
    allianceID: window.allianceID
  }

hrApp.service 'ApplicationService', ->
  @keyID = 0
  @vCode = '0'
  @characterID = 0
  @characterName = ''
  @corporationID = 0
  @corporationName = ''
  return

hrApp.service 'AlertsService', ($timeout) ->
  @alerts = []
  @addAlert = (type, message) ->
    @alerts.push {
      type: type,
      msg: message
    }
    last = @alerts.length - 1
    $timeout () =>
      @alerts.splice(last, 1)
    , 3500
  @getAlerts = ->
    return @alerts
  return

hrApp.controller 'alertsCtrl', ($scope, AlertsService) ->
  $scope.alerts = AlertsService.getAlerts()
  $scope.closeAlert = (index) ->
    $scope.alerts.splice(index, 1)

hrApp.controller 'apiCtrl', ($http, $location, $scope, AlertsService, ApplicationService) ->
  $scope.checkApiKey = ->
    if $scope.apiForm.$valid
      $http {method: 'POST', url: 'api/check_key', data: {'key_id': $scope.key_id, 'vcode': $scope.vcode}}
        .success (data) ->
          if data.valid == true
            ApplicationService.keyID = $scope.key_id
            ApplicationService.vCode = $scope.vcode
            $location.path('/apply/characters')
        .error (data, status, headers) ->
          if headers()['content-type'].indexOf("text/html") != -1 and status == 500
            AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support')
          else
            AlertsService.addAlert('danger', data.error)


hrApp.controller 'charactersCtrl', ($location, $http, $scope, ApplicationService, AlertsService, config) ->
  $scope.characters = []
  $http {method: 'GET', url: "api/characters/#{ApplicationService.keyID}/#{ApplicationService.vCode}"}
    .success (data) ->
      # for character in data.characters
      #   if character.allianceID == config.allianceID
      #     $location.path('/denied')
      $scope.characters = data.characters
    .error (data, status, headers) ->
      if headers()['content-type'].indexOf("text/html") != -1 and status == 500
        AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support')
      else
        AlertsService.addAlert('danger', data.error)

  $scope.pick = (characterID) ->
    ApplicationService.characterID = characterID
    ApplicationService.characterName = character.characterName for character in $scope.characters when character.characterID == characterID
    $location.path('/apply/corporations')

hrApp.controller 'corporationsCtrl', ($location, $http, $scope, $window, ApplicationService, AlertsService) ->
  $scope.corporations = []
  $http {method: 'GET', url: 'api/corporations'}
    .success (data) ->
      $scope.corporations = data.corporations
    .error (data, status, headers) ->
      if headers()['content-type'].indexOf("text/html") != -1 and status == 500
        AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support')
      else
        AlertsService.addAlert('danger', data.error)
  $scope.pick = (corporationID) ->
    for _corporation in $scope.corporations
      if _corporation.id == corporationID
        corporation = _corporation
        break
    ApplicationService.corporationID = corporation.id
    ApplicationService.corporationName = corporation.name
    if corporation.reddit
      $window.location.href = $('base').attr('href') + 'reddit/go'
    else
      $location.path('/apply/recap')

hrApp.controller 'redditCtrl', ($location, ApplicationService, $routeParams) ->
  ApplicationService.redditKey = $routeParams.key
  ApplicationService.redditUsername = $routeParams.reddit_username
  $location.$$search = {};
  $location.path('/apply/recap')

hrApp.controller 'recapCtrl', ($http, $location, $scope, AlertsService, ApplicationService) ->
  $scope.app = ApplicationService
  $scope.motivation = ""
  $scope.apply = ->
    if $scope.motivation.length < 5
      AlertsService.addAlert('warning', 'Please write something as motivation for joining us !')
      return false
    data = {
      'key_id': ApplicationService.keyID,
      'vcode': ApplicationService.vCode,
      'character_id': ApplicationService.characterID,
      'character_name': ApplicationService.characterName,
      'corporation_id': ApplicationService.corporationID,
      'corporation_name': ApplicationService.corporationName,
      'motivation': $scope.motivation,
      'email': $scope.email
    }
    if ApplicationService.redditKey?
      data['reddit_key'] = ApplicationService.redditKey
      data['reddit_username'] = ApplicationService.redditUsername
    $http {method: 'POST', url: 'api/application', data}
    .success (data) ->
      if data.result == 'success'
        $location.path('/apply/done')
    .error (data, status, headers) ->
      if headers()['content-type'].indexOf("text/html") != -1 and status == 500
        AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support')
      else
        AlertsService.addAlert('danger', data.error)


hrApp.config ($routeProvider, $locationProvider) ->
  $routeProvider.when('/apply', {
    templateUrl: 'templates/angular/api_input.html'
    controller: 'apiCtrl'
  })
  $routeProvider.when('/apply/characters', {
    templateUrl: 'templates/angular/characters.html'
    controller: 'charactersCtrl'
  })
  $routeProvider.when('/apply/corporations', {
    templateUrl: 'templates/angular/corporations.html'
    controller: 'corporationsCtrl'
  })
  $routeProvider.when('/apply/denied', {
    templateUrl: 'templates/angular/denied.html'
  })
  $routeProvider.when('/apply/reddit', {
    templateUrl: 'templates/angular/denied.html'
    controller: 'redditCtrl'
  })
  $routeProvider.when('/apply/recap', {
    templateUrl: 'templates/angular/recap.html'
    controller: 'recapCtrl'
  })
  $routeProvider.when('/apply/done', {
    templateUrl: 'templates/angular/done.html'
  })
  $routeProvider.when('/apply/not_found', {
    templateUrl: 'templates/angular/not_found.html'
  })
  $routeProvider.otherwise({
    redirectTo: '/apply/not_found'
  })
  $locationProvider.html5Mode(true)
