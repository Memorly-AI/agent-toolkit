# CRM Codebase

## Introduction

This document provides a detailed and comprehensive explanation of the CRM codebase provided. The codebase integrates with Odoo's JSON-RPC API to manage CRM activities like creating leads, updating them, and handling opportunities and activities.

## Imports and Logging

```python
import json
import random
import urllib.request
import urllib.error
import logging

logger = logging.getLogger("django")
```

- **json**: Utilized for encoding and decoding JSON data.
- **random**: Used to generate random numbers, particularly for the JSON-RPC `id`.
- **urllib.request** and **urllib.error**: Enables handling HTTP requests and errors.
- **logging**: Logs information to help monitor the activities and spot issues.
- A logger named "django" is initialized to handle logging events.

## Functions for JSON-RPC Communication

### `json_rpc`

```python
def json_rpc(url, method, params):
    data = {
        "jsonrpc": "2.0",
        "method": method.lower(),
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    req = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers={
        "Content-Type": "application/json"
    })
    response = urllib.request.urlopen(req)
    reply = json.loads(response.read().decode('UTF-8'))
    if 'error' in reply:
        logger.error(f"Error: {reply['error']}")
        raise Exception(reply['error'])
    return reply['result']
```

- Constructs a JSON-RPC request with the provided method and parameters.
- Makes an HTTP POST request to the specified API URL.
- Logs errors encountered during the RPC calls and raises exceptions.

### `call`

```python
def call(url, service, method, *args):
    return json_rpc(url, "call", {"service": service, "method": method, "args": args})
```

- Simplifies making JSON-RPC calls by structuring them with a service and method.

### `call_kw`

```python
def call_kw(url, cred, model, method, domain_list, limit):
    return json_rpc(url, "call", {
        "service": "object",
        "method": "execute_kw",
        "args": [*cred, model, method, domain_list, {"limit": limit}]
    })
```

- Facilitates Odoo's `execute_kw` call patterns for filtering data within a domain with an optional limit.

## CRM Class

The `CRM` class centralizes functionalities for interacting with Odoo's CRM system.

### `__init__`

```python
class CRM:
    def __init__(self, org_url, db, key, user_name):
        self.api_url = org_url + "/jsonrpc"
        self.db = db
        self.key = key
        self.user_name = user_name
        self.uid = self.get_uid()
```

- Initializes the CRM instance with API details.
- Authenticates the user and retrieves a unique user ID (`uid`).

### Authentication

```python
def get_uid(self):
    try:
        params = {
            "service": "common",
            "method": "login",
            "args": [self.db, self.user_name, self.key]
        }
        uid = json_rpc(self.api_url, "call", params)
        if uid is None:
            raise Exception("Failed to log in.")
        return uid
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return None
```

- Attempts to log in to the CRM system using user credentials.
- Returns the `uid` upon successful authentication, or logs and returns None if failed.

### CRUD Operations for Leads and Opportunities

- **Create Lead**: `create_lead(self, name, email, phone=None, description=None)`
- **Update Lead**: `update_lead(self, lead_id, values)`
- **Search Leads**: `search_leads(self, domain, limit=None)`
- **Create Opportunity**: `create_opportunity(self, name, partner_id, expected_revenue=0.0, probability=0)`
- **Convert Lead to Opportunity**: `convert_lead_to_opportunity(self, lead_id)`

These methods utilize `execute_kw` to perform create, update, and search operations on CRM leads and opportunities.

### Manage Lead Stages and Activities

- **Get Lead Stages**: `get_lead_stages(self)`
- **Move Lead Stage**: `move_lead_stage(self, lead_id, stage_id)`
- **Create Activity**: `create_activity(self, lead_id, activity_type_id, summary, due_date)`
- **Get Activity Types**: `get_activity_types(self)`
- **Get Lead Activities**: `get_lead_activities(self, lead_id)`
- **Mark Activity Done**: `mark_activity_done(self, activity_id)`

These methods facilitate managing different stages of leads, creating and tracking activities, and marking activities as done.

### Helper Functions

#### `execute_kw`

```python
def execute_kw(self, model, method, args, kwargs=None): 
    try:
        api_body = {
            "service": "object",
            "method": "execute_kw",
            "args": [self.db, self.uid, self.key, model, method, args],
            "kwargs": kwargs or {}  # Handle optional kwargs
        }
        return json_rpc(self.api_url, "call", api_body)
    except Exception as e:
        print(f"API call failed: {str(e)}")
        return None
```

- A helper function that forms the core API call for operations, making it flexible to execute various Odoo model methods.

#### `get_model_id`

```python
def get_model_id(self, model_name):
    model_ids = self.execute_kw("ir.model", "search", [[("model", "=", model_name)]])
    return model_ids[0] if model_ids else None
```

- Searches for and returns the ID of a model based on its name, crucial for activity creation.

## Conclusion

This codebase exemplifies a structured approach to interacting with Odoo's API for managing CRM operations. It leverages Python's standard libraries to effectively handle HTTP requests and JSON communications, encapsulating complex functionalities within the `CRM` class.
