(function() {
  var hrApp;

  hrApp = angular.module('hrApp', ['ngRoute', 'ui.bootstrap', 'LocalStorageModule']);

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

  hrApp.service('ApplicationService', function(localStorageService) {
    this.defaults = {
      'keyID': 0,
      'vCode': '',
      'characterID': 0,
      'characterName': '',
      'corporationID': 0,
      'corporationName': '',
      'redditKey': '',
      'redditUsername': ''
    };
    this.getInt = function(key) {
      return parseInt(localStorageService.get(key)) || this.defaults[key];
    };
    this.get = function(key) {
      return localStorageService.get(key) || this.defaults[key];
    };
    this.set = function(key, value) {
      return localStorageService.set(key, value);
    };
    this.reset = function() {
      var k, key, keys, _i, _len, _results;
      keys = [
        (function() {
          var _results;
          _results = [];
          for (k in this.defaults) {
            _results.push(k);
          }
          return _results;
        }).call(this)
      ][0];
      _results = [];
      for (_i = 0, _len = keys.length; _i < _len; _i++) {
        key = keys[_i];
        _results.push(localStorageService.remove(key, this.defaults[key]));
      }
      return _results;
    };
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
    console.log(ApplicationService.get('keyID'));
    ApplicationService.set('keyID', 5432);
    console.log(ApplicationService.getInt('keyID'));
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
            ApplicationService.set('keyID', $scope.key_id);
            ApplicationService.set('vCode', $scope.vcode);
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
      url: "api/characters/" + (ApplicationService.getInt('keyID')) + "/" + (ApplicationService.get('vCode'))
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
      var character, characterName, _i, _len, _ref;
      ApplicationService.set('characterID', characterID);
      _ref = $scope.characters;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        character = _ref[_i];
        if (character.characterID === characterID) {
          characterName = character.characterName;
        }
      }
      ApplicationService.set('characterName', characterName);
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
      ApplicationService.set('corporationID', corporation.id);
      ApplicationService.set('corporationName', corporation.name);
      if (corporation.reddit) {
        return $window.location.href = $('base').attr('href') + 'reddit/go';
      } else {
        return $location.path('/apply/recap');
      }
    };
  });

  hrApp.controller('redditCtrl', function($location, ApplicationService, $routeParams) {
    ApplicationService.set('redditKey', $routeParams.key);
    ApplicationService.set('redditUsername', $routeParams.reddit_username);
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
        'key_id': ApplicationService.getInt('keyID'),
        'vcode': ApplicationService.get('vCode'),
        'character_id': ApplicationService.getInt('characterID'),
        'character_name': ApplicationService.get('characterName'),
        'corporation_id': ApplicationService.getInt('corporationID'),
        'corporation_name': ApplicationService.get('corporationName'),
        'motivation': $scope.motivation,
        'email': $scope.email
      };
      if (ApplicationService.redditKey != null) {
        data['reddit_key'] = ApplicationService.get('redditKey');
        data['reddit_username'] = ApplicationService.get('redditUsername');
      }
      return $http({
        method: 'POST',
        url: 'api/application',
        data: data
      }).success(function(data) {
        if (data.result === 'success') {
          ApplicationService.reset();
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

  hrApp.controller('notFoundCtrl', function($location) {
    console.log('yo');
    return window.location.href = $('base').attr('href') + '/404';
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
    $routeProvider.when('/apply/reset', {
      controller: function($location, ApplicationService) {
        ApplicationService.reset();
        return $location.path('/apply');
      },
      template: '<div></div>'
    });
    $routeProvider.when('/apply/not_found', {
      controller: function() {
        return window.location.replace('/404');
      },
      template: '<div></div>'
    });
    $routeProvider.otherwise({
      controller: function() {
        return window.location.replace('/404');
      },
      template: '<div></div>'
    });
    return $locationProvider.html5Mode(true);
  });

}).call(this);
