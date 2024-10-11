from odoo.utils.jrpc_call import *


class CRM:
    def __init__(self, org_url, db, key, user_name):
        self.api_url = org_url + "/jsonrpc"
        self.db = db
        self.key = key
        self.user_name = user_name


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
        

    def create_lead(self, name, phone):
        api_body = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.db,
                self.get_uid(),
                self.key,
                "res.partner",
                "create",
                [
                    {
                        "name": name,
                        "phone": phone,
                        "category_id": [1]
                    }
                ]
            ]
        }
        api_response = json_rpc(self.api_url, "call", api_body)  
        return api_response
    



# if __name__ == "__main__":
#     org_url = "https://memorly-tech.odoo.com"
#     db = "memorly-tech"
#     key = "758537512665184c100f3fd854d2180ddc565898"
#     crm = CRM(org_url, db, key)
#     crm.get_uid()


