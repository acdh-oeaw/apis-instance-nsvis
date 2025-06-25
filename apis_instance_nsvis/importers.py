import logging
import httpx
import base64
import json
from apis_core.generic.importers import GenericModelImporter


class PlaceImporter(GenericModelImporter):
    def request(self, uri):
        if "openstreetmap.org" in uri:
            self.import_uri, b64_data = uri.split("&data=")
            data = json.loads(base64.b64decode(b64_data))
            print(data)
            latitude = data["latitude"]
            longitude = data["longitude"]

            instance = {"label": [data["label"]], "latitude": [latitude], "longitude": [longitude], "relations": {}}

            with httpx.Client() as client:
                for zoom in [5, 8, 10, 12, 13]:
                    uri = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&extratags=1&format=json&zoom={zoom}"
                    res = client.get(uri).json()
                    city = res.get("address", {}).get("city") or res.get("address", {}).get("village")
                    if city and data["city"] in city:
                        if wikidata_id := res.get("extratags", {}).get("wikidata"):
                            logging.debug("Found city %s with wikidata ID %s for instance %s", city, wikidata_id, data["label"])
                            city_uri = f"http://wikidata.org/entity/{wikidata_id}"
                            instance["relations"]["apis_instance_nsvis.locatedin"] = {"curies": [city_uri], "obj": "apis_instance_nsvis.place"}
                        break
            return instance
        return super().request(uri)
