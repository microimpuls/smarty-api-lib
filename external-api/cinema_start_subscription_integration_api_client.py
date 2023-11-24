# -*- coding: utf-8 -*-
"""
1. Данный файл должен быть импортирован при старте smarty,
Необходимо поместить его в директорию modules_available и он импортируется автоматически
2. Затем следует активировать в настройках системы: 
2.1 Авторизоваться в smarty
2.2 Во вкладке "Общие настройки" открыть пункт "Интеграция с API внешних систем" 
2.3 Создать новый объект, а в поле "API handler class:" выбрать текущую интеграцию
"""

from cinema_start.api_client import CinemaStartApiClient
import logging
import requests
import external_api.registry
from core.utils import unicode_to_str
from external_api.video_api_client import get_video_api_full_tariffs
from external_api.exceptions import ExternalApiException
from billing.currency import CurrencySettings
from datetime import datetime
from dateutil.relativedelta import relativedelta

from tvmiddleware.models import Subject, Tariff, TariffSubscription

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

    def subscribe_svod(self, subject: Subject, smarty_tariff: Tariff) -> None:
        """
        Subscribes the subject
        subject - The account or user object to pass in
        smarty_tariff - Tariff object
        
        Производит подписку субъекта
        subject - Передаваемый объект аккаунта или пользователя
        smarty_tariff - Объект тарифа
        """
        
        """Получаем пользователя из переданного объекта"""
        customer = self._customer_from_subject(subject)

        """Получаем стоимость тарифа"""
        price = float(smarty_tariff.price)

        """Проверяем подписки пользователя"""
        tariffs = get_video_api_full_tariffs(self.api_config)
        subscriptions = TariffSubscription.active_by_subject(subject).filter(tariff__in=tariffs)

        """Если это первая подписка пользователя, то добавляем её во внешний биллинг"""
        if len(subscriptions) == 1:
            try:
                api = self.get_api()
                order_id = subscriptions[0].pk
                currency = CurrencySettings.get_currency_iso_code(customer.currency)
                api.subscribe(subject, order_id, price, currency, smarty_tariff.pk)
                ExternalBillingIntegration(self.billing_base_url).add_additional_service_subscription(customer, smarty_tariff)
            except Exception as e:
                subscriptions[0].delete()
                raise ExternalApiException(repr(e))


external_api.registry.add('external_billing_integration', CinemaStartCustomApiClient)