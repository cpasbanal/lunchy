

def first_entity_value(entities, entity):
    # find the wanted entity from the wit request
    if not entities:
        return None
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val