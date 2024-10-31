"""
    API Body Schema Compiler
    This compiler provides a set of functions to validate, process, and build API request bodies based on schema strings. 
    It includes functions to validate schema strings, extract segments enclosed in parentheses, validate parameters, 
    and construct API request bodies using user inputs.
    Functions:
        - validate_complete_schema(schema_string): Validates and processes a complete schema string.
        - validate_schema(schema_string): Validates and processes a schema string.
        - extract_all_parentheses_segments(schema_string): Extracts and validates all segments enclosed in parentheses from a schema string.
        - extract_parentheses_segments(schema_string): Extracts and validates segments enclosed in parentheses from a schema string.
        - validate_param(param): Validates a parameter string and extracts its key, type, and value.
        - api_body_builder(schema, user_inputs): Constructs an API request body based on a given schema and user inputs.
    Usage:
        This module is designed to be used for validating and processing schema strings, and constructing API request bodies 
        based on the validated schema and user inputs. The main function to use is `api_body_builder`, which takes a schema 
        and user inputs, and returns a constructed API request body.

        Supported Data Types: String, Number, Boolean, List, Map

        Example:
        schema_string = '''{
            ("service" = "object"),
            ("method" = "execute_kw"),
            ("args" = [ 
                "example-db",
                2,
                "123456",
                "res.partner",
                "create",
                [
                    {
                        ("name": String),
                        ("phone": String),
                        ("category_id" = [1])
                ]
            ])
        }'''
        user_inputs = {
            "name": "John Doe",
            "phone": "1234567890"
        }
        result = api_body_builder(schema_string, user_inputs)
        # result will be {'service': 'object', 'method': 'execute_kw', 'args': ['example-db', 2, '123456', 'res.partner', 'create', [{'name': 'John Doe', 'phone': '1234567890', 'category_id': [1]}]]}
    Author:
        This compiler was developed by Azad Mosarof from Memorly.ai team.
"""

def validate_complete_schema(schema_string):
    """
    Validates and processes a schema string.

    This function takes a schema string, strips any leading and trailing whitespace,
    and checks if it starts with '{' and ends with '}'. If the schema string is valid,
    it removes the outermost curly braces and extracts all segments enclosed in parentheses.

    Args:
        schema_string (str): The schema string to be validated and processed.

    Returns:
        list: A list of segments extracted from the schema string if valid.
        None: If the schema string is not valid or an error occurs during processing.

    Raises:
        ValueError: If the schema string does not start with '{' or end with '}'.
    """
    try:
        schema_string = schema_string.strip()
        if schema_string.startswith('{') and schema_string.endswith('}'):
            schema_string = schema_string[1:-1]
        else:
            raise ValueError("Not valid schema")
        segments = extract_all_parentheses_segments(schema_string)
        return segments
    except Exception as e:
        return None
    

def validate_schema(schema_string):
    """
    Validates and processes a schema string.

    This function takes a schema string, strips any leading or trailing whitespace,
    and checks if it starts with '{' and ends with '}'. If the schema string is valid,
    it removes the outermost curly braces and extracts segments within parentheses.

    Args:
        schema_string (str): The schema string to be validated and processed.

    Returns:
        list: A list of segments extracted from the schema string if valid.
        None: If the schema string is not valid or an error occurs during processing.

    Raises:
        ValueError: If the schema string does not start with '{' or end with '}'.
    """
    try:
        schema_string = schema_string.strip()
        if schema_string.startswith('{') and schema_string.endswith('}'):
            schema_string = schema_string[1:-1]
        else:
            raise ValueError("Not valid schema")
        segments, _ = extract_parentheses_segments(schema_string)
        return segments
    except Exception as e:
        return None


def extract_all_parentheses_segments(schema_string):
    """
    Extracts and validates all segments enclosed in parentheses from a given schema string.
    This function processes a schema string to identify and extract segments enclosed in parentheses.
    It ensures that the segments are valid according to the `validate_param` function. If a segment
    is invalid, a ValueError is raised. The function also handles nested structures such as Maps and Lists.
    Args:
        schema_string (str): The schema string containing segments enclosed in parentheses.
    Returns:
        list: A list of dictionaries containing information about each valid segment.
    Raises:
        ValueError: If the schema string contains invalid segments or mismatched parentheses.
    """
    count = 0
    segment = ''
    segments = []
    inside_parentheses = False
    inside_double_quotation = False
    
    for char in schema_string:
        if char == '"':
            inside_double_quotation = not inside_double_quotation
        
        if char == '(' and not inside_double_quotation:
            if count == 0:
                inside_parentheses = True
            count += 1
        
        if inside_parentheses:
            segment += char
        
        if char == ')' and not inside_double_quotation:
            count -= 1
            if count == 0:
                param = segment.replace(' ', '')
                param = param[1:-1]
                param_info = validate_param(param)
                if not param_info["is_valid"]:
                    raise ValueError("Not a valid schema")
                segments.append(param_info)
                segment = ''
                inside_parentheses = False
                if param_info['data_type'] == "Map":
                    segments.extend(extract_all_parentheses_segments(param_info['value']))
                if param_info['data_type'] == "List" and (param_info['param_type'] == "static" or param_info['param_type'] == "default"):
                    temp = extract_all_parentheses_segments(param_info['value'][1:-1])
                    segments.extend(temp)
    
    if count != 0 or segment != '' or inside_parentheses:
        raise ValueError("Not a valid schema")
    return segments


def extract_parentheses_segments(schema_string):
    """
    Extracts and validates segments enclosed in parentheses from a given schema string.
    This function processes a schema string to identify and extract segments that are enclosed
    in parentheses. It also validates these segments to ensure they conform to a specific schema.
    Args:
        schema_string (str): The input schema string containing segments enclosed in parentheses.
    Returns:
        tuple: A tuple containing two lists:
            - segments (list): A list of dictionaries containing validated segment information.
            - _segments (list): A list of raw segments as strings, with spaces removed.
    Raises:
        ValueError: If the schema string contains unbalanced parentheses or invalid segments.
    """
    count = 0
    segment = ''
    segments = []
    _segments = []
    inside_parentheses = False
    inside_double_quotation = False
    
    for char in schema_string:
        if char == '"':
            inside_double_quotation = not inside_double_quotation
        
        if char == '(' and not inside_double_quotation:
            if count == 0:
                inside_parentheses = True
            count += 1
        
        if inside_parentheses:
            segment += char
        
        if char == ')' and not inside_double_quotation:
            count -= 1
            if count == 0:
                param = segment.replace(' ', '')
                _segments.append(param)
                param = param[1:-1]
                param_info = validate_param(param)
                if not param_info["is_valid"]:
                    raise ValueError("Not a valid schema")
                segments.append(param_info)
                segment = ''
                inside_parentheses = False
    
    if count != 0 or segment != '' or inside_parentheses:
        raise ValueError("Not a valid schema")
    return segments, _segments


def validate_param(param):
    """
    Validates a parameter string and extracts its key, type, and value.
    Args:
        param (str): The parameter string to validate. The string should be in the format:
            '"key"=value' for static parameters,
            '"key":data_type' for dynamic parameters, or
            '"key":data_type=default_value' for default parameters.
    Returns:
        dict: A dictionary containing the validation result and extracted information:
            - "is_valid" (bool): Indicates if the parameter is valid.
            - "data_type" (str): The data type of the parameter (e.g., "Number", "String", "List", "Map", "Boolean").
            - "param_type" (str): The type of the parameter ("static", "dynamic", or "default").
            - "key" (str): The key of the parameter.
            - "value" (any): The value of the parameter, which can be a string, number, boolean, list, or map.
    """
    if param[0] != '"' or param[1].isdigit():
        return {"is_valid": False}
    
    data_types = ["Number", "String", "List", "Map", "Boolean", "List[String]", "List[Number]", "List[Boolean]"]
    data_type = ""
    param_type = ""
    key = '"'
    valid_key = False
    param_value = None
    
    for i in range(1, len(param)):
        if not valid_key:
            if param[i] != '"':
                key += param[i]
            else:
                if len(key) == 1:
                    return {"is_valid": False}
                key += param[i]
                valid_key = True
        else:
            _param = param.replace(key, '', 1)
            if _param[0] not in [':', '=']:
                return {"is_valid": False}
            
            if _param[0] == "=":
                # static param
                value = _param[1:]
                if value.startswith('"') and value.endswith('"'):
                    data_type = "String"
                    param_value = value[1:-1]
                elif value.startswith('{') and value.endswith('}'):
                    data_type = "Map"
                    param_value = value
                elif value.startswith('[') and value.endswith(']'):
                    data_type = "List"
                    param_value = value
                elif value in ["true", "false"]:
                    data_type = "Boolean"
                    param_value = value.lower() == "true"
                elif value.replace('.', '', 1).isdigit():
                    data_type = "Number"
                    param_value = float(value) if '.' in value else int(value)
                else:
                    return {"is_valid": False}
                param_type = "static"
                break
            else:
                __param = _param[1:]
                if __param in data_types:
                    # dynamic param
                    data_type = __param
                    param_type = "dynamic"
                    break
                else:
                    # default param
                    if __param.split("=")[0] not in data_types:
                        return {"is_valid": False}
                    data_type = __param.split("=")[0]
                    param_value = __param.split("=")[1]
                    if param_value.startswith('"') and param_value.endswith('"') or param_value.startswith('[') and param_value.endswith(']') or param_value.startswith('{') and param_value.endswith('}'):
                        param_value = param_value[1:-1]
                        
                    if data_type == "String":
                        param_value = str(param_value)
                    elif data_type == "Number":
                        param_value = float(param_value) if '.' in param_value else int(param_value)
                    elif data_type == "Boolean":
                        param_value = param_value.lower() == "true"
                    param_type = "default"
                    break
    
    return {
        "is_valid": True,
        "data_type": data_type,
        "param_type": param_type,
        "key": key[1:-1],
        "value": param_value
    }


def api_body_builder(schema, user_inputs):
    """
    Constructs an API request body based on a given schema and user inputs.
    Args:
        schema (list): A list of dictionaries representing the schema of the API request body.
                       Each dictionary contains keys such as 'param_type', 'key', 'value', and 'data_type'.
        user_inputs (dict): A dictionary containing user-provided values for dynamic parameters.
    Returns:
        dict: A dictionary representing the constructed API request body.
    Raises:
        ValueError: If a required dynamic parameter is missing from user_inputs.
    The function follows these steps:
    1. Validates the provided schema.
    2. Defines helper functions to extract and process different data types (strings, numbers, booleans, lists, maps).
    3. Recursively builds the API request body by processing each parameter in the schema.
    Helper Functions:
        - build_value(param): Determines the value of a parameter based on its type (static, dynamic, default).
        - get_string_items(value): Extracts string items from a given value.
        - get_number_items(value): Extracts number items from a given value.
        - get_boolean_items(value): Extracts boolean items from a given value.
        - get_list_items(value): Extracts list items from a given value.
        - get_map_items(value): Extracts map items from a given value.
        - process_list(value): Processes a list value and returns a new list with processed items.
        - build_recursive(params): Recursively builds a dictionary from the given parameters.
    Example:
        schema = {
            ("id" = 1),   # Static parameter
            ("name": String = "example_name"), # Default parameter
            ("age": Number) # Dynamic parameter
        }
        user_inputs = {
            "age": 25
        }
        result = api_body_builder(schema, user_inputs)
        # result will be {'name': 'example_name', 'age': 25}
    """
    schema = validate_schema(schema)
    def build_value(param):
        if param['param_type'] == 'static':
            return param['value']
        elif param['param_type'] == 'dynamic':
            if param['key'] in user_inputs:
                return user_inputs[param['key']]
            else:
                raise ValueError(f"Missing value for dynamic parameter: {param['key']}")
        elif param['param_type'] == 'default':
            if param['key'] in user_inputs:
                return user_inputs[param['key']]
            else:
                return param['value']
            
    
    def get_string_items(value):
        items = []
        inside_double_quotation = False
        inside_list = False
        bracket_count = 0
        inside_map = False
        brace_count = 0
        first_brace = False
        first_brace_count = 0
        item = ''
        index = 0
        start_index = -1

        for char in value:
            index += 1
            if char == '[': 
                if not inside_double_quotation and not inside_map:
                    inside_list = True
                    bracket_count += 1
            elif char == ']':
                if not inside_double_quotation:
                    bracket_count -= 1
                    if bracket_count == 0:
                        inside_list = False

            if char == '{':
                if not inside_double_quotation and not inside_list:
                    inside_map = True
                    brace_count += 1
            elif char == '}':
                if not inside_double_quotation and not inside_list:
                    brace_count -= 1
                    if brace_count == 0:
                        inside_map = False

            if char == '(':
                if not inside_double_quotation and not inside_list and not inside_map:
                    first_brace = True
                    first_brace_count += 1
            elif char == ')':
                if not inside_double_quotation and not inside_list and not inside_map:
                    first_brace_count -= 1
                    if first_brace_count == 0:
                        first_brace = False

            if char == '"' and not inside_double_quotation and not inside_list and not inside_map and not first_brace:
                inside_double_quotation = True
                continue
            elif char == '"' and inside_double_quotation and not inside_list and not inside_map:
                inside_double_quotation = False
                if not inside_list:
                    items.append({
                        "start_index": start_index,
                        "end_index": index,
                        "item": item,
                        "data_type": "String"
                    })
                    item = ''
                    start_index = -1
                    
            if inside_double_quotation and not inside_list and not inside_map:
                item += char
                if start_index == -1:
                    start_index = index

        return items
    

    def get_number_items(value):
        items = []
        item = ''
        find_number = False
        inside_double_quotation = False
        inside_list = False
        bracket_count = 0
        inside_map = False
        brace_count = 0
        index = 0
        start_index = -1

        for char in value:
            index += 1
            if char == '[': 
                if not inside_double_quotation and not inside_map:
                    inside_list = True
                    bracket_count += 1
            elif char == ']':
                if not inside_double_quotation:
                    bracket_count -= 1
                    if bracket_count == 0:
                        inside_list = False

            if char == '{':
                if not inside_double_quotation and not inside_list:
                    inside_map = True
                    brace_count += 1
            elif char == '}':
                if not inside_double_quotation and not inside_list:
                    brace_count -= 1
                    if brace_count == 0:
                        inside_map = False

            if char == '"':
                if not inside_double_quotation:
                    inside_double_quotation = True
                    continue
                else:
                    inside_double_quotation = False

            if inside_double_quotation or inside_list or inside_map:
                continue
            
            if char.isdigit() or char == '.':
                find_number = True
                item += char
                if start_index == -1:
                    start_index = index

                if index == len(value):
                    items.append({
                        "start_index": start_index,
                        "end_index": index,
                        "item": float(item) if '.' in item else int(item),
                        "data_type": "Number"
                    })
            else:
                if find_number and item != '.' and item != '':
                    items.append({
                        "start_index": start_index,
                        "end_index": index,
                        "item": float(item) if '.' in item else int(item),
                        "data_type": "Number"
                    })
                    item = ''
                    start_index = -1
                    find_number = False
        return items
    

    def get_boolean_items(value):
        items = []
        item = ''
        inside_double_quotation = False
        inside_list = False
        bracket_count = 0
        inside_map = False
        brace_count = 0
        index = 0
        start_index = -1

        for char in value:
            index += 1
            if char == '[': 
                if not inside_double_quotation and not inside_map:
                    inside_list = True
                    bracket_count += 1
            elif char == ']':
                if not inside_double_quotation:
                    bracket_count -= 1
                    if bracket_count == 0:
                        inside_list = False

            if char == '{':
                if not inside_double_quotation and not inside_list:
                    inside_map = True
                    brace_count += 1
            elif char == '}':
                if not inside_double_quotation and not inside_list:
                    brace_count -= 1
                    if brace_count == 0:
                        inside_map = False

            if char == '"':
                if not inside_double_quotation:
                    inside_double_quotation = True
                    continue
                else:
                    inside_double_quotation = False

            if inside_double_quotation or inside_list or inside_map:
                continue
            
            if char.isalpha():
                item += char
                if start_index == -1:
                    start_index = index

                if index == len(value):
                    if item.lower() == 'true' or item.lower() == 'false':
                        items.append({
                            "start_index": start_index,
                            "end_index": index,
                            "item": item.lower() == 'true',
                            "data_type": "Boolean"
                        })
            else:
                if item.lower() == 'true' or item.lower() == 'false':
                    items.append({
                        "start_index": start_index,
                        "end_index": index,
                        "item": item.lower() == 'true',
                        "data_type": "Boolean"
                    })
                start_index = -1
                item = ''
        return items
    

    def get_list_items(value):
        items = []
        item = ''
        inside_double_quotation = False
        inside_list = False
        second_bracket_count = 0
        bracket_count = 0
        index = 0
        start_index = -1

        for char in value:
            index += 1
            if char == '{':
                if not inside_double_quotation:
                    second_bracket_count += 1
            elif char == '}':
                if not inside_double_quotation:
                    second_bracket_count -= 1

            if char == '"':
                if not inside_double_quotation:
                    inside_double_quotation = True
                else:
                    inside_double_quotation = False

            if char == '[': 
                if not inside_double_quotation and second_bracket_count == 0:
                    inside_list = True
                    bracket_count += 1
            elif char == ']':
                if not inside_double_quotation and second_bracket_count == 0:
                    bracket_count -= 1
                    if bracket_count == 0:
                        inside_list = False
                        items.append({
                            "start_index": start_index,
                            "end_index": index,
                            "item": item+char,
                            "data_type": "List"
                        })
                        item = ''
                        start_index = -1

            if inside_list:
                item += char
                if start_index == -1:
                    start_index = index
        return items
    

    def get_map_items(value):
        items = []
        item = ''
        inside_double_quotation = False
        inside_map = False
        third_bracket_count = 0
        bracket_count = 0
        index = 0
        start_index = -1

        for char in value:
            index += 1
            if char == '[':
                if not inside_double_quotation:
                    third_bracket_count += 1
            elif char == ']':
                if not inside_double_quotation:
                    third_bracket_count -= 1

            if char == '"':
                if not inside_double_quotation:
                    inside_double_quotation = True
                else:
                    inside_double_quotation = False

            if char == '{': 
                if not inside_double_quotation and third_bracket_count == 0:
                    inside_map = True
                    bracket_count += 1
            elif char == '}':
                if not inside_double_quotation and third_bracket_count == 0:
                    bracket_count -= 1
                    if bracket_count == 0:
                        inside_map = False
                        items.append({
                            "start_index": start_index,
                            "end_index": index,
                            "item": item+char,
                            "data_type": "Map"
                        })
                        item = ''
                        start_index = -1

            if inside_map:
                item += char
                if start_index == -1:
                    start_index = index
        return items


    def process_list(value):
        new_list = []
        value = value[1:-1]
        
        string_items = get_string_items(value)
        number_items = get_number_items(value)
        boolean_items = get_boolean_items(value)
        list_items = get_list_items(value)
        map_items = get_map_items(value)
        all_items = string_items + number_items + boolean_items + list_items + map_items
        all_items = sorted(all_items, key=lambda x: x['start_index'])

        for item in all_items:
            if item['data_type'] == 'List':
                new_list.append(process_list(item.get('item')))
            elif item['data_type'] == 'Map':
                new_list.append(build_recursive(extract_parentheses_segments(item.get('item')[1:-1])[0]))
            else:
                new_list.append(item.get('item'))

        _, _segments = extract_parentheses_segments(value)
        lsk = []
        for _segment in _segments:
            flag = False
            for item in list_items + map_items:
                if _segment in item.get('item'):
                    flag = True
                    break

            if not flag:
                lsk.append(_segment)

        for item in lsk:
            new_list.append(build_value(validate_param(item[1:-1])))
            
        return new_list


    def build_recursive(params):
        result = {}
        for param in params:
            if param['data_type'] == 'Map':
                result[param['key']] = build_recursive(extract_parentheses_segments(param['value'][1:-1])[0])
            elif param['data_type'] == 'List':
                if param['param_type'] == 'static' or param['param_type'] == 'default':
                    result[param['key']] = process_list(param['value'])
                else:
                    result[param['key']] = build_value(param)
            else:
                result[param['key']] = build_value(param)
        return result


    return build_recursive(schema)

