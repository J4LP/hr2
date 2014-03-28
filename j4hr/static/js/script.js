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
    this.keyID = 3092205;
    this.vCode = 'IL9c5vC4kDP1oWuwlSogYT3X5ZtFIvaXWy0wUu1kdPpXhtpQeyCTvvyby8ZSZaXy';
    this.characterID = 90721100;
    this.characterName = 'Vadrin Hegirin';
    this.corporationID = 98114328;
    this.corporationName = 'Fweddit';
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
    $scope.key_id = 3092205;
    $scope.vcode = 'IL9c5vC4kDP1oWuwlSogYT3X5ZtFIvaXWy0wUu1kdPpXhtpQeyCTvvyby8ZSZaXy';
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
            return $location.path('/characters');
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
      return $location.path('/corporations');
    };
  });

  hrApp.controller('corporationsCtrl', function($location, $http, $scope, ApplicationService, AlertsService) {
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
      var corporation, _i, _len, _ref;
      ApplicationService.corporationID = corporationID;
      _ref = $scope.corporations;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        corporation = _ref[_i];
        if (corporation.id === corporationID) {
          ApplicationService.corporationName = corporation.name;
        }
      }
      return $location.path('/recap');
    };
  });

  hrApp.controller('recapCtrl', function($http, $location, $scope, AlertsService, ApplicationService) {
    $scope.app = ApplicationService;
    $scope.motivation = "";
    return $scope.apply = function() {
      if ($scope.motivation.length < 5) {
        AlertsService.addAlert('warning', 'Please write something as motivation for joining us !');
        return false;
      }
      return $http({
        method: 'POST',
        url: 'api/application',
        data: {
          'key_id': ApplicationService.keyID,
          'vcode': ApplicationService.vCode,
          'character_id': ApplicationService.characterID,
          'character_name': ApplicationService.characterName,
          'corporation_id': ApplicationService.corporationID,
          'corporation_name': ApplicationService.corporationName,
          'motivation': $scope.motivation
        }
      }).success(function(data) {
        if (data.valid === true) {
          return $location.path('/done');
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
    $routeProvider.when('/', {
      templateUrl: 'templates/angular/home.html'
    });
    $routeProvider.when('/api', {
      templateUrl: 'templates/angular/api_input.html',
      controller: 'apiCtrl'
    });
    $routeProvider.when('/characters', {
      templateUrl: 'templates/angular/characters.html',
      controller: 'charactersCtrl'
    });
    $routeProvider.when('/corporations', {
      templateUrl: 'templates/angular/corporations.html',
      controller: 'corporationsCtrl'
    });
    $routeProvider.when('/denied', {
      templateUrl: 'templates/angular/denied.html'
    });
    $routeProvider.when('/recap', {
      templateUrl: 'templates/angular/recap.html',
      controller: 'recapCtrl'
    });
    $routeProvider.when('/not_found', {
      templateUrl: 'templates/angular/not_found.html'
    });
    $routeProvider.otherwise({
      redirectTo: '/not_found'
    });
    return $locationProvider.html5Mode(true);
  });

}).call(this);
