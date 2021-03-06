'use strict';

angular.module('User', ['eums.config', 'NavigationTabs', 'EumsLogin'])
    .factory('UserService', function ($http, $q, EumsConfig) {
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
            },
            hasPermission: function (permissionToCheck, userPermissions) {
                var deferred = $q.defer();
                if (!permissionToCheck) {
                    deferred.resolve(false);
                    return deferred.promise;
                }

                if (userPermissions) {
                    deferred.resolve(_.contains(userPermissions, permissionToCheck));
                    return deferred.promise;
                } else {
                    return this.retrieveUserPermissions().then(function (permissions) {
                        return _.contains(permissions, permissionToCheck);
                    });
                }
            },
            retrieveUserPermissions: function () {
                return $http.get(EumsConfig.BACKEND_URLS.PERMISSION + '/all').then(function (result) {
                    return result.data;
                });
            },
            getUserById: function(userId) {
                return $http.get(EumsConfig.BACKEND_URLS.USER + userId).then(function (result) {
                   return result.data;
                });
            }
        };
    })
    .controller('CreateUserController', function ($scope) {

        groupRolesBootstrap();

        function hideElement(element) {
            $(element).hide();
        }

        function showElement(element) {
            $(element).show();
        }

        function resetElementValue(element) {
            $(element).val('');
        }

        function disableFields(selector) {
            $('body').find(selector).prop('disabled', true);
        }

        function enableFields(selector) {
            $('body').find(selector).prop('disabled', false);
        }

        function groupRolesBootstrap() {
            var $consignee = $('#id_consignee'),
                $consignee_parent = $consignee.parent().parent();

            hideElement($consignee_parent);

            $('select.select-roles').on('change', function () {
                var $selected_role = $.trim($(this).find('option:selected').text());
                if ($selected_role.indexOf("Implementing Partner") != -1) {
                    showElement($consignee_parent);
                    enableFields('#id_consignee');
                } else {
                    hideElement($consignee_parent);
                    disableFields('#id_consignee');
                    resetElementValue($consignee);
                }
            }).change();
        }
    });
