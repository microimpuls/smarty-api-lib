
# smarty-billing-api-python
Python library for implement Smarty Billing API client

Использование:
```python
from smarty_billing_api import SmartyBillingAPI
api = SmartyBillingAPI(base_url='http://smarty.microimpuls.com', client_id=42, api_key='secret')

api.tariff_list()
api.customer_info(customer_id=1)
```