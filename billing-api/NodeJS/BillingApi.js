const axios = require('axios').default;
const MD5 = require("crypto-js/md5");

class SmartyBillingAPI {
    #base_url;
    #client_id;
    #api_key;
    constructor(base_url, client_id, api_key) {
        this.#base_url = base_url;
        this.#client_id = client_id;
        this.#api_key = api_key;
    }
    #get_signature(request_data) {
        let keys = [];
        for (let key in request_data) {
            keys.push(key);
        }
        keys.sort();
        let sign_source = "";
        for (let i = 0; i < keys.length; i++) {
            sign_source += keys[i].toString() + ':' + request_data[keys[i]] + ';';
        }
        sign_source += this.#api_key.toString();
        return MD5(Buffer.from(sign_source).toString('base64')).toString();
    }

    async #api_request(path, data) {
        if (data == null) {
            data = {};
        }
        data['client_id'] = this.#client_id;
        data['signature'] = this.#get_signature(data);
        const response = await axios({
            method: 'post',
            url: this.#base_url + path,
            headers: {'content-type': 'application/x-www-form-urlencoded'},
            data: data,
        });
        return await response.data;
    }

    async transaction_create(customer_id, transaction_id, amount=0, comment='', kwargs) {
        if (kwargs == null) {
            kwargs = {};
        }
        kwargs['customer_id'] = customer_id;
        kwargs['id'] = transaction_id;
        kwargs['amount'] = amount;
        kwargs['comment'] = comment;
        try {
            return await this.#api_request('/billing/api/transaction/create/', kwargs);
        }
        catch (e) {
            console.error(e);
        }
    }

    async transaction_delete(customer_id, transaction_id) {
        let params = {
            'customer_id': customer_id,
            'id': transaction_id,
        };
        try {
            return await this.#api_request('/billing/api/transaction/delete/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customer_create(kwargs) {
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

        let required_fields = ['firstname', 'lastname', 'middlename', 'comment'];

        for (let i = 0; i < required_fields.length; i++) {
            if (!(required_fields[i] in params)) {
                console.error("You must specify firstname or lastname or middlename or comment");
                return;
            }
        }

        try {
            return await this.#api_request('/billing/api/customer/create/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customer_info(customer_id) {
        let params = {
            'customer_id': customer_id
        };
        try {
            return await this.#api_request('/billing/api/customer/info/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customer_tariff_assign(customer_id, tariff_id) {
        let params = {
            'customer_id': customer_id,
            'tariff_id': tariff_id,
        };
        try {
            return await this.#api_request('/billing/api/customer/tariff/assign/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async customer_tariff_remove(customer_id, tariff_id) {
        let params = {
            'customer_id': customer_id,
            'tariff_id': tariff_id,
        };
        try {
            return await this.#api_request('/billing/api/customer/tariff/remove/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async account_info(abonement, account_id) {
        if (abonement == null && account_id == null) {
            console.error("abonement and account_id is null");
            return;
        }
        let params = {};
        if (abonement != null) {
            params['abonement'] = abonement;
        }
        if (account_id != null) {
            params['account_id'] = account_id;
        }
        try {
            return await this.#api_request('/billing/api/account/info/', params);
        }
        catch (e) {
            console.error(e);
        }
    }


    async account_create(customer_id, auto_activation_period) {
        let params = {
            'customer_id': customer_id,
        };
        if (auto_activation_period != null) {
            params['auto_activation_period'] = auto_activation_period
        }
        try {
            return await this.#api_request('/billing/api/account/create/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async account_delete(abonement) {
        let params = {
            'abonement': abonement,
        };
        try {
            return await this.#api_request('/billing/api/account/delete/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async account_activate(abonement) {
        let params = {
            'abonement': abonement,
        };
        try {
            return await this.#api_request('/billing/api/account/activate/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async account_deactivate(abonement) {
        let params = {
            'abonement': abonement,
        };
        try {
            return await this.#api_request('/billing/api/account/deactivate/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

    async tariff_list() {
        try {
            return await this.#api_request('/billing/api/tariff/list/');
        }
        catch (e){
            console.error(e);
        }
    }
}

// пример использования класса
// (async function() {
//     let api = new SmartyBillingAPI('base_url', 1, 'secret_key');
//     // console.log(await api.tariff_list());
//     // console.log(await api.account_info(590274));
//     // console.log(await api.account_create(2222));
//     // console.log(await api.customer_tariff_assign(2222, 1));
//     // console.log(await api.customer_info(2233));
//     // console.log(await api.customer_create({
//     //     'firstname': 'ivan',
//     //     'lastname': 'ivanov',
//     //     'middlename': 'ivanovich',
//     //     'comment': 'ochen krasivbli',
//     // }));
//     // console.log(await api.transaction_create(2233, 222,undefined, undefined));
//     // console.log(await api.transaction_delete(2233, 222));
// })();
