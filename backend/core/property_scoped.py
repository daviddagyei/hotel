class PropertyScoped:
    def filter_by_property(self, query, property_id: int):
        return query.filter_by(property_id=property_id)
