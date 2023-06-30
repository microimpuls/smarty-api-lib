"""
Установка:
1. Поместить файл в директорию Smarty /modules_available.
2. Перезагрузить Smarty.

Использование:
1. В меню Smarty "Интеграция с API внешних систем" создать новую интеграцию.
2. В поле "API handler class" указать созданный класс (в данном примере: "example_api_client").
3. Задать необходимые "Дополнительные атрибуты", которые будут передаваться в __init__ класса (в данном примере: base_url).
4. Сохранить.
"""

import logging
import requests

from urllib.parse import urljoin

import external_api.registry
from billing.api_client import SmartyBilling
from external_api.exceptions import ExternalApiException
from tvmiddleware.api_base import TVMiddlewareApiParams
from tvmiddleware.models import Account


# логи располагаются в /logs/smarty_custom.log
logger = logging.getLogger('smarty_custom')


class ExampleHydraClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, method_url):
        url = urljoin(self.base_url, method_url)
        log_ctx = {'url': url}

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)

            log_ctx.update({
                'status_code': response.status_code,
                'response': response.text
            })

            response.raise_for_status()

            # логирование успешного запроса
            logger.debug('hydra_request', extra={'ctx': log_ctx})

            response = response.json()
        except requests.HTTPError as e:
            # логирование неуспешного запроса
            logger.warning('hydra_request', extra={'ctx': log_ctx})
            return None
        except Exception as e:
            # логирование исключения
            logger.exception('external_billing_request_exception', extra={'ctx': log_ctx})
            # в случае возникновения исключения ExternalApiException метод /login вернет код 3, /account_status вернет код 2
            raise ExternalApiException('unexpected external api error')
        else:
            return response

    def show_customer(self, customer_id):
        method_url = f'/rest/v1/subjects/customers/{customer_id}'
        response = self._request(method_url)
        return response.get('customer')


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
        """Проверка статуса аккаунта во внешнем биллинге. При ошибке проверки нужно кидать исключение ExternalApiException.
        :param account: объект аутентифицированного аккаунта, от лица которого осуществляется запрос к методу /login или /account_status,
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


# регистрация класса api
external_api.registry.add('example_api_client', ExampleApiClient)
