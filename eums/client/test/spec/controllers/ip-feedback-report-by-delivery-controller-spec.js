describe('IpFeedbackReportController', function () {
    var scope, location, mockReportService, deferredResult, mockLoader, timeout,
        route = {}, initController;

    beforeEach(function () {
        module('IpFeedbackReportByDelivery');

        mockReportService = jasmine.createSpyObj('mockReportService', ['ipFeedbackReportByDelivery']);
        mockLoader = jasmine.createSpyObj('mockLoader', ['showLoader', 'hideLoader', 'showModal']);

        inject(function ($controller, $q, $location, $rootScope, $timeout) {
            deferredResult = $q.defer();
            scope = $rootScope.$new();
            location = $location;
            timeout = $timeout;

            mockReportService.ipFeedbackReportByDelivery.and.returnValue(deferredResult.promise);

            initController = function(routeParams) {
                $controller('IpFeedbackReportByDeliveryController', {
                    $scope: scope,
                    $location: location,
                    $routeParams: routeParams,
                    ReportService: mockReportService,
                    LoaderService: mockLoader
                });
            };

            initController(route);
        });
    });

    describe('on load', function () {
        it('should show the loader and hide it after the loading data', function () {
            deferredResult.resolve([]);
            scope.$apply();

            expect(mockLoader.showLoader).toHaveBeenCalled();
            expect(mockLoader.showLoader.calls.count()).toEqual(1);

            expect(mockLoader.hideLoader).toHaveBeenCalled();
            expect(mockLoader.hideLoader.calls.count()).toEqual(1);
        });

        it('should call reports service', function () {
            var response = {results: [{id: 4}, {id: 24}]};
            deferredResult.resolve(response);
            scope.$apply();

            expect(mockReportService.ipFeedbackReportByDelivery).toHaveBeenCalled();
            expect(scope.report).toEqual(response.results)
        });

        it('should filter reports service by district if requested', function () {
            initController({district: 'Fort Portal'});
            var response = {results: [{id: 4}, {id: 24}]};
            deferredResult.resolve(response);
            scope.$apply();

            expect(mockReportService.ipFeedbackReportByDelivery).toHaveBeenCalledWith({location: 'Fort Portal'}, 1);
            expect(scope.report).toEqual(response.results)
        });

        it('should set district', function () {
            expect(scope.district).toEqual('All Districts');
            initController({district: 'Fort Portal'});
            expect(scope.district).toEqual('Fort Portal');
        });
    });

    describe('on paginate', function () {
        it('should call the service with page number', function () {
            deferredResult.resolve({});
            scope.$apply();

            scope.goToPage(2);
            scope.$digest();

            expect(mockReportService.ipFeedbackReportByDelivery).toHaveBeenCalledWith({}, 2);
            expect(mockReportService.ipFeedbackReportByDelivery.calls.count()).toEqual(2);
        });
    });

    describe('on filtering', function () {
        it('should call endpoint with query params after ', function () {
            deferredResult.resolve({results: []});
            scope.$apply();

            var searchTerm = 'something';
            scope.searchTerm = {query: searchTerm};
            scope.$apply();

            timeout.flush();
            expect(mockReportService.ipFeedbackReportByDelivery.calls.count()).toEqual(2);
            expect(mockReportService.ipFeedbackReportByDelivery).toHaveBeenCalledWith({query: searchTerm}, 1);
        });

        it('should call endpoint when searchTerm programme_id changes', function () {
            deferredResult.resolve({results: []});
            scope.$apply();

            var programme_id = 2;
            scope.searchTerm = {programme_id: programme_id};
            scope.$apply();

            timeout.flush();
            expect(mockReportService.ipFeedbackReportByDelivery.calls.count()).toEqual(2);
            expect(mockReportService.ipFeedbackReportByDelivery).toHaveBeenCalledWith({programme_id: programme_id}, 1);
        });

    });

    describe('on show remark', function(){
        it('should call show modal with right index', function(){
            scope.showRemarks(3);

            expect(mockLoader.showModal).toHaveBeenCalledWith('remarks-modal-3');
        })
    })

});
