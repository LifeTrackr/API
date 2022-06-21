from api import models
from api.utils.caching_query import FromCache


class CompanionTypeCache:
    def __init__(self, db):
        self._companion_types = {}
        self._db = db
        self._get_types()
        print(self._companion_types)

    def __getitem__(self, item):
        return self._companion_types[item]

    def __setitem__(self, key, value):
        self._companion_types[key] = value

    def _get_types(self):
        with self._db() as session:
            companion_types = session.query(models.CompanionTypes).options(FromCache("default")).all()
        for comp_type in companion_types:
            self.__setitem__(comp_type.id, comp_type.type_name)
