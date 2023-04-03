const axios = require('axios').default;
const MD5 = require("crypto-js/md5");

class SmartyBillingAPI {
    #baseUrl;
    #clientId;
    #apiKey;
    constructor(baseUrl, clientId, apiKey) {
        this.#baseUrl = baseUrl;
        this.#clientId = clientId;
        this.#apiKey = apiKey;
    }
    #getSignature(requestData) {
        let keys = [];
        for (let key in requestData) {
            keys.push(key);
        }
        keys.sort();
        let signSource = "";
        for (let i = 0; i < keys.length; i++) {
            signSource += keys[i].toString() + ':' + requestData[keys[i]] + ';';
        }
        signSource += this.#apiKey.toString();
        return MD5(Buffer.from(signSource).toString('base64')).toString();
    }

    async #apiRequest(path, data) {
        if (data == null) {
            data = {};
        }
        data['client_id'] = this.#clientId;
        data['signature'] = this.#getSignature(data);
        const response = await axios({
            method: 'post',
            url: this.#baseUrl + path,
            headers: {'content-type': 'application/x-www-form-urlencoded'},
            data: data,
        });
        return await response.data;
    }

    async transactionCreate(customerId, transactionId, amount=0, comment='', kwargs) {
        if (kwargs == null) {
            kwargs = {};
        }
        kwargs['customer_id'] = customerId;
        kwargs['id'] = transactionId;
        kwargs['amount'] = amount;
        kwargs['comment'] = comment;
        try {
            return await this.#apiRequest('/billing/api/transaction/create/', kwargs);
        }
        catch (e) {
            console.error(e);
        }
    }

    async transactionDelete(customerId, transactionId) {
        let params = {
            'customer_id': customerId,
            'id': transactionId,
        };
        try {
            return await this.#apiRequest('/billing/api/transaction/delete/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customerCreate(kwargs) {
        let params = {};
        let fields = [
            'firstname', 'middlename', 'lastname', 'birthdate',
            'passport_number', 'passport_series', 'passport_issue_date', 'passport_issued_by',
            'postal_address_street', 'postal_address_bld', 'postal_address_apt',
            'postal_address_zip', 'billing_address_street', 'billing_address_bld',
            'billing_address_apt', 'billing_address_zip',
            'mobile_phone_number', 'phone_number_1', 'phone_number_2', 'fax_phone_number',
            'email', 'company_name', 'comment', 'auto_activation_period',
        ];

        for (const [key, value] of Object.entries(kwargs)) {
            if (fields.includes(key)) {
                params[key] = value;
            }
        }

        let requiredFields = ['firstname', 'lastname', 'middlename', 'comment'];

        for (let i = 0; i < requiredFields.length; i++) {
            if (!(requiredFields[i] in params)) {
                console.error("You must specify firstname or lastname or middlename or comment");
                return;
            }
        }

        try {
            return await this.#apiRequest('/billing/api/customer/create/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customerInfo(customerId) {
        let params = {
            'customer_id': customerId
        };
        try {
            return await this.#apiRequest('/billing/api/customer/info/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customerTariffAssignRemove(customerId, tariffId) {
        let params = {
            'customer_id': customerId,
            'tariff_id': tariffId,
        };
        try {
            return await this.#apiRequest('/billing/api/customer/tariff/assign/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customerTariffRemove(customerId, tariffId) {
        let params = {
            'customer_id': customerId,
            'tariff_id': tariffId,
        };
        try {
            return await this.#apiRequest('/billing/api/customer/tariff/remove/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async accountInfo(abonement, accountId) {
        if (abonement == null && accountId == null) {
            console.error("abonement and accountId is null");
            return;
        }
        let params = {};
        if (abonement != null) {
            params['abonement'] = abonement;
        }
        if (accountId != null) {
            params['account_id'] = accountId;
        }
        try {
            return await this.#apiRequest('/billing/api/account/info/', params);
        }
        catch (e) {
            console.error(e);
        }
    }


    async accountCreate(customerId, autoActivationPeriod) {
        let params = {
            'customer_id': customerId,
        };
        if (autoActivationPeriod != null) {
            params['auto_activation_period'] = autoActivationPeriod
        }
        try {
            return await this.#apiRequest('/billing/api/account/create/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async accountDelete(abonement) {
        let params = {
            'abonement': abonement,
        };
        try {
            return await this.#apiRequest('/billing/api/account/delete/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async accountActivate(abonement) {
        let params = {
            'abonement': abonement,
        };
        try {
            return await this.#apiRequest('/billing/api/account/activate/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async accountDeactivate(abonement) {
        let params = {
            'abonement': abonement,
        };
        try {
            return await this.#apiRequest('/billing/api/account/deactivate/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async tariffList() {
        try {
            return await this.#apiRequest('/billing/api/tariff/list/');
        }
        catch (e){
            console.error(e);
        }
    }
}

// пример использования класса
// (async function() {
//     let api = new SmartyBillingAPI('baseUrl', 1, 'secret_key');
//     // console.log(await api.tariffList());
//     // console.log(await api.accountInfo(590274));
//     // console.log(await api.accountCreate(2222));
//     // console.log(await api.customerTariffAssignRemove(2222, 1));
//     // console.log(await api.customerInfo(2233));
//     // console.log(await api.customerCreate({
//     //     'firstname': 'ivan',
//     //     'lastname': 'ivanov',
//     //     'middlename': 'ivanovich',
//     //     'comment': 'ochen krasivbli',
//     // }));
//     // console.log(await api.transactionCreate(2233, 222,undefined, undefined));
//     // console.log(await api.transactionDelete(2233, 222));
// })();
