from linkedin_api import Linkedin, client, cookie_repository
import os
from flask import Flask, request
import pickle
import aws_lambda_wsgi
import shutil
import requests
from refreshCookies import RefreshCookies
import time
# from dotenv import load_dotenv

app = Flask(__name__)

# load_dotenv()

# COMMON_HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/120.0.0.0 Safari/537.36"
#     ),
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer": "https://www.linkedin.com/",
#     "Connection": "keep-alive",
# }


USER_SESSION = None
SESSION_TIMESTAMP = None
SESSION_TTL = 30 * 60  # 30 minutes in seconds
SOUP = None

def get_user_session():
    global USER_SESSION, SESSION_TIMESTAMP

    # If session doesn't exist or expired, create a new one
    now = time.time()
    if USER_SESSION is None or SESSION_TIMESTAMP is None or (now - SESSION_TIMESTAMP) > SESSION_TTL:
        print("Creating new user session...")
        USER_SESSION = requests.Session()
        SESSION_TIMESTAMP = now
        SOUP = None
    else:
        print("Reusing existing user session...")

    return USER_SESSION

def getLinkedinInstance(username, password, TMP_DIR):
    return Linkedin(username = username, password = password, cookies_dir=TMP_DIR)

def clear_cookies_jr(TMP_DIR):
   for name in os.listdir(TMP_DIR):
    path = os.path.join(TMP_DIR, name)
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)          
    elif os.path.isdir(path):
        shutil.rmtree(path)   

@app.route("/getLatestPost")
def get_latest_post():
    print("Retrieving latest linkedIn post")

    username = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')
    urnId = os.environ.get('URN_ID')

    print("The username is",username)

    TMP_DIR = os.environ.get("COOKIES_TMP_DIR", "./tmp/")  # local fallback

    os.makedirs(TMP_DIR, exist_ok=True)

    api={}
    try:
        api=getLinkedinInstance(username,password,TMP_DIR)
        print("api instance ",api)
    except client.ChallengeException as e:
        print("Challenge Exception")
        return {
            "error": "challenge_required",
            "message": str(e)
        }, 403
    # Expired cookies
    except cookie_repository.LinkedinSessionExpired:
        print("Session expired Exception")
        try:
            clear_cookies_jr(TMP_DIR)
            api=getLinkedinInstance(username,password,TMP_DIR)
        # Challenge to be solved
        except client.ChallengeException as e:
            try:
                print("Challenge Exception")
                return {
                    "error": "challenge_required",
                    "message": str(e)
                }, 403
            except Exception as e:
                print("Exception encountered ",e)
                return {
                    "error": "Exception",
                    "message": str(e)
                }, 500      
        except Exception as e:
            print("Exception encountered ",e)
            return {
                "error": "Exception",
                "message": str(e)
            }, 500
    except Exception as e:
        print("Exception encountered ",e)
        return {
            "error": "Exception",
            "message": str(e)
        }, 500
    
    post = api.get_profile_posts(urn_id=urnId,post_count=1)[0]
    # Extracting post content
    post_content = post["commentary"]["text"]["text"]

    print(post_content)

    return {
        "content": post_content
    }, 200

@app.route("/helloWorld")
def print_hello_world():
    print("Hello World")
    username = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')
    session=get_user_session()
    refreshCookies = RefreshCookies()
    SOUP=refreshCookies.login(session,username,password)
    print(SOUP)
    return "Hello World"

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

@app.route("/webhook", methods=['GET', 'POST'])
def print_webhooks():
    if request.method == 'GET':
        print('webhook endpoint verification')
        webhookVerifyToken = os.environ.get('WEBHOOK_VERIFY_TOKEN')
        mode = request.args.get('hub.mode')
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == webhookVerifyToken:
            print("Webhook verified successfully!")
            return challenge, 200
        else:
            print("Webhook verification failed!")
            return 'Forbidden', 403
    
    if request.method == 'POST':
        username = os.environ.get('LINKEDIN_EMAIL')
        password = os.environ.get('LINKEDIN_PASSWORD')
        owner=os.environ.get("OWNER")

        display_phone_number=""
        recipient_phone_number=""
        status=""
        timestamp=""
        webhook_reply=""
        print("Logging events")
        data=request.get_json()
        print("The webhook is ",data)
        if data:
            try:
                display_phone_number = data.get('entry')[0].get('changes')[0].get('value').get('metadata').get('display_phone_number')
                recipient_phone_number = data.get('entry')[0].get('changes')[0].get('value').get('statuses')[0].get('recipient_id')
                status = data.get('entry')[0].get('changes')[0].get('value').get('statuses')[0].get('status')
                timestamp = data.get('entry')[0].get('changes')[0].get('value').get('statuses')[0].get('timestamp')
            except:
                print("Error while extracting value from a webhook field")
            # Asking user to send linkedin verification code
            try:
                webhook_reply =  data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('interactive').get("button_reply").get("title")
                if webhook_reply == "Refresh cookies now!":
                    print("Owner chose to refresh cookies now")
                    print("Asking user for challenge verification PIN")
                    session=get_user_session()
                    # session.headers.update(COMMON_HEADERS)
                    refreshCookies = RefreshCookies()
                    SOUP=refreshCookies.login(session,username,password)
                    print("Sending message for verification code")
                    send_to_whatsapp_contact("Please share LinkedIn login verification code in the specified format\n verification code=<verification_code>",owner,standard_payload,"Standard")
            except Exception as e:
                print("Not a webhook reply",e)
            
            try:
                # Check for verification code
                verification_code_text_placeholder = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get("body")
                if verification_code_text_placeholder.startswith("verification code="):
                    print("Invoking automation to perform login and have cookies saved to temp dir")
                    session=get_user_session()
                    # session.headers.update(COMMON_HEADERS)
                    verification_code = verification_code_text_placeholder.split("verification code=")[1]
                    refreshCookies = RefreshCookies()
                    refreshCookies.verify_pin(session,verification_code,SOUP)
                    time.sleep(10)
                    print("Sign in automation code completed execution")
            except Exception as e:
                print("Error extracting verification code",e)



            print("The sender phone number is ", display_phone_number)
            print("The recipient phone number is ",recipient_phone_number)
            print("The status is ",status)
            print("The timestamp is ",timestamp)

        return "Success", 200


def handler(event, context):
    print("LinkedIn_to_Whatsapp_handler")
    return aws_lambda_wsgi.response(app, event, context)

if __name__ == "__main__":
    app.run()
