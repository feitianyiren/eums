describe('IP Delivered Items Controller', function () {
    var mockDeliveryService, scope, location, mockLoaderService, q,
        mockDeliveryNodeService, controller, mockAnswerService;

    var nodeOne = {
        id: 1,
        location: 'Kampala',
        consignee: {id: 10},
        track: true,
        deliveryDate: '2015-01-02',
        remark: 'some remarks',
        item: 1,
        quantityIn: 10
    };

    var nodeTwo = {
        id: 2,
        location: 'Kampala',
        consignee: {id: 10},
        track: true,
        deliveryDate: '2015-01-02',
        remark: 'some other remarks',
        item: 2,
        quantityIn: 5
    };
    var deliveryNodes = [nodeOne, nodeTwo];

    var activeDelivery = {
        id: 1,
        location: 'Kampala',
        consignee: {id: 10},
        track: true,
        deliveryDate: '2015-01-02',
        remark: 'some remarks',
        totalValue: 6000,
        distributionplannodeSet: deliveryNodes,
        type: 'Purchase Order'
    };

    var firstNodeAnswers = [
        {
            question_label: 'itemReceived',
            type: 'multipleChoice',
            text: 'Was item received?',
            value: 'Yes',
            options: ['Yes'],
            position: 0
        },
        {
            "text": "How much was received?",
            "type": "numeric",
            "question_label": "amountReceived",
            "value": "10",
            "position": 1
        },
        {
            "text": "Was product in good order?",
            "type": "text",
            "question_label": "quality",
            "value": "",
            "position": 4
        },
        {
            question_label: 'satisfied',
            type: 'multipleChoice',
            text: 'are you satisfied?',
            value: '',
            options: ['Yes'],
            position: 3
        }
    ];
    var secondNodeAnswers = [
        {
            question_label: 'itemReceived',
            type: 'multipleChoice',
            text: 'Was item received?',
            value: 'Yes',
            options: ['Yes'],
            position: 0
        },
        {
            "text": "How much was received?",
            "type": "numeric",
            "question_label": "amountReceived",
            "value": "5",
            "position": 1
        },
        {
            "text": "Was product in good order?",
            "type": "text",
            "question_label": "quality",
            "value": "",
            "position": 4
        },
        {
            question_label: 'satisfied',
            type: 'multipleChoice',
            text: 'are you satisfied?',
            value: '',
            options: ['Yes'],
            position: 0
        }
    ];
    var nodeAnswers = [
        {
            id: 1, answers: firstNodeAnswers
        },
        {
            id: 2, answers: secondNodeAnswers
        }
    ];

    var combinedDeliveryNodes = [
        {
            id: 1,
            location: 'Kampala',
            consignee: {id: 10},
            quantityIn: 10,
            track: true,
            deliveryDate: '2015-01-02',
            remark: 'some remarks',
            item: 1,
            answers: firstNodeAnswers
        },
        {
            id: 2,
            location: 'Kampala',
            consignee: {id: 10},
            quantityIn: 5,
            track: true,
            deliveryDate: '2015-01-02',
            remark: 'some other remarks',
            item: 2,
            answers: secondNodeAnswers
        }];

    var nodeAnswersWithoutValues = [{
        id: 1,
        "answers": [
            {
                "question_label": "itemReceived",
                "text": "Was the item received?",
                "value": "",
                "position": 1,
                "type": "multipleChoice",
                "options": [
                    "No",
                    "Yes"
                ]
            },
            {
                "text": "How much was received?",
                "type": "numeric",
                "question_label": "amountReceived",
                "value": "",
                "position": 2
            },
            {
                "question_label": "qualityOfProduct",
                "text": "What is the quality of the product?",
                "value": "",
                "position": 3,
                "type": "multipleChoice",
                "options": [
                    "Incomplete",
                    "Expired",
                    "Substandard",
                    "Damaged",
                    "Good"
                ]
            },
            {
                "question_label": "satisfiedWithProduct",
                "text": "Are you satisfied with the product?",
                "value": "",
                "position": 4,
                "type": "multipleChoice",
                "options": [
                    "No",
                    "Yes"
                ]
            },
            {
                "text": "Remarks",
                "type": "text",
                "question_label": "additionalDeliveryComments",
                "value": "",
                "position": 5
            }
        ]

    }];

    var combinedDeliveryNodesWithAnswers = [
        {
            id: 1,
            location: 'Kampala',
            consignee: {id: 10},
            track: true,
            deliveryDate: '2015-01-02',
            remark: 'some remarks',
            item: 1,
            quantityIn: 10,
            answers: [
                {
                    "question_label": "itemReceived",
                    "text": "Was the item received?",
                    "value": "Yes",
                    "position": 1,
                    "type": "multipleChoice",
                    "options": [
                        "No",
                        "Yes"
                    ]
                },
                {
                    "text": "How much was received?",
                    "type": "numeric",
                    "question_label": "amountReceived",
                    "value": "10",
                    "position": 2
                },
                {
                    "question_label": "qualityOfProduct",
                    "text": "What is the quality of the product?",
                    "value": "",
                    "position": 3,
                    "type": "multipleChoice",
                    "options": [
                        "Incomplete",
                        "Expired",
                        "Substandard",
                        "Damaged",
                        "Good"
                    ]
                },
                {
                    "question_label": "satisfiedWithProduct",
                    "text": "Are you satisfied with the product?",
                    "value": "Yes",
                    "position": 4,
                    "type": "multipleChoice",
                    "options": [
                        "No",
                        "Yes"
                    ]
                },
                {
                    "text": "Remarks",
                    "type": "text",
                    "question_label": "additionalDeliveryComments",
                    "value": "",
                    "position": 5
                }
            ]
        }
    ];

    function initializeController() {
        controller('ItemsDeliveredToIpController', {
            $scope: scope,
            LoaderService: mockLoaderService,
            DeliveryService: mockDeliveryService,
            DeliveryNodeService: mockDeliveryNodeService,
            $routeParams: {activeDeliveryId: 1}
        });
    }

    beforeEach(function () {

        module('ItemsDeliveredToIp');

        inject(function ($controller, $rootScope, $location, $q, LoaderService, AnswerService, DeliveryService,
                         DeliveryNodeService) {
            controller = $controller;
            scope = $rootScope.$new();
            location = $location;
            q = $q;
            mockLoaderService = LoaderService;
            mockAnswerService = AnswerService;
            mockDeliveryService = DeliveryService;
            mockDeliveryNodeService = DeliveryNodeService;

            spyOn(mockLoaderService, 'showLoader');
            spyOn(mockLoaderService, 'showModal');
            spyOn(mockLoaderService, 'hideLoader');
            spyOn(mockAnswerService, 'createWebAnswer');
            spyOn(mockDeliveryService, 'get');
            spyOn(mockDeliveryService, 'getDetail');
            spyOn(mockDeliveryNodeService, 'filter');
            spyOn(location, 'path');

        });
    });

    describe('on load', function () {

        beforeEach(function () {
            mockDeliveryService.get.and.returnValue(q.when(activeDelivery));
            mockDeliveryService.getDetail.and.returnValue(q.when(nodeAnswers));
            mockDeliveryNodeService.filter.and.returnValue(q.when(deliveryNodes));
        });

        it('should show loader while loading', function () {
            initializeController();
            scope.$apply();

            expect(mockLoaderService.showLoader).toHaveBeenCalled();
            expect(mockLoaderService.showLoader.calls.count()).toBe(1);
        });

        it('should call the delivery service and set the shipment date and total value in the scope', function () {
            initializeController();
            scope.$apply();

            expect(mockDeliveryService.get).toHaveBeenCalledWith(1);
            expect(mockDeliveryNodeService.filter).toHaveBeenCalledWith({distribution_plan: 1});
            expect(scope.shipmentDate).toBe('2015-01-02');
            expect(scope.totalValue).toBe(6000)
        });

        it('should load answers for a delivery', function () {
            initializeController();
            scope.$apply();

            expect(mockDeliveryService.getDetail).toHaveBeenCalledWith(activeDelivery, 'answers');
        });

        it('should set default values when not satisfied and not in good condition', function () {
            mockDeliveryService.getDetail.and.returnValue(q.when([{
                "question_label": "isDeliveryInGoodOrder",
                "text": "Was delivery in good condition?",
                "value": "No",
                "position": 3,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }, {
                "question_label": "satisfiedWithDelivery",
                "text": "Are you satisfied with the delivery?",
                "value": "No",
                "position": 4,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }]));
            initializeController();
            scope.$apply();

            expect(scope.defaultItemCondition).toEqual('');
            expect(scope.isSatisfied).toEqual('No');
        });

        it('should set default values when not satisfied and in good condition', function () {
            mockDeliveryService.getDetail.and.returnValue(q.when([{
                "question_label": "isDeliveryInGoodOrder",
                "text": "Was delivery in good condition?",
                "value": "Yes",
                "position": 3,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }, {
                "question_label": "satisfiedWithDelivery",
                "text": "Are you satisfied with the delivery?",
                "value": "No",
                "position": 4,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }]));
            initializeController();
            scope.$apply();

            expect(scope.defaultItemCondition).toEqual('Good');
            expect(scope.isSatisfied).toEqual('No');
        });

        it('should set default values when satisfied and in good condition', function () {
            mockDeliveryService.getDetail.and.returnValue(q.when([{
                "question_label": "isDeliveryInGoodOrder",
                "text": "Was delivery in good condition?",
                "value": "Yes",
                "position": 3,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }, {
                "question_label": "satisfiedWithDelivery",
                "text": "Are you satisfied with the delivery?",
                "value": "Yes",
                "position": 4,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }]));
            initializeController();
            scope.$apply();

            expect(scope.defaultItemCondition).toEqual('Good');
            expect(scope.isSatisfied).toEqual('Yes');
        });

        it('should set default values when satisfied and not in good condition', function () {
            mockDeliveryService.getDetail.and.returnValue(q.when([{
                "question_label": "isDeliveryInGoodOrder",
                "text": "Was delivery in good condition?",
                "value": "No",
                "position": 3,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }, {
                "question_label": "satisfiedWithDelivery",
                "text": "Are you satisfied with the delivery?",
                "value": "Yes",
                "position": 4,
                "type": "multipleChoice",
                "options": ["No", "Yes"]
            }]));
            initializeController();
            scope.$apply();

            expect(scope.defaultItemCondition).toEqual('');
            expect(scope.isSatisfied).toEqual('Yes');
        });

        it('should get all the answers for all nodes belonging to a delivery', function () {
            initializeController();
            scope.$apply();

            expect(mockDeliveryService.getDetail).toHaveBeenCalledWith(activeDelivery, 'node_answers');
        });

        it('should combine nodes and node answers belonging to a delivery', function () {
            initializeController();
            scope.$apply();

            expect(scope.combinedDeliveryNodes).toEqual(combinedDeliveryNodes);
        });

        it('should default itemReceived to yes and quantityReceived to quantity shipped when no values exist for those answers', function () {
            var isFirstTime = true;
            mockDeliveryService.getDetail.and.callFake(function () {
                if (isFirstTime) {
                    isFirstTime = false;
                    return q.when([{
                        "question_label": "isDeliveryInGoodOrder",
                        "text": "Was delivery in good condition?",
                        "value": "No",
                        "position": 3,
                        "type": "multipleChoice",
                        "options": ["No", "Yes"]
                    }, {
                        "question_label": "satisfiedWithDelivery",
                        "text": "Are you satisfied with the delivery?",
                        "value": "Yes",
                        "position": 4,
                        "type": "multipleChoice",
                        "options": ["No", "Yes"]
                    }])
                }
                return q.when(nodeAnswersWithoutValues)
            });
            initializeController();
            scope.$apply();

            expect(scope.combinedDeliveryNodes).toEqual(combinedDeliveryNodesWithAnswers);
        });

        it('should hide the loader after loading the data', function () {
            initializeController();
            scope.$apply();

            expect(mockLoaderService.hideLoader).toHaveBeenCalled();
            expect(mockLoaderService.hideLoader.calls.count()).toBe(1);
        });

        it('should show the add remarks modal for a specific node when add remark button is clicked', function () {
            initializeController();
            scope.$apply();

            scope.addRemark(1);
            scope.$apply();

            expect(mockLoaderService.showModal).toHaveBeenCalledWith('add-remark-answer-modal-1')
        });
    });

    describe('on save', function () {
        beforeEach(function () {
            mockDeliveryService.get.and.returnValue(q.when(activeDelivery));
            mockDeliveryService.getDetail.and.returnValue(q.when(nodeAnswers));
            mockDeliveryNodeService.filter.and.returnValue(q.when(deliveryNodes));
        });

        it('should show loader while saving', function () {
            initializeController();
            scope.$apply();
            scope.saveAnswers();
            scope.$apply();

            expect(mockLoaderService.showLoader).toHaveBeenCalled();
            expect(mockLoaderService.showLoader.calls.count()).toBe(2);
        });

        it('should call save web answers end points', function () {
            mockAnswerService.createWebAnswer.and.returnValue(q.when());
            initializeController();
            scope.$apply();

            scope.saveAnswers();
            scope.$apply();

            expect(mockAnswerService.createWebAnswer).toHaveBeenCalled();
            expect(mockAnswerService.createWebAnswer.calls.count()).toBe(2);
        });

        it('should not send answers if answer to item received is no', function () {
            mockAnswerService.createWebAnswer.and.returnValue(q.when());
            initializeController();
            scope.$apply();

            var deliveryNode = {
                id: 1,
                "answers": [
                    {
                        "question_label": "itemReceived",
                        "text": "Was the item received?",
                        "value": "No",
                        "position": 1,
                        "type": "multipleChoice",
                        "options": [
                            "No",
                            "Yes"
                        ]
                    },
                    {
                        "text": "How much was received?",
                        "type": "numeric",
                        "question_label": "amountReceived",
                        "value": 4,
                        "position": 2
                    },
                    {
                        "question_label": "qualityOfProduct",
                        "text": "What is the quality of the product?",
                        "value": "Substandard",
                        "position": 3,
                        "type": "multipleChoice",
                        "options": [
                            "Incomplete",
                            "Expired",
                            "Substandard",
                            "Damaged",
                            "Good"
                        ]
                    },
                    {
                        "question_label": "satisfiedWithProduct",
                        "text": "Are you satisfied with the product?",
                        "value": "No",
                        "position": 4,
                        "type": "multipleChoice",
                        "options": [
                            "No",
                            "Yes"
                        ]
                    },
                    {
                        "text": "Remarks",
                        "type": "text",
                        "question_label": "additionalDeliveryComments",
                        "value": "2222222222",
                        "position": 5
                    }
                ]

            };

            var expectedUsedAnswers = [
                {
                    "question_label": "itemReceived",
                    "text": "Was the item received?",
                    "value": "No",
                    "position": 1,
                    "type": "multipleChoice",
                    "options": [
                        "No",
                        "Yes"
                    ]
                }
            ];

            scope.combinedDeliveryNodes = [deliveryNode];

            scope.$apply();
            scope.saveAnswers();
            scope.$apply();
            expect(location.path).toHaveBeenCalledWith('/ip-deliveries');
            expect(mockAnswerService.createWebAnswer).toHaveBeenCalledWith(deliveryNode, expectedUsedAnswers);
        });

        it('should navigate to the home page upon success', function () {
            mockAnswerService.createWebAnswer.and.returnValue(q.when());
            initializeController();
            scope.$apply();
            scope.saveAnswers();
            scope.$apply();

            expect(location.path).toHaveBeenCalledWith('/ip-deliveries');
        });

        it('should hide loader at the end', function () {
            mockAnswerService.createWebAnswer.and.returnValue(q.when());
            initializeController();
            scope.$apply();
            scope.saveAnswers();
            scope.$apply();

            expect(mockLoaderService.hideLoader).toHaveBeenCalled();
            expect(mockLoaderService.hideLoader.calls.count()).toBe(2);
        });

        it('should disable fields and set values when item received is set to No', function () {
            initializeController();
            scope.$apply();

            scope.combinedDeliveryNodes = [
                {
                    id: 1,
                    "answers": [
                        {
                            "question_label": "itemReceived",
                            "text": "Was the item received?",
                            "value": "No",
                            "position": 1,
                            "type": "multipleChoice",
                            "options": [
                                "No",
                                "Yes"
                            ]
                        },
                        {
                            "text": "How much was received?",
                            "type": "numeric",
                            "question_label": "amountReceived",
                            "value": 4,
                            "position": 2
                        },
                        {
                            "question_label": "qualityOfProduct",
                            "text": "What is the quality of the product?",
                            "value": "Substandard",
                            "position": 3,
                            "type": "multipleChoice",
                            "options": [
                                "Incomplete",
                                "Expired",
                                "Substandard",
                                "Damaged",
                                "Good"
                            ]
                        },
                        {
                            "question_label": "satisfiedWithProduct",
                            "text": "Are you satisfied with the product?",
                            "value": "No",
                            "position": 4,
                            "type": "multipleChoice",
                            "options": [
                                "No",
                                "Yes"
                            ]
                        },
                        {
                            "text": "Remarks",
                            "type": "text",
                            "question_label": "additionalDeliveryComments",
                            "value": "2222222222",
                            "position": 5
                        }
                    ]

                }
            ];

            scope.$apply();

            var changedDeliveryNodes = [
                {
                    id: 1,
                    answers: [
                        {
                            "question_label": "itemReceived",
                            "text": "Was the item received?",
                            "value": "No",
                            "position": 1,
                            "type": "multipleChoice",
                            "options": [
                                "No",
                                "Yes"
                            ]
                        },
                        {
                            "text": "How much was received?",
                            "type": "numeric",
                            "question_label": "amountReceived",
                            "value": '0',
                            "position": 2
                        },
                        {
                            "question_label": "qualityOfProduct",
                            "text": "What is the quality of the product?",
                            "value": "Incomplete",
                            "position": 3,
                            "type": "multipleChoice",
                            "options": [
                                "Incomplete",
                                "Expired",
                                "Substandard",
                                "Damaged",
                                "Good"
                            ]
                        },
                        {
                            "question_label": "satisfiedWithProduct",
                            "text": "Are you satisfied with the product?",
                            "value": "No",
                            "position": 4,
                            "type": "multipleChoice",
                            "options": [
                                "No",
                                "Yes"
                            ]
                        },
                        {
                            "text": "Remarks",
                            "type": "text",
                            "question_label": "additionalDeliveryComments",
                            "value": "2222222222",
                            "position": 5
                        }
                    ]
                }
            ];

            expect(scope.combinedDeliveryNodes).toEqual(changedDeliveryNodes);

        });

        describe('validations', function () {
            it('should set can save answer to false when a value is not set', function () {
                initializeController();
                scope.$apply();

                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'itemReceived',
                            type: 'multipleChoice',
                            text: 'Was item received?',
                            value: '',
                            options: ['Yes'],
                            position: 0
                        }
                    ]
                    },
                    {
                        id: 2, answers: [
                        {
                            question_label: 'additionalComments',
                            type: 'text',
                            text: 'Any additional comments?',
                            value: '',
                            position: 1
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(false);
            });

            it('should set can save answer to false when numeric question has non positive answer', function () {
                initializeController();
                scope.$apply();
                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'amountReceived',
                            type: 'numeric',
                            text: 'Amount received?',
                            value: -1,
                            options: [],
                            position: 0
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(false);
            });

            it('should set can save answers to false when numeric is not a number', function () {
                initializeController();
                scope.$apply();

                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'amountReceived',
                            type: 'numeric',
                            text: 'Amount received?',
                            value: 'not a number',
                            options: [],
                            position: 0
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(false);
            });

            it('should set can save answers to false when value is empty', function () {
                initializeController();
                scope.$apply();

                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'amountReceived',
                            type: 'numeric',
                            text: 'Amount received?',
                            value: '',
                            options: [],
                            position: 0
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(false);
            });

            it('should set can save answer to false when numeric question has zero answer', function () {
                initializeController();
                scope.$apply();
                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'amountReceived',
                            type: 'numeric',
                            text: 'Amount received?',
                            value: '0',
                            options: [],
                            position: 0
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(true);
            });

            it('should set can save answer to true when numeric value is positive number', function () {
                initializeController();
                scope.$apply();

                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'amountReceived',
                            type: 'numeric',
                            text: 'Amount received?',
                            value: 2,
                            options: [],
                            position: 0
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(true);
            });

            it('should set can save answer to true when all values are set', function () {
                initializeController();
                scope.$apply();

                scope.combinedDeliveryNodes = [
                    {
                        id: 1, answers: [
                        {
                            question_label: 'itemReceived',
                            type: 'multipleChoice',
                            text: 'Was item received?',
                            value: 'Yes',
                            options: ['Yes'],
                            position: 0
                        }
                    ]
                    },
                    {
                        id: 2, answers: [
                        {
                            question_label: 'additionalComments',
                            type: 'text',
                            text: 'Any additional comments?',
                            value: 'Remarks',
                            position: 1
                        },
                        {
                            question_label: 'quantityReceived',
                            type: 'numeric',
                            text: 'How many did you receive?',
                            value: 10,
                            position: 1
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(true);
            });

            it('should not validate remarks', function () {
                initializeController();
                scope.$apply();

                scope.combinedDeliveryNodes = [
                    {

                        id: 2, answers: [
                        {
                            question_label: 'additionalDeliveryComments',
                            type: 'text',
                            text: 'Remarks',
                            value: '',
                            position: 1
                        }
                    ]
                    }
                ];
                scope.$apply();

                expect(scope.areValidAnswers).toBe(true);
            });
        });
    });
});

