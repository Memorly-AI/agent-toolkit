# API Body Schema Compiler

Welcome to the API Body Schema Compiler documentation. This tool is designed to help validate, process, and construct API request bodies based on defined schema strings. This detailed document will guide you through the functionalities, the workflow of each component, and provide examples for better understanding.

---

## Overview

This compiler consists of several functions focused on validating, processing, and composing API request bodies according to predefined schemas. The key operations include:

- Validating schema strings.
- Extracting segments enclosed in parentheses.
- Validating parameters within the schema.
- Constructing API request bodies using user-provided inputs.

### Functions

The primary functions included in this compiler are:

- **validate_complete_schema(schema_string)**
- **validate_schema(schema_string)**
- **extract_all_parentheses_segments(schema_string)**
- **extract_parentheses_segments(schema_string)**
- **validate_param(param)**
- **api_body_builder(schema, user_inputs)**

### Usage

This module is dedicated to schema string validation and processing, ultimately facilitating the construction of API request bodies based on valid schemas and user inputs. The main function of interest is `api_body_builder`.

The functions support several data types: String, Number, Boolean, List, and Map.

#### Example Usage

Here's a brief example demonstrating the module's core functionality:

```python
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
            }
        ]
    ])
}'''

user_inputs = {
    "name": "Full Name",
    "phone": "1234567890"
}

result = api_body_builder(schema_string, user_inputs)

# Result will be {'service': 'object', 'method': 'execute_kw', 'args': ['example-db', 2, '123456', 'res.partner', 'create', [{'name': 'Full Name', 'phone': '1234567890', 'category_id': [1]}]]}
```

## Function Descriptions

### 1. validate_complete_schema(schema_string)

This function validates and processes the entire schema string. It ensures the string starts with `{` and ends with `}`. If valid, it strips these braces and extracts segments within parentheses.

#### Parameters
- `schema_string` (str): The string representing the schema to be validated and processed.

#### Returns
- `list`: A list of extracted valid segments.
- `None`: If the string is invalid or an error occurs.

---

### 2. validate_schema(schema_string)

Functionally similar to `validate_complete_schema`, this variant focuses on extracting segments within parentheses if the broad schema string is valid.

#### Parameters
- `schema_string` (str): The schema string for validation and processing.

#### Returns
- `list`: A list of validated and extracted segments.
- `None`: If validation fails or errors occur during processing.

---

### 3. extract_all_parentheses_segments(schema_string)

This function parses the schema to validate and extract all parameters enclosed in parentheses, addressing nested structures like Lists and Maps.

#### Parameters
- `schema_string` (str): The input schema containing segments within parentheses.

#### Returns
- `list`: A structured list of valid segments.

#### Raises
- `ValueError`: On encountering invalid schema segments or mismatched parentheses.

---

### 4. extract_parentheses_segments(schema_string)

This function identifies and validates segments in parentheses, returning both raw and structured segment data.

#### Parameters
- `schema_string` (str): The schema string to process.

#### Returns
- `tuple`: Contains two lists:
  - Validated segment information.
  - Raw segment strings without spaces.

#### Raises
- `ValueError`: For invalid segment structures or unbalanced parentheses.

---

### 5. validate_param(param)

Validates parameters, extracts keys, types, and values, considering three parameter types: static, dynamic, and default.

#### Parameters
- `param` (str): The parameter string for validation.

#### Returns
- `dict`: Includes validation results and extracted details.

---

### 6. api_body_builder(schema, user_inputs)

Builds an API request body as per the schema and input data provided by users. It focuses on parameter validation and integration into a coherent request structure.

#### Parameters
- `schema` (list): A validated schema list.
- `user_inputs` (dict): The user-provided input values.

#### Returns
- `dict`: Represents the completed API request body.

#### Raises
- `ValueError`: For missing dynamic parameters required for request completion.

---

## Author

Developed by Azad Mosarof from the Memorly.AI team, this module is tailored for schema validation and API body composition, ensuring robust interaction with APIs through properly structured requests.
