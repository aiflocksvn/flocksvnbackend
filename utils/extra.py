def build_query_string(data: dict) -> str:
    query_params = ""
    for key, value in data.items():
        query_params += f'&{key}={value}'
    return query_params
