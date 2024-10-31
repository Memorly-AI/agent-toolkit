from crm import CRM
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Odoo connection details
ODOO_URL = os.getenv('ODOO_URL')
ODOO_DB = os.getenv('ODOO_DB')
ODOO_USERNAME = os.getenv('ODOO_USERNAME')
ODOO_KEY = os.getenv('ODOO_KEY')

def test_crm_operations():

    # Initialize CRM
    crm = CRM(ODOO_URL, ODOO_DB, ODOO_KEY, ODOO_USERNAME)
    
    print("\n>>> Testing CRM operations...")

    # Test create lead
    lead_name = f"Test Lead {int(time.time())}"
    lead_email = "testlead@example.com"
    lead_id = crm.create_lead(lead_name, lead_email, phone="1234567890", description="This is a test lead")
    print(f"\n>>> Created lead with ID: {lead_id}")

    # Test search leads
    leads = crm.search_leads([('name', '=', lead_name)], limit=1)
    print(f"\n>>> Found lead: {leads[0] if leads else 'Not found'}")

    # Test update lead
    update_result = crm.update_lead(lead_id, {'description': 'Updated description'})
    print(f"\n>>> Updated lead: {update_result}")

    # Test create opportunity
    opp_name = f"Test Opportunity {int(time.time())}"
    opp_id = crm.create_opportunity(opp_name, lead_id, expected_revenue=1000, probability=50)
    print(f"\n>>> Created opportunity with ID: {opp_id}")

    # Test get lead stages
    stages = crm.get_lead_stages()
    print(f"\n>>> Lead stages: {stages}")

    # Test move lead stage
    if stages:
        move_result = crm.move_lead_stage(lead_id, stages[0]['id'])
        print(f"\n>>> Moved lead to stage: {move_result}")

    # Test create activity
    activity_types = crm.get_activity_types()
    if activity_types:
        activity_id = crm.create_activity(lead_id, activity_types[0]['id'], "Test Activity", "2023-12-31")
        print(f"\n>>> Created activity with ID: {activity_id}")

        # Test get lead activities
        activities = crm.get_lead_activities(lead_id)
        print(f"\n>>> Lead activities: {activities}")

        # Test mark activity as done
        done_result = crm.mark_activity_done(activity_id)
        print(f"\n>>> Marked activity as done: {done_result}")

    print("\n>>> CRM operations test completed.")

if __name__ == "__main__":
    test_crm_operations()