'use strict';

describe('New IP Delivery Controller', function () {
    var mockIpService, location, scope, q, mockDeliveryService, mockDeliveryNodeService, routeParams, timeout, mockDeliveryNode,
        mockLoaderService, mockItemService, mockConsigneeItemService, mockSystemSettingsService, mockUserService;
    var ipNodes, toast, initController, deliveryGroups,
        userGetCurrentUserPromise, userHasPermissionToPromise, deferredPermissionsResultsPromise;
    var districts = ['Kampala', 'Mukono'];
    var orderItemId = 1890;
    var fetchedItem = {id: 1, description: 'Some name', unit: 1};
    var fetchedConsigneeItems = {results: [{id: 2, availableBalance: 450}]};
    var distributionPlan = {id: 1, programme: "Some programme"};
    var createdDistributionPlan = {id: 2, programme: "Some programme"};
    var stubSystemSettings = {
        "id": 1,
        "auto_track": false,
        "sync_start_date": null,
        "sync_end_date": null,
        'notification_message': 'notification',
        "district_label": "District"
    };
    var stubCurrentIpUser = {
        "username": "wakiso",
        "first_name": "",
        "last_name": "",
        "userid": 2,
        "consignee_id": 1,
        "email": "ip@ip.com"
    };

    beforeEach(function () {
        module('NewDeliveryByIp');

        mockDeliveryNode = function (options) {
            Object.defineProperty(this, 'isEndUser', {
                get: function () {
                    return this.treePosition === 'END_USER';
                }.bind(this)
            });
            this.track = options.track;
            this.treePosition = options.treePosition;
        };
        ipNodes = [
            {id: 1, item: orderItemId, orderNumber: '12345678', quantityShipped: 10, balance: 10},
            {id: 2, item: orderItemId, orderNumber: '12345678', quantityShipped: 20, balance: 20},
            {id: 3, item: orderItemId, orderNumber: '12345678', quantityShipped: 30, balance: 30},
            {id: 4, item: orderItemId, orderNumber: '12345678', quantityShipped: 40, balance: 40},
            {id: 1, item: orderItemId, orderNumber: '98765432', quantityShipped: 10, balance: 10},
            {id: 2, item: orderItemId, orderNumber: '98765432', quantityShipped: 20, balance: 20}
        ];
        deliveryGroups = [
            {
                orderNumber: '12345678', totalQuantity: 100, numberOfShipments: 4, isOpen: function () {
            }
            },
            {
                orderNumber: '98765432', totalQuantity: 30, numberOfShipments: 2, isOpen: function () {
            }
            }
        ];

        mockIpService = jasmine.createSpyObj('mockIpService', ['loadAllDistricts']);
        mockDeliveryService = jasmine.createSpyObj('mockDeliveryService', ['get', 'create']);
        mockDeliveryNodeService = jasmine.createSpyObj('mockDeliveryNodeService', ['filter', 'create']);
        mockLoaderService = jasmine.createSpyObj('mockLoaderService', ['showLoader', 'hideLoader', 'showModal']);
        mockItemService = jasmine.createSpyObj('ItemService', ['get']);
        mockConsigneeItemService = jasmine.createSpyObj('ConsigneeItemService', ['filter']);
        mockUserService = jasmine.createSpyObj('mockUserService', ['getCurrentUser', 'hasPermission', 'retrieveUserPermissions'])
        mockSystemSettingsService = jasmine.createSpyObj('mockSystemSettingsService', ['getSettings', 'getSettingsWithDefault']);

        inject(function ($controller, $rootScope, $q, $location, ngToast, $timeout) {
            scope = $rootScope.$new();
            timeout = $timeout;
            location = $location;
            toast = ngToast;
            q = $q;
            routeParams = {itemId: 2};

            userGetCurrentUserPromise = $q.defer();
            userHasPermissionToPromise = $q.defer();
            deferredPermissionsResultsPromise = $q.defer();
            mockConsigneeItemService.filter.and.returnValue($q.when(fetchedConsigneeItems));
            mockIpService.loadAllDistricts.and.returnValue($q.when({data: districts}));
            mockDeliveryService.get.and.returnValue($q.when(distributionPlan));
            mockDeliveryService.create.and.returnValue($q.when(createdDistributionPlan));
            mockDeliveryNodeService.filter.and.returnValue($q.when(ipNodes));
            mockDeliveryNodeService.create.and.returnValue($q.when({}));
            mockItemService.get.and.returnValue($q.when(fetchedItem));
            mockSystemSettingsService.getSettings.and.returnValue(q.when(stubSystemSettings));
            mockSystemSettingsService.getSettingsWithDefault.and.returnValue(q.when(stubSystemSettings));
            mockUserService.getCurrentUser.and.returnValue(userGetCurrentUserPromise.promise);
            mockUserService.hasPermission.and.returnValue(userHasPermissionToPromise.promise);
            mockUserService.retrieveUserPermissions.and.returnValue(deferredPermissionsResultsPromise.promise);

            spyOn($location, 'path');
            spyOn(toast, 'create');

            initController = function (theRoutsParams) {
                $controller('NewDeliveryByIpController', {
                    $scope: scope,
                    $timeout: timeout,
                    $routeParams: theRoutsParams,
                    $location: location,
                    ngToast: toast,
                    IPService: mockIpService,
                    DeliveryService: mockDeliveryService,
                    DeliveryNodeService: mockDeliveryNodeService,
                    DeliveryNode: mockDeliveryNode,
                    ItemService: mockItemService,
                    ConsigneeItemService: mockConsigneeItemService,
                    SystemSettingsService: mockSystemSettingsService,
                    UserService: mockUserService,
                    LoaderService: mockLoaderService
                });
            };
            initController(routeParams);
        });
    });

    describe('On assigning items to other ips', function () {
        beforeEach(function () {
            var toOthersRouteParams = {itemId: 2};
            initController(toOthersRouteParams);
        });

        it('should show loader on load', function () {
            scope.$apply();
            expect(mockLoaderService.showLoader).toHaveBeenCalled();
            expect(mockLoaderService.hideLoader).toHaveBeenCalled();
        });

        it('should have empty initial data on load', function () {
            expect(scope.errors).toBe(false);
            expect(scope.districts).toEqual([]);
            expect(JSON.stringify(scope.newDelivery)).toEqual(JSON.stringify({track: true, treePosition: 'END_USER'}));
            expect(JSON.stringify(scope.newDelivery.isEndUser)).toBeTruthy();
        });

        it('should load all districts and put them on scope', function () {
            expect(scope.districtsLoaded).toBeFalsy();
            scope.$apply();
            expect(scope.districts).toEqual([{id: 'Kampala', name: 'Kampala'}, {id: 'Mukono', name: 'Mukono'}]);
            expect(scope.districtsLoaded).toBeTruthy();
        });

        it('should load deliveries made to IP for the item', function () {
            scope.$apply();
            var filterParams = {item__item: routeParams.itemId, is_distributable: true};
            expect(mockDeliveryNodeService.filter).toHaveBeenCalledWith(filterParams);
            expect(scope.allDeliveries).toEqual(ipNodes);
            expect(scope.deliveryGroups.count()).toBe(2);
            expect(scope.deliveryGroups.first().orderNumber).toEqual('12345678');
            expect(scope.deliveryGroups[1].orderNumber).toEqual('98765432');
            expect(scope.deliveryGroups.first().totalQuantity).toBe(100);
            expect(scope.deliveryGroups.first().numberOfShipments).toBe(4);
        });

        it('should load list of POs or Waybills for which deliveries have been made', function () {
            scope.$apply();
            expect(scope.deliveryGroups.first().orderNumber).toEqual('12345678');
            expect(scope.deliveryGroups[1].orderNumber).toEqual('98765432');
            expect(scope.deliveryGroups.first().totalQuantity).toBe(100);
            expect(scope.deliveryGroups.first().numberOfShipments).toBe(4);
        });

        it('should select deliveries for the first PO or Waybill', function () {
            scope.$apply();
            var selectedDeliveries = [
                {id: 1, item: orderItemId, orderNumber: '12345678', quantityShipped: 10, balance: 10},
                {id: 2, item: orderItemId, orderNumber: '12345678', quantityShipped: 20, balance: 20},
                {id: 3, item: orderItemId, orderNumber: '12345678', quantityShipped: 30, balance: 30},
                {id: 4, item: orderItemId, orderNumber: '12345678', quantityShipped: 40, balance: 40}
            ];

            expect(scope.selectedDeliveries).toEqual(selectedDeliveries);
        });

        it('should change selected deliveries when selected order number is changed', function () {
            scope.$apply();
            scope.selectedOrderNumber = '98765432';
            scope.$apply();
            var selectedDeliveries = [
                {id: 1, item: orderItemId, orderNumber: '98765432', quantityShipped: 10, balance: 10},
                {id: 2, item: orderItemId, orderNumber: '98765432', quantityShipped: 20, balance: 20}
            ];
            expect(scope.selectedDeliveries).toEqual(selectedDeliveries);
        });

        it('it should open delivery group when order number is the selected order number', function () {
            scope.$apply();
            scope.selectedOrderNumber = '98765432';
            scope.$apply();
            expect(scope.deliveryGroups.first().isOpen()).toBeFalsy();
            expect(scope.deliveryGroups[1].isOpen()).toBeTruthy();
        });

        it('it should change selected order number and selected deliveries', function () {
            scope.$apply();
            var orderNumber = '98765432';
            scope.updateSelectedOrderNumber(orderNumber);
            scope.$apply();
            expect(scope.selectedOrderNumber).toEqual(orderNumber);
        });

        it('it should have no selected order number and deliveries, if updated/clicked twice', function () {
            scope.$apply();
            var orderNumber = '98765432';
            scope.updateSelectedOrderNumber(orderNumber);
            scope.$apply();
            scope.updateSelectedOrderNumber(orderNumber);
            scope.$apply();
            expect(scope.selectedOrderNumber).toBe(undefined);
            expect(scope.deliveryGroups.first().isOpen()).toBeFalsy();
            expect(scope.deliveryGroups[1].isOpen()).toBeFalsy();
        });

        it('should fetch item details and put them on scope', function () {
            scope.$apply();
            expect(scope.item).toEqual(fetchedItem);
        });

        it('should fetch consignee item details on load', function () {
            scope.$apply();
            expect(mockConsigneeItemService.filter).toHaveBeenCalledWith({item: 2});
            expect(scope.quantityAvailable).toBe(450);
        });

        it('should broadcast add contact event when addContact is called', function () {
            spyOn(scope, '$broadcast');
            scope.addContact();
            expect(scope.$broadcast).toHaveBeenCalledWith('add-contact');
        });

        it('should put new contact on scope after save', function () {
            var contact = {_id: 1, firstName: 'James', lastName: 'Bean'};

            var contactScope = scope.$new();
            contactScope.$emit('contact-saved', contact);
            scope.$apply();

            expect(scope.newDelivery.contact_person_id).toBe(contact._id);
            expect(scope.newDelivery.contact).toEqual(contact);
        });

        it('should put contact name into select after contact-saved is called', function () {
            var fakeTextSetter = jasmine.createSpy();
            var fakeContactInput = {
                siblings: function () {
                    return {
                        find: function () {
                            return {text: fakeTextSetter}
                        }
                    }
                }
            };
            spyOn(angular, 'element').and.returnValue(fakeContactInput);

            var contact = {_id: 1, firstName: 'James', lastName: 'Bean'};
            var contactScope = scope.$new();
            contactScope.$emit('contact-saved', contact);
            scope.$apply();

            expect(fakeTextSetter).toHaveBeenCalledWith('James Bean');
        });

        it('should broadcast add consignee event when addConsignee is called', function () {
            spyOn(scope, '$broadcast');
            scope.addConsignee();
            expect(scope.$broadcast).toHaveBeenCalledWith('add-consignee');
        });

        it('should put new consignee on scope after save', function () {
            var consignee = {id: 1, name: 'Wakiso DHO', location: 'Wakiso'};

            var consigneeScope = scope.$new();
            consigneeScope.$emit('consignee-saved', consignee);
            scope.$apply();

            expect(scope.newDelivery.consignee).toEqual(consignee);
        });

        it('should compute new delivery quantity from individual deliveries quantityShipped', function () {
            scope.$apply();
            expect(scope.totalQuantityShipped).toBe(100);
            scope.selectedDeliveries.first().quantityShipped = 100;
            scope.$apply();
            expect(scope.totalQuantityShipped).toBe(190);

            scope.selectedDeliveries.last().quantityShipped = 500;
            scope.$apply();
            expect(scope.totalQuantityShipped).toBe(650);
        });

        it('should put consignee name into select after consignee-saved is called', function () {
            var consignee = {id: 1, name: 'Wakiso DHO', location: 'Wakiso'};
            spyOn(scope, '$broadcast');
            var consigneeScope = scope.$new();
            consigneeScope.$emit('consignee-saved', consignee);
            scope.$apply();

            expect(scope.$broadcast).toHaveBeenCalledWith('set-consignee', consignee);
        });

        it('should save new delivery using only parent nodes with non-zero quantities', function () {
            scope.$apply();
            var newDelivery = setupNewDelivery();
            scope.deliveries = [
                {id: 1, item: orderItemId, quantityShipped: 10, distributionPlan: 1},
                {id: 2, item: orderItemId, quantityShipped: 0, distributionPlan: 2},
                {id: 3, item: orderItemId, quantityShipped: 40, distributionPlan: 3}
            ];

            scope.save();
            scope.$apply();

            var createArgs = mockDeliveryNodeService.create.calls.allArgs().first().first();
            var additionalFields = {track: true, item: 1890, parents: [{id: 1, quantity: 10}, {id: 3, quantity: 40}]};
            var expectedArgs = Object.merge(newDelivery, additionalFields);
            expect(JSON.stringify(createArgs)).toEqual(JSON.stringify(expectedArgs));
        });

        it('should not save delivery when any required field on the new delivery is not provided', function () {
            scope.$apply();
            assertSaveFails.if('location').is(undefined);
            assertSaveFails.if('consignee').is(undefined);
            assertSaveFails.if('deliveryDate').is(undefined);
            assertSaveFails.if('contact_person_id').is(undefined);
        });

        it('should not save new delivery if all deliveries to IP have no or zero quantity shipped', function () {
            scope.$apply();
            setupNewDelivery();
            scope.selectedDeliveries = [{id: 1, item: orderItemId}, {id: 2, item: orderItemId, quantityShipped: 0}];
            scope.save();
            expect(mockDeliveryNodeService.create).not.toHaveBeenCalled();
        });

        it('should not save new delivery if any of the deliveries has a quantity shipped higher than their balance', function () {
            scope.$apply();
            setupNewDelivery();
            scope.selectedDeliveries = [
                {id: 1, balance: 10, item: orderItemId, quantityShipped: 50},
                {id: 2, balance: 20, item: orderItemId, quantityShipped: 10}
            ];
            scope.save();
            expect(mockDeliveryNodeService.create).not.toHaveBeenCalled();
            expect(scope.errors).toBeTruthy();
            expect(toast.create).toHaveBeenCalledWith({
                content: 'Cannot save. Please fill out or fix values for all fields marked in red',
                class: 'danger'
            });
        });

        it('should show success toast upon save', function () {
            scope.$apply();
            setupNewDelivery();
            scope.save();
            scope.$apply();
            timeout.flush();
            expect(toast.create.calls.count()).toBe(1);
            expect(toast.create).toHaveBeenCalledWith({
                content: 'Delivery Successfully Created',
                class: 'success'
            });
        });

        it('should redirect to deliveries by ip list upon successful save', function () {
            scope.$apply();
            setupNewDelivery();
            scope.save();
            scope.$apply();
            expect(location.path).toHaveBeenCalledWith('/deliveries-by-ip/' + routeParams.itemId)
        });

        it('should show failure toast when save fails', function () {
            scope.$apply();
            setupNewDelivery();
            mockDeliveryNodeService.create.and.returnValue(q.reject());
            scope.save();
            scope.$apply();
            expect(toast.create).toHaveBeenCalledWith({
                content: 'Failed to save delivery',
                class: 'danger'
            });
        });

        it('should fail to save new delivery if its quantities are from shipments with different order numbers bu the same order type', function () {
            scope.$apply();
            setupNewDelivery();
            scope.selectedDeliveries = [
                {id: 1, balance: 10, item: orderItemId, quantityShipped: 10, orderNumber: 444, orderType: 'waybill'},
                {id: 2, balance: 20, item: orderItemId, quantityShipped: 10, orderNumber: 555, orderType: 'waybill'}
            ];
            scope.save();
            expect(mockDeliveryNodeService.create).not.toHaveBeenCalled();
        });

        it('should fail to save new delivery if its quantities are from shipments with the same order numbers but different order types', function () {
            scope.$apply();
            setupNewDelivery();
            scope.selectedDeliveries = [
                {id: 1, balance: 10, item: orderItemId, quantityShipped: 10, orderNumber: 444, orderType: 'waybill'},
                {
                    id: 2,
                    balance: 20,
                    item: orderItemId,
                    quantityShipped: 10,
                    orderNumber: 444,
                    orderType: 'purchase order'
                }
            ];
            scope.save();
            expect(mockDeliveryNodeService.create).not.toHaveBeenCalled();
        });
    });

    describe('On assigning items to self', function () {
        beforeEach(function () {
            userGetCurrentUserPromise.resolve(stubCurrentIpUser);
            var toSelfRouteParams = {itemId: 2, deliveryMode: 'self'};
            initController(toSelfRouteParams);
        });

        it('should get correct delivery mode based on route-params', function () {
            scope.$apply();
            expect(scope.isAssigningItemsToSelf).toBeTruthy();
        });

        it('should get current login user, with its consignee info on load', function () {
            scope.$apply();
            expect(mockUserService.getCurrentUser).toHaveBeenCalled();
            expect(scope.currentUser).toEqual(stubCurrentIpUser);
            expect(scope.currentUser.consignee_id).not.toEqual(null);
        });

        it('should set is-end-user to true on load', function () {
            scope.$apply();
            expect(scope.newDelivery).not.toEqual(null);
            expect(scope.newDelivery.isEndUser).toBeTruthy();
        });
    });

    var assertSaveFails = {
        if: function (fieldname) {
            return {
                is: function (val) {
                    var unsetParams = {};
                    unsetParams[fieldname] = val;
                    setupNewDelivery(unsetParams);
                    scope.save();
                    expect(mockDeliveryNodeService.create).not.toHaveBeenCalled();
                    expect(scope.errors).toBeTruthy();
                    expect(toast.create).toHaveBeenCalledWith({
                        content: 'Cannot save. Please fill out or fix values for all fields marked in red',
                        class: 'danger'
                    });
                }
            }
        }
    };

    function setupNewDelivery(unset) {
        scope.newDelivery = {};
        scope.newDelivery.consignee = 10;
        scope.newDelivery.location = 'Jinja';
        scope.newDelivery.deliveryDate = '2015-01-30';
        scope.newDelivery.contact_person_id = '3A09C3B1-0937-4082-93D9-4ACC3E86B2B3';
        scope.newDelivery.parents = [{id: 1, quantity: 10}];
        Object.each(unset, function (key, value) {
            scope.newDelivery[key] = value;
        });
        return scope.newDelivery;
    }
});