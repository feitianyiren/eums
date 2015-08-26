'use strict';

angular.module('IpFeedbackReport', ['eums.config', 'ReportService', 'Loader'])
    .controller('IpFeedbackReportController', function ($scope, $q, $location, ReportService, LoaderService) {

        loadIpFeedbackReport();

        $scope.$watch('searchTerm', function () {
            if ($scope.searchTerm && $scope.searchTerm.trim()) {
                loadIpFeedbackReport({query: $scope.searchTerm})
            }
        });

        $scope.goToPage = function (page) {
            loadIpFeedbackReport({page: page})
        };

        function loadIpFeedbackReport(filterParams) {
            LoaderService.showLoader();
            ReportService.ipFeedbackReport(filterParams)
                .then(function (response) {
                    $scope.report = response.results;
                    LoaderService.hideLoader();
                });
        }

    });