"""
Установка:
1. Поместить файл в директорию Smarty /modules_available.
2. Перезагрузить Smarty.

Использование:
1. В меню Smarty "Интеграция с API внешних систем" создать новую интеграцию.
2. В поле "API handler class" указать созданный класс (в данном примере: "example_api_client").
3. Задать необходимые "Дополнительные атрибуты", которые будут передаваться в __init__ класса (в примере: base_url).
4. Сохранить.
"""

from datetime import datetime
import logging
import requests

from urllib.parse import urljoin
from django.utils.translation import gettext_lazy as _

import external_api.registry
from billing.api_client import SmartyBilling, SmartyBillingErrorBalance, SmartyBillingErrorTariffAlreadyActive
from external_api.exceptions import ExternalApiException
from tvmiddleware.api_base import TVMiddlewareApiParams
from tvmiddleware.billing_helpers import CustomerTariffService, SubjectSubscriptionService
from tvmiddleware.exceptions import CustomerAssignTariffBalanceError
from tvmiddleware.models import Account, Customer, Tariff

from external_api.objects import AccountRegisterResponse, TariffAssignResponse
from tvmiddleware.models import AccountHelper, ClientPlayDevice
from tvmiddleware.billing_helpers import activation_price
from tvmiddleware.register import RegisterParams, RegisterProcess


# логи располагаются в /logs/smarty_custom.log
logger = logging.getLogger('smarty_custom')


class ExampleHydraClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, method_url, data, method):
        url = urljoin(self.base_url, method_url)
        log_ctx = {'url': url}

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            if method == "post":
                response = requests.post(url, json=data, headers=headers)
            elif method == "put":
                response = requests.put(url, json=data, headers=headers)
            else:
                response = requests.get(url, data, headers=headers)

            log_ctx.update({
                'status_code': response.status_code,
                'response': response.text
            })

            response.raise_for_status()

            # логирование успешного запроса
            logger.debug('hydra_request', extra={'ctx': log_ctx})

            response = response.json()
        except requests.HTTPError:
            # логирование неуспешного запроса
            logger.warning('hydra_request', extra={'ctx': log_ctx})
            return None
        except Exception:
            # логирование исключения
            logger.exception('external_billing_request_exception', extra={'ctx': log_ctx})
            # в случае возникновения исключения ExternalApiException метод /login вернет код 3,
            #                                                              /account_status вернет код 2
            raise ExternalApiException('unexpected external api error')
        else:
            return response

    def show_customer(self, customer_id):
        method_url = f'/rest/v1/subjects/customers/{customer_id}'
        response = self._request(method_url, {}, '')
        return response.get('customer')

    def create_customer(self, register_params: RegisterParams):
        """Метод создания кастомера во внешнем биллинге"""

        """Пример формирования данных на основе register_params для отправки в внешний биллинг"""
        data = {
            "customer": {
                "n_base_subject_id": 78194101,
                "vc_code": "Meine created",
                "t_tags": [
                    "тестовый_абонент"
                ],
                "n_subj_group_id": 55027301,
                "group_ids": [
                    40250801
                ],
                "vc_rem": register_params.comment
            }
        }
        method_url = "/rest/v1/subjects/customers/"
        response = self._request(method_url, data=data, method="post")
        return response

    def create_subscription(self, external_id_tariff, external_id_customer):
        """Создания подписки во внешнем биллинге"""

        """Формирование данных для отправки во внешний биллинг"""
        data = {
            "subscription": {
                "n_service_id": external_id_tariff,
                "n_customer_id": external_id_customer,
                "d_begin": datetime.now().astimezone().isoformat(sep="T", timespec="seconds")
            }
        }
        url = f'/rest/v1/subjects/customers/{external_id_customer}/subscriptions/'
        self._request(url, data=data, method="post")

    def close_subscription(self, external_id_tariff, external_id_customer):
        """Отключение подписки во внешнем биллинге"""

        """Формирование данных для отправки во внешний биллинг"""
        data = {
            "subscription": {
                "n_service_id": external_id_tariff,
                "n_customer_id": external_id_customer,
                "d_end": datetime.now().astimezone().isoformat(sep="T", timespec="seconds"),
                "close_charge_log": True
            }
        }
        url = f'/rest/v1/subjects/customers/{external_id_customer}/subscriptions/{external_id_tariff}'
        self._request(url, data=data, method="put")


class ExampleApiClient(SmartyBilling):
    def __init__(self, base_url, **kwargs):
        super().__init__(**kwargs)
        self.hydra_api = ExampleHydraClient(base_url=base_url)

    def check_account(
            self,
            account: Account,
            ip: str,
            device_uid: str,
            device_model: str,
            params: TVMiddlewareApiParams, **kwargs
    ) -> str:
        """Проверка статуса аккаунта во внешнем биллинге.
        При ошибке проверки нужно кидать исключение ExternalApiException.
        :param account: объект аутентифицированного аккаунта, от лица которого осуществляется запрос к методу /login
        или /account_status,
        :param ip: ip-адрес источника запроса к методу /login или /account_status,
        :param device_uid: uid устройства, переданный в метод /login или /account_status,
        :param device_model: модель устройства, переданная в метод /login или /account_status,
        :param params: объект содержащий полную информацию о запросе к методу /login или /account_status
        :returns: str
        """

        # Проверка считается успешной если не возникло исключение ExternalApiException

        # Условие успешной проверки
        if account and self.hydra_api.show_customer(account.ext_id):
            # Проверка успешна. /login и /account_status вернут код 0
            # Возвращаемое значение будет занесено в лог smarty_accounts.log. Больше оно нигде не используется.
            return "check successful"
        else:
            # Проверка неуспешна. /login вернет код 3, /account_status вернет код 2
            raise ExternalApiException('check failed')

    def register_account_new(
            self, register_params: RegisterParams, params: TVMiddlewareApiParams, client_play_device: ClientPlayDevice
    ) -> AccountRegisterResponse:
        """Регистрация аккаунта во внешнем биллинге.

        @param register_params: Параметры регистрации.
        @param params: Параметры API.
        @param client_play_device: Тип устройства.

        @return: Результат регистрации.
        """

        response = AccountRegisterResponse()

        """Подтверждает номер телефона, если это необходимо."""
        process = RegisterProcess(params.client, client_play_device, register_params, '')
        process.confirm_registration()

        """После подтверждения номера телефона отправляем запрос во внешний биллинг и получаем ext_id"""
        response.ext_id = self.hydra_api.create_customer(register_params)['customer']['n_subject_id']

        response.abonement = AccountHelper.get_next_abonement(params.client)
        response.status = AccountRegisterResponse.STATUS_NEED_TO_CREATE
        return response

    def customer_assign_nonbasic_tariff(self, customer: Customer, tariff: Tariff, is_free: bool=False):
        """Подключает тариф во внешней системе (используются только дополнительные тарифы).

        @param customer: Объект абонента.
        @param tariff: Объект тарифа.
        @param is_free: Объект тарифа.
        """

        """Получение внешнего id тарифа из смарти"""
        external_id_tariff = tariff.ext_id
        if not external_id_tariff:
            raise ExternalApiException('no external tariff id')

        """Получения внешнего id кастомера из смарти для отправки во внешний биллинг"""
        external_id_customer = customer.ext_id
        if not external_id_customer:
            raise ExternalApiException('no external customer id')

        """Проверяем на наличие тарифа у кастомера"""
        tariff_service = CustomerTariffService(customer)
        if tariff_service.tariff_active_for(tariff):
            raise SmartyBillingErrorTariffAlreadyActive

        """Проверяем баланс кастомера"""
        price = activation_price(tariff, customer)

        if not is_free and customer.balance() < price:
            raise CustomerAssignTariffBalanceError(_("Customer's balance is less than activation price"))

        """Отправляем запрос на подключение тарифа во внешний биллинг"""
        self.hydra_api.create_subscription(external_id_tariff, external_id_customer)
        
        """В случае подключения тарифа во внешнем биллинге подключаем тариф в смарти"""
        SubjectSubscriptionService(customer).subscribe_with_default_parameters(tariff, is_free=is_free)

        return TariffAssignResponse()

    def customer_unassign_nonbasic_tariff(self, customer: Customer, tariff: Tariff):
        """Отключает дополнительный тариф.

        @param customer: Объект абонента.
        @param tariff: Объект тарифа.
        """

        """Получение внешнего id тарифа из смарти"""
        external_id_tariff = tariff.ext_id
        if not external_id_tariff:
            raise ExternalApiException('no external tariff id')

        """Получения внешнего id кастомера из смарти для отправки во внешний биллинг"""
        external_id_customer = customer.ext_id
        if not external_id_customer:
            raise ExternalApiException('no external customer id')

        """Отключаем тариф в внешнем биллинге"""
        self.hydra_api.close_subscription(external_id_tariff, external_id_customer)

        """В случае успешного отключения тарифа во внешнем биллинге отключаем в смарти"""
        crt = SubjectSubscriptionService(customer)
        crt.unsubscribe(tariff)


# регистрация класса api
external_api.registry.add('example_api_client', ExampleApiClient)
