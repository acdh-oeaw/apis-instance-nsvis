import httpx
import json
import base64
from apis_core.utils.autocomplete import ExternalAutocompleteAdapter


class NominatimAutocompleteAdapter(ExternalAutocompleteAdapter):

    def extract(self, feature):
        address = feature.get("address")
        osm_id = f"{feature['osm_type'][0]}{feature['osm_id']}"
        url = f"https://nominatim.openstreetmap.org/lookup?osm_ids={osm_id}"
        result = {
                "id": f"https://nominatim.openstreetmap.org/lookup?osm_ids={osm_id}",
                "latitude": feature.get("lat"),
                "longitude": feature.get("lon"),
                "label": feature.get("display_name"),
                "city": address.get("city") or address.get("suburb") or address.get("village")
        }
        # We are passing some data that is part of the result to the import step
        # using a URI parameter - this way the import step does not have to fetch
        # the data a second time.
        b64_data = base64.b64encode(json.dumps(result).encode()).decode("ascii")
        id = f"{url}&data={b64_data}"
        return {
                "id": id,
                "text": self.get_result_label(result),
                "selected_text": self.get_result_label(result)
        }

    def address_with_housenumber(self, feature):
        """
        Remove results that don't have either a road or a house number
        """
        properties = feature.get("address", {})
        return properties.get("road", False) and properties.get("house_number", False)

    def get_results(self, q, client=httpx.Client()):
        url = f"https://nominatim.openstreetmap.org/search?q={q}&addressdetails=1&format=json"
        try:
            res = client.get(url)
            if res:
                return list(map(self.extract, filter(self.address_with_housenumber, res.json())))
        except:
            pass
        return []
