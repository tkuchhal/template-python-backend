import requests
import json


class WiremockClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.admin_url = self.base_url + "/__admin"

    def stub(self, method, url, status_code=200, response_body=None, response_headers=None):
        stub_data = {
            "request": {
                "method": method.upper(),
                "urlPattern": url
            },
            "response": {
                "status": status_code,
                "headers": response_headers or {},
                "jsonBody": response_body
            }
        }

        try:
            response = requests.post(self.admin_url + "/mappings", json=stub_data)
            response.raise_for_status()
            print(f"Stub created. Response: {response.text}")
        except requests.RequestException as e:
            print(f"Error setting up Wiremock stub: {e}")
            print(f"Attempted to post to: {response.url}")
            print(f"Stub data: {json.dumps(stub_data, indent=2)}")
            raise

        return self.base_url + url

    def verify_stub_creation(self):
        try:
            response = requests.get(self.admin_url + "/mappings")
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error verifying stub creation: {e}")
            raise

    def reset(self):
        try:
            response = requests.post(self.admin_url + "/reset")
            response.raise_for_status()
            print("Wiremock reset successfully.")
        except requests.RequestException as e:
            print(f"Error resetting Wiremock: {e}")
            raise

    def get_all_mappings(self):
        try:
            response = requests.get(self.admin_url + "/mappings")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting all mappings: {e}")
            raise
