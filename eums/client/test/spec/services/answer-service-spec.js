describe('Answer Service', function () {
    var answerService, mockServiceFactory, mockService;

    var answerId = 1;
    var answer = {value: 'Edited'};
    var data = {id: answerId, value: answer.value};

    beforeEach(function () {
        module('Answer');
        mockServiceFactory = jasmine.createSpyObj('mockServiceFactory', ['create']);
        mockService = jasmine.createSpyObj('mockService', ['update', 'create']);
        mockServiceFactory.create.and.returnValue(mockService);

        module(function ($provide) {
            $provide.value('ServiceFactory', mockServiceFactory);
        });

        inject(function (AnswerService) {
            answerService = AnswerService;
        });
    });

    it('should know how to update text answer', function () {
        answerService.updateTextAnswer(answerId, answer);
        expect(mockService.update).toHaveBeenCalledWith(data, 'PATCH');
    });

    it('should know how to update numeric answer', function () {
        answerService.updateNumericAnswer(answerId, answer);
        expect(mockService.update).toHaveBeenCalledWith(data, 'PATCH');
    });

    it('should know how to update multiple choice answer', function () {
        answerService.updateNumericAnswer(answerId, answer);
        expect(mockService.update).toHaveBeenCalledWith(data, 'PATCH');
    });

    it('should know how to create web answer', function () {
        var deliveryId = 1;
        var answers = [{questionLabel: 'received', value: 'Yes'}];

        answerService.createWebAnswer(deliveryId, answers);

        expect(mockService.create).toHaveBeenCalledWith(
            {
                delivery: deliveryId,
                answers: answers
            });
    });
});
