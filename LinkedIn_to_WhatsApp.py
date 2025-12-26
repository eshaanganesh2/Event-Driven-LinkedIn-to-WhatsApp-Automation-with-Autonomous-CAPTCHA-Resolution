from linkedin_api import Linkedin, client, cookie_repository
import os
from flask import Flask, request
import pickle
import aws_lambda_wsgi
import shutil

app = Flask(__name__)

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
    return "Hello World"

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
        display_phone_number=""
        recipient_phone_number=""
        status=""
        timestamp=""
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
            # from_number = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
            # timestamp = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('timestamp')
            # type = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('type')
            # text = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
                print("Error while extracting value from a webhook field")
            print("The sender phone number is ", display_phone_number)
            print("The recipient phone number is ",recipient_phone_number)
            print("The status is ",status)
            print("The timestamp is ",timestamp)
            # print("The from number is ",from_number)
            # print("The timestamp is ",timestamp)
            # print("The type is ",type)
            # print("The text is ",text)

        return "Success", 200


def handler(event, context):
    print("LinkedIn_to_Whatsapp_handler")
    return aws_lambda_wsgi.response(app, event, context)

if __name__ == "__main__":
    app.run()
