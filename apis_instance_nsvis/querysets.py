from apis_acdhch_default_settings.querysets import E53_PlaceExternalAutocomplete
from apis_core.utils.autocomplete import ExternalAutocomplete
from apis_instance_nsvis.autocomplete import NominatimAutocompleteAdapter


class PlaceExternalAutocomplete(ExternalAutocomplete):
    adapters = E53_PlaceExternalAutocomplete.adapters + [NominatimAutocompleteAdapter(template="e53_place_from_nominatim_autocomplete_result.html")]
