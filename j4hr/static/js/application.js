(function() {
  var hrApp;

  hrApp = angular.module('hrApp', ['ngRoute', 'ui.bootstrap']);

  hrApp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    return $interpolateProvider.endSymbol('}]}');
  });

  hrApp.config(function($httpProvider) {
    return $httpProvider.defaults.headers.post['X-CSRFToken'] = window.csrftoken;
  });

  hrApp.constant('config', {
    allianceID: window.allianceID
  });

  hrApp.service('ApplicationService', function() {
    this.keyID = 0;
    this.vCode = '0';
    this.characterID = 0;
    this.characterName = '';
    this.corporationID = 0;
    this.corporationName = '';
  });

  hrApp.service('AlertsService', function($timeout) {
    this.alerts = [];
    this.addAlert = function(type, message) {
      var last;
      this.alerts.push({
        type: type,
        msg: message
      });
      last = this.alerts.length - 1;
      return $timeout((function(_this) {
        return function() {
          return _this.alerts.splice(last, 1);
        };
      })(this), 3500);
    };
    this.getAlerts = function() {
      return this.alerts;
    };
  });

  hrApp.controller('alertsCtrl', function($scope, AlertsService) {
    $scope.alerts = AlertsService.getAlerts();
    return $scope.closeAlert = function(index) {
      return $scope.alerts.splice(index, 1);
    };
  });

  hrApp.controller('apiCtrl', function($http, $location, $scope, AlertsService, ApplicationService) {
    return $scope.checkApiKey = function() {
      if ($scope.apiForm.$valid) {
        return $http({
          method: 'POST',
          url: 'api/check_key',
          data: {
            'key_id': $scope.key_id,
            'vcode': $scope.vcode
          }
        }).success(function(data) {
          if (data.valid === true) {
            ApplicationService.keyID = $scope.key_id;
            ApplicationService.vCode = $scope.vcode;
            return $location.path('/apply/characters');
          }
        }).error(function(data, status, headers) {
          if (headers()['content-type'].indexOf("text/html") !== -1 && status === 500) {
            return AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support');
          } else {
            return AlertsService.addAlert('danger', data.error);
          }
        });
      }
    };
  });

  hrApp.controller('charactersCtrl', function($location, $http, $scope, ApplicationService, AlertsService, config) {
    $scope.characters = [];
    $http({
      method: 'GET',
      url: "api/characters/" + ApplicationService.keyID + "/" + ApplicationService.vCode
    }).success(function(data) {
      return $scope.characters = data.characters;
    }).error(function(data, status, headers) {
      if (headers()['content-type'].indexOf("text/html") !== -1 && status === 500) {
        return AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support');
      } else {
        return AlertsService.addAlert('danger', data.error);
      }
    });
    return $scope.pick = function(characterID) {
      var character, _i, _len, _ref;
      ApplicationService.characterID = characterID;
      _ref = $scope.characters;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        character = _ref[_i];
        if (character.characterID === characterID) {
          ApplicationService.characterName = character.characterName;
        }
      }
      return $location.path('/apply/corporations');
    };
  });

  hrApp.controller('corporationsCtrl', function($location, $http, $scope, $window, ApplicationService, AlertsService) {
    $scope.corporations = [];
    $http({
      method: 'GET',
      url: 'api/corporations'
    }).success(function(data) {
      return $scope.corporations = data.corporations;
    }).error(function(data, status, headers) {
      if (headers()['content-type'].indexOf("text/html") !== -1 && status === 500) {
        return AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support');
      } else {
        return AlertsService.addAlert('danger', data.error);
      }
    });
    return $scope.pick = function(corporationID) {
      var corporation, _corporation, _i, _len, _ref;
      _ref = $scope.corporations;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        _corporation = _ref[_i];
        if (_corporation.id === corporationID) {
          corporation = _corporation;
          break;
        }
      }
      ApplicationService.corporationID = corporation.id;
      ApplicationService.corporationName = corporation.name;
      if (corporation.reddit) {
        return $window.location.href = $('base').attr('href') + 'reddit/go';
      } else {
        return $location.path('/apply/recap');
      }
    };
  });

  hrApp.controller('redditCtrl', function($location, ApplicationService, $routeParams) {
    ApplicationService.redditKey = $routeParams.key;
    ApplicationService.redditUsername = $routeParams.reddit_username;
    $location.$$search = {};
    return $location.path('/apply/recap');
  });

  hrApp.controller('recapCtrl', function($http, $location, $scope, AlertsService, ApplicationService) {
    $scope.app = ApplicationService;
    $scope.motivation = "";
    return $scope.apply = function() {
      var data;
      if ($scope.motivation.length < 5) {
        AlertsService.addAlert('warning', 'Please write something as motivation for joining us !');
        return false;
      }
      data = {
        'key_id': ApplicationService.keyID,
        'vcode': ApplicationService.vCode,
        'character_id': ApplicationService.characterID,
        'character_name': ApplicationService.characterName,
        'corporation_id': ApplicationService.corporationID,
        'corporation_name': ApplicationService.corporationName,
        'motivation': $scope.motivation,
        'email': $scope.email
      };
      if (ApplicationService.redditKey != null) {
        data['reddit_key'] = ApplicationService.redditKey;
        data['reddit_username'] = ApplicationService.redditUsername;
      }
      return $http({
        method: 'POST',
        url: 'api/application',
        data: data
      }).success(function(data) {
        if (data.result === 'success') {
          return $location.path('/apply/done');
        }
      }).error(function(data, status, headers) {
        if (headers()['content-type'].indexOf("text/html") !== -1 && status === 500) {
          return AlertsService.addAlert('danger', 'Internal Server Error. Please try again or contact our support');
        } else {
          return AlertsService.addAlert('danger', data.error);
        }
      });
    };
  });

  hrApp.config(function($routeProvider, $locationProvider) {
    $routeProvider.when('/apply', {
      templateUrl: 'templates/angular/api_input.html',
      controller: 'apiCtrl'
    });
    $routeProvider.when('/apply/characters', {
      templateUrl: 'templates/angular/characters.html',
      controller: 'charactersCtrl'
    });
    $routeProvider.when('/apply/corporations', {
      templateUrl: 'templates/angular/corporations.html',
      controller: 'corporationsCtrl'
    });
    $routeProvider.when('/apply/denied', {
      templateUrl: 'templates/angular/denied.html'
    });
    $routeProvider.when('/apply/reddit', {
      templateUrl: 'templates/angular/denied.html',
      controller: 'redditCtrl'
    });
    $routeProvider.when('/apply/recap', {
      templateUrl: 'templates/angular/recap.html',
      controller: 'recapCtrl'
    });
    $routeProvider.when('/apply/done', {
      templateUrl: 'templates/angular/done.html'
    });
    $routeProvider.when('/apply/not_found', {
      templateUrl: 'templates/angular/not_found.html'
    });
    $routeProvider.otherwise({
      redirectTo: '/apply/not_found'
    });
    return $locationProvider.html5Mode(true);
  });

}).call(this);
