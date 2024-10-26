from odoo.utils.jrpc_call import *

class CRM:

    def __init__(self, org_url, db, key, user_name):
        self.api_url = org_url + "/jsonrpc"
        self.db = db
        self.key = key
        self.user_name = user_name
        self.uid = self.get_uid()

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

    def create_lead(self, name, email, phone=None, description=None):
        lead_data = {
            "name": name,
            "email_from": email,
            "phone": phone,
            "description": description,
            "type": "lead"
        }
        return self.execute_kw("crm.lead", "create", [lead_data])

    def update_lead(self, lead_id, values):
        return self.execute_kw("crm.lead", "write", [[lead_id], values])

    def search_leads(self, domain, limit=None):
        return self.execute_kw("crm.lead", "search_read", [domain], {"limit": limit})

    def create_opportunity(self, name, partner_id, expected_revenue=0.0, probability=0):
        opp_data = {
            "name": name,
            "partner_id": partner_id,
            "type": "opportunity",
            "expected_revenue": expected_revenue,
            "probability": probability
        }
        return self.execute_kw("crm.lead", "create", [opp_data])

    def convert_lead_to_opportunity(self, lead_id):
        return self.execute_kw("crm.lead", "convert_opportunity", [[lead_id]])

    def get_lead_stages(self):
        return self.execute_kw("crm.stage", "search_read", [[]])

    def move_lead_stage(self, lead_id, stage_id):
        return self.execute_kw("crm.lead", "write", [[lead_id], {"stage_id": stage_id}])

    def create_activity(self, lead_id, activity_type_id, summary, due_date):
        activity_data = {
            "res_model_id": self.get_model_id("crm.lead"),
            "res_id": lead_id,
            "activity_type_id": activity_type_id,
            "summary": summary,
            "date_deadline": due_date
        }
        return self.execute_kw("mail.activity", "create", [activity_data])

    def get_model_id(self, model_name):
        model_ids = self.execute_kw("ir.model", "search", [[("model", "=", model_name)]])
        return model_ids[0] if model_ids else None

    def get_activity_types(self):
        return self.execute_kw("mail.activity.type", "search_read", [[]])

    def get_lead_activities(self, lead_id):
        domain = [("res_model", "=", "crm.lead"), ("res_id", "=", lead_id)]
        return self.execute_kw("mail.activity", "search_read", [domain])

    def mark_activity_done(self, activity_id):
        return self.execute_kw("mail.activity", "action_done", [[activity_id]])
