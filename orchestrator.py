import requests
import os
import json
from linkedin_api import client

# Obtaining latest LinkedIn post
def get_latest_post():
    url = os.environ.get("AWS_HOST")+"/Prod/getLatestPost"
    res = requests.get(url)
    return res

# Sending whastapp notification
def send_to_whatsapp_contact(latest_post,recipient,payload,template):
    # Prepare whatsapp graph api request body
    token = os.environ.get("WHATSAPP_BEARER_TOKEN")
    print("The token is ",token)
    print("The recipient is ",recipient)
    url = os.environ.get("WHATSAPP_API_URL")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if template=="Standard":
        payload["to"]=recipient
        payload["text"]["body"]=latest_post
    
    if template=="Reply":
        payload["to"]=recipient

    res = requests.post(url, headers=headers, json=payload)

    print("WhatsApp API response:", res.status_code, res.text)
    return {
        "statusCode": res.status_code,
        "body": res.text
    }

def lambda_handler(event, context):
    print("Starting scheduled orchestration...")
    recipients_str=os.environ.get("RECIPIENTS")
    print("The recipient list is ",recipients_str)
    recipients=json.loads(recipients_str)

    owner=os.environ.get("OWNER")
    print("The owner is ",owner)

    standard_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "recipient",
        "type": "text",
        "text": {
            "preview_url": True,
            "body": "latest_post"
        }
    }

    reply_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "recipient",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Do you want to refresh session cookies now?"
            },
            "action": {
            "buttons": [
                {
                "type": "reply",
                "reply": {
                    "id": "change-button",
                    "title": "Refresh cookies now!"
                }
                },
                {
                "type": "reply",
                "reply": {
                    "id": "cancel-button",
                    "title": "No"
                }
                }
            ]
            }
        }
    }

    res = get_latest_post()
    data=res.json()
    if res.status_code==403:
        if data.get("error") == "challenge_required":
            print("Sending message template to owner, asking to trigger the refresh cookie flow")
            template="Reply"
            send_to_whatsapp_contact("",owner,reply_payload,template)
            return {"statusCode": 200, "body": "User needs to refresh cookies"}

    elif res.status_code==500:
        return {"statusCode": 500, "body": data.get("message")}
    # Step 3: Call second endpoint
    elif res.status_code==200:
        template="Standard"
        latest_post=data.get("content")
        for recipient in recipients:
            send_to_whatsapp_contact(latest_post,recipient,standard_payload,template)

        return {"statusCode": 200, "body": "Workflow completed"}
