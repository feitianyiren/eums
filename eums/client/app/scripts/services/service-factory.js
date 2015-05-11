'use strict';

angular.module('GenericService', []).factory('ServiceFactory', function ($http, $q) {
    var buildObject = function (object, buildMap) {
        var buildOutPromises = [];
        Object.each(buildMap, function (property, service) {
            buildOutPromises.push(service.get(object[property]))
        });
        return $q.all(buildOutPromises).then(function (builtObjects) {
            builtObjects.each(function (builtObject, index) {
                object[Object.keys(buildMap)[index]] = builtObject;
            });
            return object;
        });
    };

    var nestedObjectsToIds = function(object) {
        var objectToFlatten = Object.clone(object);
        return Object.map(objectToFlatten, function(key, value, original) {
            if (typeof value === 'object' && value.id) {
                original[key] = value.id;
            }
            return original[key];
        });
    };

    return function (options) {
        return {
            all: function (nestedBuildParams) {
                !nestedBuildParams && (nestedBuildParams = {});
                return $http.get(options.uri).then(function (response) {
                    var buildPromises = response.data.map(function (flatObject) {
                        return buildObject(flatObject, nestedBuildParams);
                    });
                    return $q.all(buildPromises).then(function (builtObjects) {
                        return builtObjects.map(function (object) {
                            return object;
                        });
                    });
                });
            },
            get: function (id, nestedBuildParams) {
                !nestedBuildParams && (nestedBuildParams = {});
                return $http.get('{1}{2}/'.assign(options.uri, id)).then(function (response) {
                    return buildObject(response.data, nestedBuildParams).then(function (builtObject) {
                        return builtObject;
                    });
                });
            },
            create: function (object) {
                return $http.post(options.uri, object).then(function (response) {
                    return response.data;
                });
            },
            update: function (object) {
                var flatObject = nestedObjectsToIds(object);
                return $http.put('{1}{2}/'.assign(options.uri, object.id), flatObject).then(function (response) {
                    return response.status;
                });
            },
            del: function (object) {
                return $http.delete('{1}{2}/'.assign(options.uri, object.id), object).then(function (response) {
                    return response.status;
                });
            }
        };
    };
});

