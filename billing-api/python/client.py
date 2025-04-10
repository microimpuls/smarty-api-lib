# -*- coding: utf-8 -*-
import json
import urllib.parse
import hashlib
import base64
import urllib.request
import urllib.error
import urllib


class BillingAPIException(Exception):
    pass


class SmartyBillingAPI(object):
    def __init__(self, base_url, client_id, api_key):
        """
        :param base_url: хост smarty, например http://smarty.microimpuls.com
        :param client_id: идентефикатор клиента
        :param api_key: ключ клиента
        """
        self.base_url = base_url
        self.client_id = client_id
        self.api_key = api_key

    def _get_signature(self, request_data):
        sign_source = u''
        for (key, value) in sorted(request_data.items()):
            sign_source += u'%s:%s;' % (key, value)
        sign_source += self.api_key
        digester = hashlib.md5()
        sign_source_utf = sign_source.encode('utf-8')
        sign_source_base64 = base64.b64encode(sign_source_utf)
        digester.update(sign_source_base64)
        signature = digester.hexdigest()
        return signature

    def _get_full_url(self, path):
        parsed_base_url = urllib.parse.urlparse(self.base_url)
        full_url = urllib.parse.urlunparse(parsed_base_url._replace(path=path))
        return full_url

    def _api_request(self, path, data=None):
        url = self._get_full_url(path)
        data = data or {}
        data['client_id'] = self.client_id
        data['signature'] = self._get_signature(data)
        encoded_post_data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, encoded_post_data)
        response = urllib.request.urlopen(req)
        api_response = json.loads(response.read())
        if api_response['error']:
            error_message = "Api Error %(error)s: %(error_message)s" % api_response
            raise BillingAPIException(error_message)
        return api_response

    def transaction_create(self, customer_id, transaction_id, amount=0, comment='', **kwargs):
        params = {
            'customer_id': customer_id,
            'id': transaction_id,
            'amount': amount,
            'comment': comment
        }
        params.update(**kwargs)
        return self._api_request('/billing/api/transaction/create/', params)

    def transaction_delete(self, customer_id, transaction_id):
        params = {
            'customer_id': customer_id,
            'id': transaction_id,
        }
        return self._api_request('/billing/api/transaction/delete/', params)

    def customer_create(self, **kwargs):
        """ Создание кастомера
        """
        params = {}
        fields = {
            'firstname', 'middlename', 'lastname', 'birthdate',
            'passport_number', 'passport_series', 'passport_issue_date', 'passport_issued_by',
            'postal_address_street', 'postal_address_bld', 'postal_address_apt',
            'postal_address_zip', 'billing_address_street', 'billing_address_bld',
            'billing_address_apt', 'billing_address_zip',
            'mobile_phone_number', 'phone_number_1', 'phone_number_2', 'fax_phone_number',
            'email', 'company_name', 'comment', 'ext_id',
            'send_sms',
            'bank_account_blz', 'bank_account_bic', 'bank_account_number', 'bank_account_iban',
            'bank_account_bank_name', 'bank_account_owner_name',
            'contract_number', 'dealer_id',
            'meta',
            'send_sms_messages', 'send_email_messages',
            'postal_address_city', 'postal_address_country'
        }

        for key, value in kwargs.items():
            if key in fields:
                params[key] = value

        required_fields = ['firstname', 'lastname', 'middlename', 'comment']

        if not any(i in params.keys() for i in required_fields):
            raise BillingAPIException(
                "You must specify firstname or lastname or middlename or comment"
            )
        return self._api_request('/billing/api/customer/create/', params)

    def customer_modify(self, **kwargs):
        params = {}
        fields = {
            'customer_id', 'ext_id'
            'firstname', 'middlename', 'lastname', 'birthdate',
            'passport_number', 'passport_series', 'passport_issue_date', 'passport_issued_by',
            'postal_address_street', 'postal_address_bld', 'postal_address_apt',
            'postal_address_zip', 'billing_address_street', 'billing_address_bld',
            'billing_address_apt', 'billing_address_zip',
            'mobile_phone_number', 'phone_number_1', 'phone_number_2', 'fax_phone_number',
            'email', 'company_name', 'comment',
            'bank_account_blz', 'bank_account_bic', 'bank_account_number', 'bank_account_iban',
            'bank_account_bank_name', 'bank_account_owner_name',
            'send_sms_messages', 'send_email_messages',
            'meta',
        }

        for key, value in kwargs.items():
            if key in fields:
                params[key] = value

        if 'customer_id' not in params and 'ext_id' not in params:
            raise BillingAPIException(
                'You must specify customer_id or ext_id of customer to modify'
            )
        return self._api_request('/billing/api/customer/modify/', params)

    def customer_info(self, customer_id):
        params = {
            'customer_id': customer_id
        }
        return self._api_request('/billing/api/customer/info/', params)

    def customer_tariff_assign(self, customer_id, tariff_id):
        params = {
            'customer_id': customer_id,
            'tariff_id': tariff_id
        }
        return self._api_request('/billing/api/customer/tariff/assign/', params)

    def customer_tariff_remove(self, customer_id, tariff_id):
        params = {
            'customer_id': customer_id,
            'tariff_id': tariff_id
        }
        return self._api_request('/billing/api/customer/tariff/remove/', params)
    
    def account_info(self, abonement=None, account_id=None):
        assert any([abonement, account_id])
        params = {}
        if abonement:
            params.update(abonement=abonement)
        if account_id:
            params.update(account_id=account_id)
        return self._api_request('/billing/api/account/info/', params)

    def account_create(self, customer_id, auto_activation_period=None):
        params = {
            'customer_id': customer_id
        }
        if auto_activation_period:
            params['auto_activation_period'] = auto_activation_period
        return self._api_request('/billing/api/account/create/', params)

    def account_delete(self, abonement):
        params = {
            'abonement': abonement
        }
        return self._api_request('/billing/api/account/delete/', params)

    def account_activate(self, abonement):
        params = {
            'abonement': abonement
        }
        return self._api_request('/billing/api/account/activate/', params)

    def account_deactivate(self, abonement):
        params = {
            'abonement': abonement
        }
        return self._api_request('/billing/api/account/deactivate/', params)

    def tariff_list(self):
        return self._api_request('/billing/api/tariff/list/')


# api = SmartyBillingAPI(base_url='http://localhost:8000/', client_id=1, api_key='top secret')
# api.tariff_list()
# print(api.customer_create(
#     firstname='Bill',
#     middlename='Muriel',
#     meta='{"my_boolean_param": true, "my_int_param": 1, "my_str_param": "something"}'
# ))
# api.transaction_create(customer_id=1, transaction_id=4, processed=1, amount=50)
