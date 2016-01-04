from abc import ABCMeta, abstractmethod

import requests
from celery.utils.log import get_task_logger

from eums import settings

logger = get_task_logger(__name__)


class VisionException(Exception):
    def __init__(self, message=''):
        super(VisionException, self).__init__(message)


class VisionDataSynchronizer:
    __metaclass__ = ABCMeta
    NO_DATA_MESSAGE = u'No Data Available'

    def __init__(self, url):
        if not url:
            raise VisionException(message='Url is required')

        self.url = url
        logger.info("Vision sync url:%s" % self.url)

    @abstractmethod
    def _convert_records(self, records):
        pass

    @abstractmethod
    def _save_records(self, records):
        pass

    @abstractmethod
    def _get_json(self, data):
        return []

    def _load_records(self):
        response = requests.get(self.url, headers={'Content-Type': 'application/json'},
                                auth=(settings.VISION_USER, settings.VISION_PASSWORD),
                                verify=False)

        if response.status_code != 200:
            raise VisionException(message=('Load data failed! Http code:%s' % response.status_code))

        return self._get_json(response.json())

    def sync(self):
        try:
            original_records = self._load_records()
            converted_records = self._convert_records(original_records)
            self._save_records(converted_records)
        except Exception, e:
            raise VisionException(message=e.message)
