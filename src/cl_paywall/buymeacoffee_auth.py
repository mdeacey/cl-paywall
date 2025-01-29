from __future__ import annotations
import requests
import os
import chainlit as cl

def extract_payer_emails(json_response):
    return [item.get("payer_email") for item in json_response.get("data", [])]

def get_bmac_payers(access_token: str | None = None, one_time: bool = False):
    if access_token is None:
        access_token = os.getenv("BMAC_API_KEY")
    
    if not access_token:
        cl.error("Buy Me a Coffee API key is missing.")
        return []
    
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://developers.buymeacoffee.com/api/v1/supporters" if one_time else "https://developers.buymeacoffee.com/api/v1/subscriptions?status=active"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return extract_payer_emails(response.json())
    else:
        cl.error(f"Error fetching subscriptions: {response.status_code} - {response.text}")
        return []
