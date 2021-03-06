import copy
import json
import logging
from urllib import urlencode

import requests
from django.conf import settings

from rest_framework.status import HTTP_200_OK, HTTP_504_GATEWAY_TIMEOUT

from eums.celery import app

logger = logging.getLogger(__name__)

HEADER_CONTACT = {"Content-Type": "application/json"}
HEADER_RAPID_PRO = {'Authorization': 'Token %s' % settings.RAPIDPRO_API_TOKEN, "Content-Type": "application/json"}


class ContactService(object):
    contact_type_map = {
        'IMPLEMENTING_PARTNER': 'IP',
        'MIDDLE_MAN': 'Sub-consignee',
        'END_USER': 'End-user'
    }

    @staticmethod
    def get(contact_person_id):
        default_contact = {'_id': '', 'firstName': '', 'lastName': '', 'phone': '',
                           'types': [], 'outcomes': [], 'ips': [], 'districts': []}

        try:
            response = requests.get(url='%s%s' % (settings.CONTACTS_SERVICE_URL, contact_person_id))
            if response.status_code is HTTP_200_OK:
                return response.json()

            logger.error('Contact not found')
            return default_contact
        except Exception, error:
            logger.error(error)
            return default_contact

    @staticmethod
    def get_all():
        contacts = [{'_id': '', 'firstName': '', 'lastName': '', 'phone': '',
                     'types': [], 'outcomes': [], 'ips': [], 'districts': []}]
        try:
            response = requests.get(url='%s' % settings.CONTACTS_SERVICE_URL)
            if response.status_code is HTTP_200_OK:
                return response.json()

            logger.error('Contact not found')
            return contacts
        except Exception, error:
            logger.error(error)
            return contacts

    @staticmethod
    def get_by_user_id(created_by_user_id):
        contacts = [{'_id': '', 'firstName': '', 'lastName': '', 'phone': '',
                     'types': [], 'outcomes': [], 'ips': [], 'districts': []}]
        try:
            response = requests.get('%s?createdbyuserid=%s' % (settings.CONTACTS_SERVICE_URL, created_by_user_id))
            if response.status_code is HTTP_200_OK:
                return response.json()

            logger.error('Contact not found')
            return contacts
        except Exception, error:
            logger.error(error)
            return contacts

    @staticmethod
    def search(param):
        default_contact = {'_id': '', 'firstName': '', 'lastName': '', 'phone': '',
                           'types': [], 'outcomes': [], 'ips': [], 'districts': []}
        try:
            response = requests.get(url='%s?searchfield=%s' % (settings.CONTACTS_SERVICE_URL, param))
            if response.status_code is HTTP_200_OK:
                return response.json()

            logger.error('Contact not found')
            return default_contact
        except Exception, error:
            logger.error(error)
            return default_contact

    @staticmethod
    def delete(contact_person_id):
        try:
            response = requests.delete(url='%s%s' % (settings.CONTACTS_SERVICE_URL, contact_person_id))
            return response.status_code
        except Exception, error:
            logger.error(error)
            return HTTP_504_GATEWAY_TIMEOUT

    @staticmethod
    def update(contact):
        try:
            response = requests.put(settings.CONTACTS_SERVICE_URL, json.dumps(contact),
                                    headers=HEADER_CONTACT)
            return response.status_code
        except Exception, error:
            logger.error(error)
            return HTTP_504_GATEWAY_TIMEOUT

    @staticmethod
    def add(contact):
        try:
            return requests.post(settings.CONTACTS_SERVICE_URL, json.dumps(contact),
                                 headers=HEADER_CONTACT)
        except Exception, error:
            logger.error(error)
            return HTTP_504_GATEWAY_TIMEOUT

    @staticmethod
    def update_after_delivery_creation(contact_id, type, outcome, district, ip):
        try:
            origin_contact = ContactService.get(contact_id)
            updated_contact = ContactService._update_contact(origin_contact, type, outcome, district, ip)

            if origin_contact != updated_contact:
                ContactService.update(updated_contact)
                ContactService.add_or_update_rapid_pro_contact(updated_contact)
        except Exception, e:
            logger.error(e)

    @staticmethod
    def _append_if_not_exist(val, value_list=[]):
        if val and (val not in value_list):
            value_list.append(val)

    @staticmethod
    def _update_contact(origin_contact, type, outcome, district, ip):
        updated_contact = copy.deepcopy(origin_contact)
        ContactService._append_if_not_exist(type, updated_contact['types'])
        ContactService._append_if_not_exist(outcome, updated_contact['outcomes'])
        ContactService._append_if_not_exist(ip, updated_contact['ips'])
        ContactService._append_if_not_exist(district, updated_contact['districts'])
        return updated_contact

    @staticmethod
    def add_or_update_rapid_pro_contact(contact):
        logger.info('rapid pro live = %s' % settings.RAPIDPRO_LIVE)

        if not settings.RAPIDPRO_LIVE:
            return

        rapid_pro_contact = ContactService.build_rapid_pro_contact(contact)
        phone = contact.get('phone')
        pre_phone = contact.get('prePhone')

        pre_rapid_pro_contact = ContactService.get_rapid_pro_contact(pre_phone or phone).json()
        results = pre_rapid_pro_contact.get('results')

        if results:
            rapid_pro_contact.update({
                'uuid': results[0].get('uuid')
            })
            if results[0].get('urns'):
                rapid_pro_contact.get('urns').extend(results[0].get('urns'))
            if pre_phone and pre_phone != phone:
                try:
                    rapid_pro_contact.get('urns').remove('tel:%s' % pre_phone)
                except ValueError:
                    pass

        response = ContactService.__post_contact_to_rapid_pro(rapid_pro_contact)
        logger.info('add or update rapid pro contact response = [%s]' % response)
        return response

    @staticmethod
    def __post_contact_to_rapid_pro(contact):
        try:
            url = settings.RAPIDPRO_URLS.get('CONTACTS')
            if contact.get('uuid'):
                url = '%s?%s' % (url, urlencode({'uuid': contact.get('uuid')}))
            response = requests.post(url, data=json.dumps(contact),
                                     headers=HEADER_RAPID_PRO, verify=settings.RAPIDPRO_SSL_VERIFY)
            logger.info('rapid pro contact api response: %s', response.json())
            return response
        except Exception, error:
            logger.error(error)
            return HTTP_504_GATEWAY_TIMEOUT

    @staticmethod
    def get_rapid_pro_contact_group(name):
        if not settings.RAPIDPRO_LIVE:
            return

        url_get_rapid_pro_contact_group = '%s?%s' % (settings.RAPIDPRO_URLS.get('GROUPS'), urlencode({
            'name': '%s' % name
        }))
        response = requests.get(url_get_rapid_pro_contact_group, headers=HEADER_RAPID_PRO,
                                verify=settings.RAPIDPRO_SSL_VERIFY)
        return response.json()['results'][0] if len(response.json()['results']) > 0 else None

    @staticmethod
    def get_rapid_pro_contact(phone):
        if not settings.RAPIDPRO_LIVE:
            return

        params = {'urn': 'tel:%s' % phone}
        response = requests.get(settings.RAPIDPRO_URLS.get('CONTACTS'), params=params, headers=HEADER_RAPID_PRO,
                                verify=settings.RAPIDPRO_SSL_VERIFY)
        return response

    @staticmethod
    def delete_rapid_pro_contact(phone):
        if not settings.RAPIDPRO_LIVE:
            return

        url_delete_rapid_pro_contact = '%s?%s' % (settings.RAPIDPRO_URLS.get('CONTACTS'), urlencode({
            'urns': 'tel:%s' % phone
        }))
        response = requests.delete(url_delete_rapid_pro_contact, headers=HEADER_RAPID_PRO,
                                   verify=settings.RAPIDPRO_SSL_VERIFY)
        return response

    @staticmethod
    def build_rapid_pro_contact(contact):
        group_name = 'EUMS'
        contact_group = ContactService.get_rapid_pro_contact_group(group_name)
        contact_group_uuid = contact_group['uuid'] if contact_group else ''
        logger.info('group uuid of EUMS is %s' % contact_group_uuid)

        return {
            'name': '%(firstName)s %(lastName)s' % contact,
            'groups': [contact_group_uuid],
            'urns': ['tel:%(phone)s' % contact],
            'fields': ContactService.build_rapid_pro_contact_fields(contact)
        }

    @staticmethod
    def build_rapid_pro_contact_fields(contact):
        contact_label = ContactService.convert_contact_types(contact.get('types'))
        return {
            'firstname': contact.get('firstName'),
            'lastname': contact.get('lastName'),
            'districts': ','.join(contact.get('districts')) if contact.get('districts') else str(None),
            'ips': ','.join(contact.get('ips')) if contact.get('ips') else str(None),
            'types': ','.join(contact_label) if contact_label else str(None),
            'outcomes': ','.join(contact.get('outcomes')) if contact.get('outcomes') else str(None),
        }

    @staticmethod
    def convert_contact_types(pre_types):
        if not pre_types:
            return None

        new_types = []
        for contact_label in pre_types:
            if contact_label in ContactService.contact_type_map:
                new_types.append(ContactService.contact_type_map[contact_label])
        return new_types

    @staticmethod
    def get_rapid_pro_contact_uuid(phone):
        try:
            results = ContactService.get_rapid_pro_contact(phone).json().get('results')
            return results[0].get('uuid')
        except Exception, error:
            logger.error(error)


@app.task
def execute_rapid_pro_contact_update(contact):
    logger.info('%s%s%s' % ('*' * 10, 'update rapid pro contact', '*' * 10))
    ContactService.add_or_update_rapid_pro_contact(contact)


@app.task
def execute_rapid_pro_contact_delete(phone):
    logger.info('%s%s%s' % ('*' * 10, 'delete rapid pro contact', '*' * 10))
    ContactService.delete_rapid_pro_contact(phone)
