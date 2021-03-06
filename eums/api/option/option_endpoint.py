from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from eums.models import Option


class OptionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text', 'question')


class OptionViewSet(ModelViewSet):
    queryset = Option.objects.all().order_by('text')
    serializer_class = OptionSerialiser


class ReceivedOptionViewSet(ModelViewSet):
    queryset = Option.objects.filter(question__label='productReceived').order_by('-text')
    serializer_class = OptionSerialiser


class QualityOptionViewSet(ModelViewSet):
    queryset = Option.objects.filter(question__label='qualityOfProduct').order_by('text')
    serializer_class = OptionSerialiser


class SatisfiedOptionViewSet(ModelViewSet):
    queryset = Option.objects.filter(question__label='satisfiedWithProduct').order_by('-text')
    serializer_class = OptionSerialiser


class DeliveryReceivedOptionViewSet(ModelViewSet):
    queryset = Option.objects.filter(question__label='deliveryReceived').order_by('-text')
    serializer_class = OptionSerialiser


class DeliverySatisfiedOptionViewSet(ModelViewSet):
    queryset = Option.objects.filter(question__label='satisfiedWithDelivery').order_by('-text')
    serializer_class = OptionSerialiser


class DeliveryConditionOptionViewSet(ModelViewSet):
    queryset = Option.objects.filter(question__label='isDeliveryInGoodOrder').order_by('-text')
    serializer_class = OptionSerialiser


optionRouter = DefaultRouter()
optionRouter.register(r'option', OptionViewSet)
optionRouter.register(r'received-options', ReceivedOptionViewSet)
optionRouter.register(r'quality-options', QualityOptionViewSet)
optionRouter.register(r'satisfied-options', SatisfiedOptionViewSet)
optionRouter.register(r'delivery-received-options', DeliveryReceivedOptionViewSet)
optionRouter.register(r'delivery-satisfied-options', DeliverySatisfiedOptionViewSet)
optionRouter.register(r'delivery-condition-options', DeliveryConditionOptionViewSet)
