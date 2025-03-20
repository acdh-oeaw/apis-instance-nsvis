import os

from apis_core.utils.autocomplete import (
    ExternalAutocomplete,
    TypeSenseAutocompleteAdapter,
    LobidAutocompleteAdapter,
)


class E53_PlaceExternalAutocomplete(ExternalAutocomplete):
    adapters = [
        TypeSenseAutocompleteAdapter(
            collections=[
                "prosnet-wikidata-place-index",
                "prosnet-geonames-place-index",
            ],
            token=os.getenv("TYPESENSE_TOKEN", None),
            server=os.getenv("TYPESENSE_SERVER", None),
        ),
        LobidAutocompleteAdapter(
            params={
                "filter": "type:PlaceOrGeographicName",
                "format": "json:preferredName",
            }
        ),
    ]
