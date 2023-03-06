const MD5 = require("crypto-js/md5");
const querystring = require('node:querystring');
const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

class SmartyContentAPI {
    #baseUrl;
    #clientId;
    #apiKey;
    constructor(baseUrl, clientId, apiKey) {
        this.#baseUrl = baseUrl;
        this.#clientId = clientId;
        this.#apiKey = apiKey;
    }
    #getSignature(requestData) {
        const sortedRequestData = Object.keys(requestData)
            .sort()
            .reduce((sorted, key) => {
                sorted[key] = requestData[key];
                return sorted;
            }, {});
        for (let key in sortedRequestData) {
            if (typeof sortedRequestData[key] == "object") {
                sortedRequestData[key].sort();
            }
        }
        let signSource = querystring.stringify(sortedRequestData, ';', ':', { encodeURIComponent: unescape });

        signSource += ';' + this.#apiKey.toString();
        console.log(signSource);
        return MD5(Buffer.from(signSource).toString('base64')).toString();
    }


    async #apiRequest(path, data) {
        if (data == null) {
            data = {};
        }
        data['client_id'] = this.#clientId;
        data['signature'] = this.#getSignature(data);
        const http = new XMLHttpRequest();
        http.open('POST', this.#baseUrl + path, false);

        http.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8');
        http.responseType = 'json';

        http.send(querystring.stringify(data, '&'));

        http.onload;

        return http.responseText;
    }

    async customerCreate(name, rating, kwargs) {
        let params = {
            'name': name,
            'rating': rating,
            'recording_days': 0
        };
        let fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 'name_lang5',
            'hbb_channel_pid', 'uri', 'url_prefix', 'multicast_address',
            'secondary_multicast_address', 'id_for_stream_service', 'comment',
            'version', 'option1', 'option2', 'option3', 'telemeter_account_name',
            'telemeter_tmsec_name', 'telemeter_cat_id', 'telemeter_vc_id',
            'telemeter_vc_version', 'mediahills_id', 'pause_live_tv_shift', 'lcn_number',
            'recording_days', 'telemeter', 'aspect_ratio', 'show_in_all', 'parent_control',
            'enabled', 'display_on_site', 'category', 'epg_channel', 'copyright_holder',
            'price_category', 'sort_after_cid', 'additional_categories', 'tariffs',
            'stream_services', 'hbb_providers'
        ];

        if (kwargs) {
            for (const [key, value] of Object.entries(kwargs)) {
                if (fields.includes(key)) {
                    params[key] = value;
                }
            }
        }

        try {
            return await this.#apiRequest('content/api/channel/create/', params);
        }
        catch (e) {
            console.error(e);
        }
    }

}

// пример использования класса
(async function() {
    let api = new SmartyContentAPI('your base url', 1, 'top secret');
    console.log(await api.customerCreate('тест', '0'));
    // console.log(await api.tariffList());
    // console.log(await api.accountInfo(590274));
    // console.log(await api.accountCreate(2222));
    // console.log(await api.customerTariffAssignRemove(2222, 1));
    // console.log(await api.customerInfo(2233));
    // console.log(await api.customerCreate({
    //     'firstname': 'ivan',
    //     'lastname': 'ivanov',
    //     'middlename': 'ivanovich',
    //     'comment': 'ochen krasivbli',
    // }));
    // console.log(await api.transactionCreate(2233, 222,undefined, undefined));
    // console.log(await api.transactionDelete(2233, 222));
})();
