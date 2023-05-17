# -*- coding: utf-8 -*-

from cinema_start.api_client import CinemaStartApiClient
import logging
import requests
from core.utils import unicode_to_str
from external_api.video_api_client import api_has_subscription
from external_api.exceptions import ExternalApiException, NotEnoughFundsException
from tvmiddleware.billing_helpers import activation_price, SubscriptionCreator, get_subject_tariff_compat
from billing.currency import CurrencySettings
from clients.models import LocaleString
from clients.locale import BackendStrings
from billing.actions import buy_tariff
import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta

custom_logger = logging.getLogger('smarty_custom')


class BillingAPIException(Exception):
    """
    This class is designed to handle external billing errors

    Этот класс предназначен для обработки ошибок внешнего биллинга
    """
    def __init__(self, message, *args, **kwargs):
        if isinstance(message, requests.Response):
            message = message.content.decode('utf-8')
        self.message = unicode_to_str(message)
        super(BillingAPIException, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.message


class ExternalBillingIntegration(object):
    """
    This class is designed to work with external billing

    Класс предназначен для работы с внешним биллингом
    """
    def __init__(self, billing_base_url):
        self.billing_base_url = billing_base_url
        
    def add_additional_service_subscription(self, customer, subscription_id):
        """
        Creating a subscription in external billing

        Создание подписки во внешнем биллинге
        """

        url_api = self.billing_base_url + f'/rest/v1/subjects/customers/{customer.ext_id}/subscriptions/{subscription_id}/additional_services'

        dt = datetime.now()
        current_datetime = dt.astimezone().isoformat(sep="T", timespec="seconds")
        dt = dt + relativedelta(months=+1)
        next_date = dt.astimezone().isoformat(sep="T", timespec="seconds")

        data = {
            "additional_service": {
                "n_par_subscription_id": subscription_id,
                "n_service_id": "",
                "d_begin": current_datetime,
                "d_end": next_date,
                "n_quant": 1,
                "immediate": True
            } 
        }

        self._request(url_api, data)

    def _request(self, url, data):
        """
        Sending a request to create a subscription to external billing
        
        Отправка запроса во внешний биллинг
        """
        try:
            response = requests.post(url=url, json=data) # If the method is different from post, then you need to change the function to "requests.get"
        except Exception as exc:
            custom_logger.exception('external_billing_request_excepton', extra={'ctx': {
                'url': url,
                'data': data
            }})
            raise BillingAPIException(repr(exc))
        if response.status_code != 201:
            custom_logger.error('external_billing_response', extra={'ctx': {
                'error': response.text,
                'code': response.status_code
            }})
            raise BillingAPIException(response) 
        else:
            custom_logger.info("external_billing", extra={"ctx": {
                'url': url,
                'data': data,
                'response_content': response.content,
                'status_code': response.status_code
            }})


class CinemaStartCustomApiClient(CinemaStartApiClient):
    """
    An example of integrating a cinema subscription with external billing

    Пример интеграции подписки на кинотеатр с внешнем биллинге
    """
    def init(self, **kwargs):
        super(CinemaStartCustomApiClient, self).init(**kwargs)
        self.billing_base_url = kwargs.get('billing_base_url', '')

    def perform_video_action(self, video, action, goods_id, params):
        if action == 'subscribe':
            customer = params.account.customer
            smarty_tariff = self.get_tariff_obj()
            return self.subscribe_svod(customer, smarty_tariff)
        return {}

    def subscribe_svod(self, subject, smarty_tariff, skip_transaction_creation=False, dont_assign_tariff=False):
        """
        subject - The account or user object to pass in
        smarty_tariff - Tariff object
        skip_transaction_creation - Parameter responsible for disabling debiting the cost of the tariff from the account
        dont_assign_tariff - Parameter responsible for skipping the connection of the tariff in Smart in case of skipping the payment operation
        
        subject - Передаваемый объект аккаунта или пользователя
        smarty_tariff - Объект тарифа
        skip_transaction_creation - Параметр, отвечающий за отключение списания стоимости тарифа с аккаунта
        dont_assign_tariff - Параметр, отвечающий за пропуск подключения тарифа в смарти в случае пропуска операции оплаты
        """
        customer = self._customer_from_subject(subject)
        price = 0.0
        if not skip_transaction_creation:
            if settings.EXTERNAL_API_VIDEO_CHECK_BALANCE_REQUEST:
                self.perform_subscr_action_in_default_video_api_client(smarty_tariff.id, customer, 'check_balance')
                customer.refresh_from_db()

            price = float(activation_price(smarty_tariff, customer))
            if not self.ignore_customer_balance_check and price and price > customer.balance:
                raise NotEnoughFundsException('subscription price is greater than customer balance')

        has_subscription = api_has_subscription(subject, self.api_config)

        if not has_subscription:
            creator = SubscriptionCreator(smarty_tariff, subject, api_config=self.api_config, unlimited=True)
            subscription = creator.create()
            try:
                api = self.get_api()
                order_id = subscription.pk
                currency = CurrencySettings.get_currency_iso_code(customer.currency)
                api.subscribe(subject, order_id, price, currency, smarty_tariff.pk)
                ExternalBillingIntegration(self.billing_base_url).add_additional_service_subscription(customer, smarty_tariff)
            except Exception as e:
                subscription.delete()
                api.unsubscribe(subject)
                raise ExternalApiException(repr(e))

        if not self.ignore_customer_balance_check and not skip_transaction_creation:
            # WARN: BALANCE CHANGED
            template = LocaleString.get_string(customer.client, BackendStrings.tariff_activation_id)
            buy_tariff(customer, smarty_tariff, price, "external_billing_integration", template.format(id=smarty_tariff))
        elif not dont_assign_tariff:
            tariff_compat = get_subject_tariff_compat(subject)
            tariff_compat.assign(smarty_tariff)