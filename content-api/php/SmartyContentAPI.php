<?php
	class SmartyContentAPI {
		private $base_url, $client_id, $api_key;

		public function __construct($base_url, $client_id, $api_key) {
			$this->base_url = $base_url;
			$this->client_id = $client_id;
			$this->api_key = $api_key;
		}

		private function get_signature($data) {
			$size = count($data);
			ksort($data);
			$sign_source = "";
			foreach ($data as $key => $value) {
				$sign_source .= $key . ":" . $value . ";";
			}
			$sign_source .= $this->api_key;
			$base64_sign_source = base64_encode($sign_source);
			$md5_base64_sign_source = md5($base64_sign_source);
			return $md5_base64_sign_source;
		}

		private function api_request($path, $data) {
			$data["client_id"] = $this->client_id;
			$data["signature"] = $this->get_signature($data);
			$ch = curl_init($this->base_url.$path);
			curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
			curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
			$html = curl_exec($ch);
			return $html;
		}

		private function set_params(&$params, $fields, $args) {
			if ($args != NULL) {
				foreach ($args as $key => $value) {
					if (in_array($key, $fields)) {
						$params[$key] = $value;
					}
				}
			}
		}

		public function video_create($name, $rating, $args) {
	        $params = [];
            $params["name"] = $name;
            $params["rating"] = $rating;
	        $fields = [
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
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/video/create/", $params);
	    }
	    public function videofile_create($name, $vid, $args) {
	        $params["name"] = $name;
	        $params["vid"] = $vid;
	        $fields = [
	                "episode_id", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
	                "name_lang5", "filename", "duration", "is_trailer", "ext_id", "sort_after_vfid",
	                "quality",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/video/file/create/", $params);
	    }

	    public function video_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/video/delete/", $params);
	    }

	    public function video_modify($id, $args) {
	        $params["id"] = $id;
	        $fields = [
	                "load_meta", "kinopoisk_id", "name_lang1", "name_lang2", "name_lang3",
	                "name_lang4", "name_lang5", "name_orig", "director", "director_lang1",
	                "director_lang2", "director_lang3", "director_lang4", "director_lang5",
	                "countries", "countries_lang1", "countries_lang2", "countries_lang3",
	                "countries_lang4", "countries_lang5", "description", "description_lang1",
	                "description_lang2", "description_lang3", "description_lang4", "description_lang5",
	                "year", "poster_url", "screenshot_url", "actors_set", "genres_kinopoisk",
	                "kinopoisk_rating", "imdb_rating", "rating", "duration",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/video/modify/", $params);
	    }

	    public function videofile_modify($id, $args) {
	        $params["id"] = $id;
	        $fields = [
	                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
	                "name_lang5", "filename", "is_trailer", "duration", "episode_id", "quality",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/video/file/modify/", $params);
	    }

	    public function season_create($name, $vid, $args) {
	        $params["name"] = $name;
	        $params["vid"] = $vid;
	        $fields = [
	                "name_lang1", "name_lang2", "name_lang3",
	                "name_lang4", "name_lang5", "sort_after_sid",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/season/create/", $params);
	    }

	    public function season_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/season/delete/", $params);
	    }

	    public function season_modify($season_id, $args) {
	        $params["season_id"] = $season_id;
	        $fields = [
	                "name", "name_lang1", "name_lang2", "name_lang3",
	                "name_lang4", "name_lang5", "sort_after_sid",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/season/modify/", $params);
	    }

	    public function episode_create($vid, $name, $args) {
	        $params["name"] = $name;
	        $params["vid"] = $vid;
	        $fields = [
	                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
	                "description", "description_lang1", "description_lang2", "description_lang3",
	                "description_lang4", "description_lang5", "duration", "season_id",
	                "sort_after_eid",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/episode/create/", $params);
	    }

	    public function episode_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/episode/delete/", $params);
	    }

	    public function episode_modify($episode_id, $args) {
	        $parans["episode_id"] = $episode_id;
	        $fields = [
	                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
	                "name_lang5", "description", "description_lang1", "description_lang2",
	                "description_lang3", "description_lang4", "description_lang5", "duration",
	                "sort_after_eid",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/episode/modify/", $params);
	    }

	    public function channel_create($name, $rating, $args) {
	        $params["name"] = $name;
	        $parans["rating"] = $rating;
	        $fields = [
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
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/channel/create/", $params);
	    }

	    public function channel_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/channel/delete/", $params);
	    }

	    public function seance_create($vid, $date_start, $args) {
	        $params["vid"] = $vid;
	        $params["date_start"] = $date_start;
	        $fields = [
	                "vfid", "date_end",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/seance/create/", $params);
	    }

	    public function seance_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/seance/delete/", $params);
	    }

	    public function seance_ticket_create($sid, $args) {
	        $params["sid"] = $sid;
	        $fields = ["code"];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/seance/ticket/create/", $params);
	    }

	    public function seance_ticket_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/seance/ticket/delete/", $params);
	    }

	    public function radio_create($name, $args) {
	        $params["name"] = $name;
	        $fields = [
	                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
	                "enabled", "tariffs", "uri", "description", "description_lang1",
	                "description_lang2", "description_lang3", "description_lang4",
	                "description_lang5", "radio_channel",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/radio/create/", $params);
	    }

	    public function radio_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/radio/delete/", $params);
	    }

	    public function camera_create($name, $args) {
	        $params["name"] = $name;
	        $fields = [
	                "name_lang1", "name_lang2", "name_lang3", "name_lang4", "name_lang5",
	                "category", "additional_categories", "enabled", "sort_after_cid", "epg_channel",
	                "tariffs", "stream_services", "uri", "url_prefix", "price_category",
	                "multicast_address", "secondary_multicast_address", "id_for_stream_service",
	                "comment", "option1", "option2", "option3",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/camera/create/", $params);
	    }

	    public function camera_modify($camera_id, $args) {
	        $params["camera_id"] = $camera_id;
	        $fields = [
	                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
	                "name_lang5", "enabled", "tariffs", "stream_services", "uri",
	                "url_prefix", "multicast_address", "price_category",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/camera/modify/", $params);
	    }

	    public function camera_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/camera/delete/", $params);
	    }

	    public function actor_create($args) {
	        $fields = [
	                "name", "name_lang1", "name_lang2", "name_lang3", "name_lang4",
	                "name_lang5", "birthdate", "gender", "country", "country_lang1",
	                "country_lang2", "country_lang3", "country_lang4", "country_lang5",
	                "profession", "profession_lang1", "profession_lang2", "profession_lang3",
	                "profession_lang4", "profession_lang5", "biography", "biography_lang1",
	                "biography_lang2", "biography_lang3", "biography_lang4", "biography_lang5",
	                "name_orig", "movie_db_id",
	        ];
	        $this->set_params($params, $fields, $args);
	        return $this->api_request("/content/api/actor/create/", $params);
	    }

	    public function actor_delete($id) {
	        $params["id"] = $id;
	        return $this->api_request("/content/api/actor/delete/", $params);
	    }
	}
	/*
	$data = ["date_end" => "2012-01-01T12:00:00"];
	$api = new SmartyContentAPI("http://176.28.64.92/", 1, "top secret");
	print_r($api->seance_create("316346", "2010-01-01T12:00:00", $data));
	*/
?>
