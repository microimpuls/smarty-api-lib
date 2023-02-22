import java.io.*;
import java.math.BigInteger;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.Map;
import java.util.TreeMap;

public class SmartyContentAPI {
    private
    String base_url, api_key, client_id;
    public SmartyContentAPI(String base_url_in, String client_id_in, String api_key_in) {
        base_url = base_url_in;
        api_key = api_key_in;
        client_id = client_id_in;
    }
    private String get_signature(TreeMap<String, String> data) {
        String sign_source = "";
        for (Map.Entry<String, String> it: data.entrySet()) {
            sign_source += it.getKey() + ":" + it.getValue() + ";";
        }
        sign_source += api_key;
        String base64_sign = Base64.getEncoder().encodeToString(sign_source.getBytes());
        MessageDigest md5 = null;
        try {
            md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
        md5.update(base64_sign.getBytes(), 0, base64_sign.length());
        return new BigInteger(1, md5.digest()).toString(16);
    }
    private String api_request(String path, TreeMap<String, String> data) {
        StringBuilder ans = new StringBuilder();

        data.put("client_id", client_id);
        data.put("signature", get_signature(data));
        StringBuilder postData = new StringBuilder();
        for (Map.Entry<String,String> param : data.entrySet()) {
            if (postData.length() != 0) postData.append('&');
            try {
                postData.append(URLEncoder.encode(param.getKey(), "UTF-8"));
                postData.append('=');
                postData.append(URLEncoder.encode(param.getValue(), "UTF-8"));
            } catch (UnsupportedEncodingException e) {
                throw new RuntimeException(e);
            }
        }
        byte[] out = new byte[0];
        try {
            out = postData.toString().getBytes("UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }

        URL url;
        HttpURLConnection httpURLConnection;
        OutputStream os = null;
        InputStreamReader isR = null;
        BufferedReader bfR = null;

        try {
            url = new URL(base_url + path);
            httpURLConnection = (HttpURLConnection)url.openConnection();
            httpURLConnection.setRequestMethod("POST");
            httpURLConnection.setDoOutput(true);
            httpURLConnection.setDoInput(true);

            httpURLConnection.setConnectTimeout(1000);
            httpURLConnection.setReadTimeout(1000);
            httpURLConnection.connect();

            try {
                os = httpURLConnection.getOutputStream();
                os.write(out);
            } catch (Exception e) {
                System.err.print(e.getMessage());
            }
            if (HttpURLConnection.HTTP_OK == httpURLConnection.getResponseCode()) {
                isR = new InputStreamReader(httpURLConnection.getInputStream());
                bfR = new BufferedReader(isR);
                String line;
                while ((line=bfR.readLine()) != null) {
                    ans.append(line);
                }
            }

        } catch (IOException e) {
            throw new RuntimeException(e);
        } finally {
            try {
                if (isR != null) {
                    isR.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                if (bfR != null) {
                    bfR.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                if (os != null) {
                    os.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return ans.toString();
    }

    private void set_params(TreeMap<String, String> params, String[] fields, TreeMap<String, String> args) {
        if (args == null) {
            return;
        }
        boolean flag;
        String cur_key;
        for (Map.Entry<String, String> param : args.entrySet()) {
            flag = false;
            cur_key = param.getKey();
            for (String val: fields) {
                if (val == cur_key) {
                    flag = true;
                    break;
                }
            }
            if (flag) {
                params.put(cur_key, param.getValue());
            }
        }
    }

    public String video_create(String name, String rating, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        params.put("rating", rating);
        String[] fields = {
                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5", "name_orig",
                "description", "description_lang1", "description_lang2", "description_lang3",
                "description_lang4", "description_lang5", "year", "countries", "countries_lang1",
                "countries_lang2", "countries_lang3", "countries_lang4", "countries_lang5",
                "director", "director_lang1", "director_lang2", "director_lang3", "director_lang4",
                "director_lang5", "genres_kinopoisk", "uri", "language", "language_lang1",
                "language_lang2", "language_lang3", "language_lang4", "language_lang5", "ext_id",
                "premiere_date", "published_from", "published_to", "copyright_holder",
                "external_api_config", "price_category", "video_provider", "genres", "stream_services",
                "tariffs", "actors_set", "available_on", "package_videos", "kinopoisk_rating",
                "imdb_rating", "average_customers_rating", "duration", "parent_control",
                "is_announcement"
        };
        set_params(params, fields, args);
        return api_request("/content/api/video/create/", params);
    }

    public String videofile_create(String name, String vid, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        params.put("vid", vid);
        String[] fields = {
                "episode_id", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
                "name_lang5", "filename", "duration", "is_trailer", "ext_id", "sort_after_vfid",
                "quality",
        };
        set_params(params, fields, args);
        return api_request("/content/api/video/file/create/", params);
    }

    public String video_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/video/delete/", params);
    }

    public String video_modify(String id, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        String[] fields = {
                "load_meta", "kinopoisk_id", "name_lang1", "name_lang2", "name_lang3",
                "name_lang4", "name_lang5", "name_orig", "director", "director_lang1",
                "director_lang2", "director_lang3", "director_lang4", "director_lang5",
                "countries", "countries_lang1", "countries_lang2", "countries_lang3",
                "countries_lang4", "countries_lang5", "description", "description_lang1",
                "description_lang2", "description_lang3", "description_lang4", "description_lang5",
                "year", "poster_url", "screenshot_url", "actors_set", "genres_kinopoisk",
                "kinopoisk_rating", "imdb_rating", "rating", "duration",
        };
        set_params(params, fields, args);
        return api_request("/content/api/video/modify/", params);
    }

    public String videofile_modify(String id, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        String[] fields = {
                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
                "name_lang5", "filename", "is_trailer", "duration", "episode_id", "quality",
        };
        set_params(params, fields, args);
        return api_request("/content/api/video/file/modify/", params);
    }

    public String season_create(String name, String vid, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        params.put("vid", vid);
        String[] fields = {
                "name_lang1", "name_lang2", "name_lang3",
                "name_lang4", "name_lang5", "sort_after_sid",
        };
        set_params(params, fields, args);
        return api_request("/content/api/season/create/", params);
    }

    public String season_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/season/delete/", params);
    }

    public String season_modify(String season_id, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("season_id", season_id);
        String[] fields = {
                "name", "name_lang1", "name_lang2", "name_lang3",
                "name_lang4", "name_lang5", "sort_after_sid",
        };
        set_params(params, fields, args);
        return api_request("/content/api/season/modify/", params);
    }

    public String episode_create(String vid, String name, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        params.put("vid", vid);
        String[] fields = {
                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
                "description", "description_lang1", "description_lang2", "description_lang3",
                "description_lang4", "description_lang5", "duration", "season_id",
                "sort_after_eid",
        };
        set_params(params, fields, args);
        return api_request("/content/api/episode/create/", params);
    }

    public String episode_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/episode/delete/", params);
    }

    public String episode_modify(String episode_id, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("episode_id", episode_id);
        String[] fields = {
                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
                "name_lang5", "description", "description_lang1", "description_lang2",
                "description_lang3", "description_lang4", "description_lang5", "duration",
                "sort_after_eid",
        };
        set_params(params, fields, args);
        return api_request("/content/api/episode/modify/", params);
    }

    public String channel_create(String name, String rating, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        params.put("rating", rating);
        String[] fields = {
                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
                "hbb_channel_pid", "uri", "url_prefix", "multicast_address",
                "secondary_multicast_address", "id_for_stream_service", "comment",
                "version", "option1", "option2", "option3", "telemeter_account_name",
                "telemeter_tmsec_name", "telemeter_cat_id", "telemeter_vc_id",
                "telemeter_vc_version", "mediahills_id", "pause_live_tv_shift", "lcn_number",
                "recording_days", "telemeter", "aspect_ratio", "show_in_all", "parent_control",
                "enabled", "display_on_site", "category", "epg_channel", "copyright_holder",
                "price_category", "sort_after_cid", "additional_categories", "tariffs",
                "stream_services", "hbb_providers",
        };
        set_params(params, fields, args);
        return api_request("/content/api/channel/create/", params);
    }

    public String channel_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/channel/delete/", params);
    }


    public String seance_create(String vid, String date_start, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("vid", vid);
        params.put("date_start", date_start);
        String[] fields = {
                "vfid", "date_end"
        };
        set_params(params, fields, args);
        return api_request("/content/api/seance/create/", params);
    }


    public String seance_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/seance/delete/", params);
    }

    public String seance_ticket_create(String sid, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("sid", sid);
        String[] fields = {"code"};
        set_params(params, fields, args);
        return api_request("/content/api/seance/ticket/create/", params);
    }

    public String seance_ticket_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/seance/ticket/delete/", params);
    }

    public String radio_create(String name, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        String[] fields = {
                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
                "enabled", "tariffs", "uri", "description", "description_lang1",
                "description_lang2", "description_lang3", "description_lang4",
                "description_lang5", "radio_channel",
        };
        set_params(params, fields, args);
        return api_request("/content/api/radio/create/", params);
    }

    public String radio_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/radio/delete/", params);
    }

    public String camera_create(String name, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("name", name);
        String[] fields = {
                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
                "category", "additional_categories", "enabled", "sort_after_cid", "epg_channel",
                "tariffs", "stream_services", "uri", "url_prefix", "price_category",
                "multicast_address", "secondary_multicast_address", "id_for_stream_service",
                "comment", "option1", "option2", "option3",
        };
        set_params(params, fields, args);
        return api_request("/content/api/camera/create/", params);
    }

    public String camera_modify(String camera_id, TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("camera_id", camera_id);
        String[] fields = {
                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
                "name_lang5", "enabled", "tariffs", "stream_services", "uri",
                "url_prefix", "multicast_address", "price_category",
        };
        set_params(params, fields, args);
        return api_request("/content/api/camera/modify/", params);
    }

    public String camera_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/camera/delete/", params);
    }

    public String actor_create(TreeMap<String, String> args) {
        TreeMap<String, String> params = new TreeMap<>();
        String[] fields = {
                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
                "name_lang5", "birthdate", "gender", "country", "country_lang1",
                "country_lang2", "country_lang3", "country_lang4", "country_lang5",
                "profession", "profession_lang1", "profession_lang2", "profession_lang3",
                "profession_lang4", "profession_lang5", "biography", "biography_lang1",
                "biography_lang2", "biography_lang3", "biography_lang4", "biography_lang5",
                "name_orig", "movie_db_id",
        };
        set_params(params, fields, args);
        return api_request("/content/api/actor/create/", params);
    }

    public String actor_delete(String id) {
        TreeMap<String, String> params = new TreeMap<>();
        params.put("id", id);
        return api_request("/content/api/actor/delete/", params);
    }

}
