'use strict';

angular.module('User', ['eums.config']).factory('UserService', function ($http, $q) {
    var currentUser;
    return {
        getCurrentUser: function () {
            if (!currentUser) {
                return $http.get('/api/current-user/').then(function (response) {
                    currentUser = response.data;
                    return currentUser;
                });
            }
            var deferred = $q.defer();
            deferred.resolve(currentUser);
            return deferred.promise;
        },
        checkUserPermission: function (permission) {
            return $http.get('/api/permission?permission=' + permission).then(function () {
                return true;
            }).catch(function () {
                return false;
            });
        }
    };
});