'use strict';

angular.module('IpFeedbackReports', ['eums.config', 'ReportService', 'Loader'])
    .controller('IpFeedbackReportsController', function ($scope, $q, $location, ReportService, LoaderService) {

        loadIpFeedbackReport();

        $scope.$watch('searchTerm', function () {
            if ($scope.searchTerm && $scope.searchTerm.trim()) {
                loadIpFeedbackReport($scope.searchTerm)
            }
        });

        function loadIpFeedbackReport(filterParams) {
            LoaderService.showLoader();
            ReportService.ipFeedbackReport(filterParams)
                .then(function (response) {
                    $scope.report = response.results;
                    LoaderService.hideLoader();
                });
        }

    });