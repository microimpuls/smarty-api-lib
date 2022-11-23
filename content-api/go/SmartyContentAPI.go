package SmartyContentAPI

import (
	"crypto/md5"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"sort"
	"time"
)

var base_url string
var client_id int
var api_key string

func _MD5(data string) string {
	h := md5.Sum([]byte(data))
	return fmt.Sprintf("%x", h)
}

func _get_signature(request_data map[string]interface{}, api_key string) string {
	keys := []string{}
	for key := range request_data {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	sign_source := ""
	for _, key := range keys {
		sign_source += fmt.Sprintf("%v:%v;", key, request_data[key])
	}
	sign_source += api_key
	base64_sign_source := base64.StdEncoding.EncodeToString([]byte(sign_source))
	md5_base64_sign_source := _MD5(base64_sign_source)
	return md5_base64_sign_source
}

func _api_request(path string, data map[string]interface{}) string {
	data["client_id"] = client_id
	data["signature"] = _get_signature(data, api_key)

	formdata := url.Values{}
	for key, value := range data {
		formdata.Add(key, fmt.Sprintf("%v", value))
	}
	resp, err := http.PostForm(base_url+path, formdata)
	if err != nil {
		fmt.Printf("%v", err)
	}
	var result map[string]interface{}

	json.NewDecoder(resp.Body).Decode(&result)
	return fmt.Sprintf("%v", result)
}

func _set_params(params map[string]interface{}, fields []string, args map[string]interface{}) {
	var flag bool
	for key, value := range args {
		flag = false
		for _, f_val := range fields {
			if key == f_val {
				flag = true
				break
			}
		}
		if flag {
			params[key] = value
		}
	}
}

func NewApi(new_base_url string, new_client_id int, new_api_key string) {
	base_url = new_base_url
	client_id = new_client_id
	api_key = new_api_key
}

func Video_create(name string, rating int, args map[string]interface{}) string {
	params := map[string]interface{}{
		"name":   name,
		"rating": fmt.Sprintf("%v", rating),
	}
	fields := []string{
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
		"is_announcement",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/video/create/", params)
}

func Videofile_create(name string, vid string, args map[string]interface{}) string {
	params := map[string]interface{}{
		"name": name,
		"vid":  vid,
	}
	fields := []string{
		"episode_id", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
		"name_lang5", "filename", "duration", "is_trailer", "ext_id", "sort_after_vfid",
		"quality",
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/video/file/create/", params)
}

func Video_delete(id int) string {

	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/video/delete/", params)
}

func Video_modify(id int, args map[string]interface{}) string {

	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	fields := []string{
		"load_meta", "kinopoisk_id", "name_lang1", "name_lang2", "name_lang3",
		"name_lang4", "name_lang5", "name_orig", "director", "director_lang1",
		"director_lang2", "director_lang3", "director_lang4", "director_lang5",
		"countries", "countries_lang1", "countries_lang2", "countries_lang3",
		"countries_lang4", "countries_lang5", "description", "description_lang1",
		"description_lang2", "description_lang3", "description_lang4", "description_lang5",
		"year", "poster_url", "screenshot_url", "actors_set", "genres_kinopoisk",
		"kinopoisk_rating", "imdb_rating", "rating", "duration",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/video/modify/", params)
}

func Videofile_modify(id int, args map[string]interface{}) string {

	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	fields := []string{
		"name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
		"name_lang5", "filename", "is_trailer", "duration", "episode_id", "quality",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/video/file/modify/", params)
}

func Season_create(name string, vid string, args map[string]interface{}) string {
	params := map[string]interface{}{
		"name": name,
		"vid":  vid,
	}
	fields := []string{
		"name_lang1", "name_lang2", "name_lang3",
		"name_lang4", "name_lang5", "sort_after_sid",
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/season/create/", params)
}

func Season_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/season/delete/", params)
}

func Season_modify(season_id int, args map[string]interface{}) string {
	params := map[string]interface{}{
		"season_id": fmt.Sprintf("%v", season_id),
	}
	fields := []string{
		"name", "name_lang1", "name_lang2", "name_lang3",
		"name_lang4", "name_lang5", "sort_after_sid",
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/season/modify/", params)
}

func Episode_create(vid string, name string, args map[string]interface{}) string {
	params := map[string]interface{}{
		"vid":  vid,
		"name": name,
	}
	fields := []string{
		"name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
		"description", "description_lang1", "description_lang2", "description_lang3",
		"description_lang4", "description_lang5", "duration", "season_id",
		"sort_after_eid",
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/episode/create/", params)
}

func Episode_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/episode/delete/", params)
}

func Episode_modify(episode_id int, args map[string]interface{}) string {
	params := map[string]interface{}{
		"episode_id": fmt.Sprintf("%v", episode_id),
	}
	fields := []string{
		"name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
		"name_lang5", "description", "description_lang1", "description_lang2",
		"description_lang3", "description_lang4", "description_lang5", "duration",
		"sort_after_eid",
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/episode/modify/", params)
}

func Channel_create(name string, rating int, args map[string]interface{}) string {
	params := map[string]interface{}{
		"name":   name,
		"rating": fmt.Sprintf("%v", rating),
	}
	fields := []string{
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
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/channel/create/", params)
}

func Channel_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/channel/delete/", params)
}

func Seance_create(vid int, date_start time.Time, args map[string]interface{}) string {
	params := map[string]interface{}{
		"vid":        fmt.Sprintf("%v", vid),
		"date_start": fmt.Sprintf(date_start.Format(time.RFC3339)),
	}
	fields := []string{
		"vfid", "date_end",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/seance/create/", params)
}

func Seance_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/seance/delete/", params)
}

func Seance_ticket_create(sid int, args map[string]interface{}) string {
	params := map[string]interface{}{"sid": fmt.Sprintf("%v", sid)}
	fields := []string{"code"}
	_set_params(params, fields, args)
	return _api_request("/content/api/seance/ticket/create/", params)
}

func Seance_ticket_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/seance/ticket/delete/", params)
}

func Radio_create(name string, args map[string]interface{}) string {
	params := map[string]interface{}{"name": name}
	fields := []string{
		"name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
		"enabled", "tariffs", "uri", "description", "description_lang1",
		"description_lang2", "description_lang3", "description_lang4",
		"description_lang5", "radio_channel",
	}

	_set_params(params, fields, args)
	return _api_request("/content/api/radio/create/", params)
}

func Radio_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/radio/delete/", params)
}

func Camera_create(name string, args map[string]interface{}) string {
	params := map[string]interface{}{"name": name}
	fields := []string{
		"name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
		"category", "additional_categories", "enabled", "sort_after_cid", "epg_channel",
		"tariffs", "stream_services", "uri", "url_prefix", "price_category",
		"multicast_address", "secondary_multicast_address", "id_for_stream_service",
		"comment", "option1", "option2", "option3",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/camera/create/", params)
}

func Camera_modify(camera_id int, args map[string]interface{}) string {
	params := map[string]interface{}{"camera_id": fmt.Sprintf("%v", camera_id)}
	fields := []string{
		"name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
		"name_lang5", "enabled", "tariffs", "stream_services", "uri",
		"url_prefix", "multicast_address", "price_category",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/camera/modify/", params)
}

func Camera_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", id)}
	return _api_request("/content/api/camera/delete/", params)
}

func Actor_create(args map[string]interface{}) string {
	params := map[string]interface{}{}
	fields := []string{
		"name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
		"name_lang5", "birthdate", "gender", "country", "country_lang1",
		"country_lang2", "country_lang3", "country_lang4", "country_lang5",
		"profession", "profession_lang1", "profession_lang2", "profession_lang3",
		"profession_lang4", "profession_lang5", "biography", "biography_lang1",
		"biography_lang2", "biography_lang3", "biography_lang4", "biography_lang5",
		"name_orig", "movie_db_id",
	}
	_set_params(params, fields, args)
	return _api_request("/content/api/actor/create/", params)
}

func Actor_delete(id int) string {
	params := map[string]interface{}{"id": fmt.Sprintf("%v", fmt.Sprintf("%v", id))}
	return _api_request("/content/api/actor/delete/", params)
}
