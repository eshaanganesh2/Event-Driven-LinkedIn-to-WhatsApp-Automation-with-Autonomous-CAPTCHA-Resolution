from linkedin_api import Linkedin, client, cookie_repository
import os
import shutil
from flask import Flask, request, jsonify
import aws_lambda_wsgi
import boto3
import json
import time
import pickle
import ast
import base64
from boto3.dynamodb.types import Binary

app = Flask(__name__)
lambda_client = boto3.client('lambda')

# Global variable to hold the browser for cleanup
browser_instance = None
pw_instance = None

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('PIN_TABLE_NAME', 'PinStoreTable'))

def getLinkedinInstance(username, password, TMP_DIR):
    return Linkedin(username = username, password = password, cookies_dir=TMP_DIR)

def clear_cookies_jr(TMP_DIR):
   for name in os.listdir(TMP_DIR):
    path = os.path.join(TMP_DIR, name)
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)          
    elif os.path.isdir(path):
        shutil.rmtree(path)

def move_bundled_cookies(username, TMP_DIR):
    # 1. Path where the file exists in your Docker image
    bundled_path = os.path.join(os.environ['LAMBDA_TASK_ROOT'], 'tmp', f"{username}.jr")
    print("The bundled path is",bundled_path)
    
    # 2. Path where the library wants to use it (/tmp/)
    runtime_path = os.path.join(TMP_DIR, f"{username}.jr")
    
    # 3. Only copy if it's not already there (prevents redundant work on warm starts)
    if not os.path.exists(runtime_path):
        if os.path.exists(bundled_path):
            shutil.copy(bundled_path, runtime_path)
            print(f"Successfully moved bundled cookies to {runtime_path}")
        else:
            print(f"CRITICAL: Bundled file not found at {bundled_path}")
    else:
        print(f"Cookies file already exists at {TMP_DIR}")
    
def sync_cookies_from_db(username, TMP_DIR):
    print("Checking DynamoDB for cookies and writing them to /tmp if found")
    cookie_path = os.path.join(TMP_DIR, f"{username}.jr")
    try:
        response = table.get_item(Key={'owner': os.environ.get('OWNER')})
        if 'Item' in response and 'linkedin_cookies' in response['Item']:
            # DynamoDB binary data is wrapped in a Binary object in Boto3
            cookie_bytes = response['Item']['linkedin_cookies'].value
            with open(cookie_path, "wb") as f:
                f.write(cookie_bytes)
            print(f"Restored cookies from DynamoDB to {cookie_path}")

            #####################################################################
            # Code block for printing how much longer cookies are valid for
            with open(cookie_path, "rb") as f:
                jar = pickle.load(f)
                
            now = int(time.time())
            for cookie in jar:
                if cookie.name == 'li_at':
                    # cookie.expires is a Unix timestamp
                    if cookie.expires and cookie.expires > now:
                        remaining = (cookie.expires - now) / 86400
                        print(f"Verified: {cookie.name} is valid for {remaining:.2f} more days.")
                        return True
                    else:
                        print(f"Warning: {cookie.name} has expired!")
                        print("cookie expired on ",cookie.expires)
            #####################################################################
            return True
    except Exception as e:
        print(f"No cookies in DB or error: {e}")
    return False

def clear_verification_pin_from_db():
    print("Clearing the PIN from DynamoDB to prevent reuse")
    try:
        table.update_item(
            Key={'owner': os.environ.get('OWNER')},
            UpdateExpression="REMOVE pin",
            # We add a condition to ensure we only try to remove it if it exists
            ConditionExpression="attribute_exists(pin)"
        )
        print("PIN successfully cleared.")
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        print("PIN attribute did not exist; nothing to clear.")
    except Exception as e:
        print(f"Error clearing PIN: {e}")

def save_cookies_to_db(username, TMP_DIR):
    print("Reading the local .jr file and saving it to DynamoDB")
    cookie_path = os.path.join(TMP_DIR, f"{username}.jr")
    if os.path.exists(cookie_path):
        with open(cookie_path, "rb") as f:
            cookie_bytes = f.read()
            table.update_item(
                Key={'owner': os.environ.get('OWNER')},
                UpdateExpression="SET linkedin_cookies = :c",
                ExpressionAttributeValues={':c': Binary(cookie_bytes)}
            )
        print("Cookies synced to DynamoDB")

@app.route("/helloWorld")
def print_hello_world():
    print("Hello World")
    return "Hello World"

@app.route("/getLatestPost")
def get_latest_post():
    print("Retrieving latest linkedIn post")

    username = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')
    urnId = os.environ.get('URN_ID')

    print("The username is",username)

    TMP_DIR = os.environ.get("COOKIES_TMP_DIR", "./tmp/")  # local fallback

    clear_verification_pin_from_db()

    os.makedirs(TMP_DIR, exist_ok=True)
    cookie_path = os.path.join(TMP_DIR, f"{username}.jr")
    if not sync_cookies_from_db(username, TMP_DIR) and not os.path.exists(cookie_path):
        move_bundled_cookies(username, TMP_DIR)
    else:
        print("Using existing cookies from DynamoDB/tmp dir")

    api={}
    try:
        api=getLinkedinInstance(username,password,TMP_DIR)
        print("api instance ",api)
    except client.ChallengeException as e:
        print("1. client.ChallengeException: Challenge Exception")
        return {
            "error": "challenge_required",
            "message": str(e)
        }, 403
    # Expired cookies
    except cookie_repository.LinkedinSessionExpired:
        print("cookie_repository.LinkedinSessionExpired: Session expired Exception")
        try:
            clear_cookies_jr(TMP_DIR)
            print("Cookies dir cleared")
            api=getLinkedinInstance(username,password,TMP_DIR)
        # Challenge to be solved
        except client.ChallengeException as e:
            try:
                print("2. client.ChallengeException: Challenge Exception")
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
    
    save_cookies_to_db(username, TMP_DIR)
    post = api.get_profile_posts(urn_id=urnId,post_count=1)[0]
    # Extracting post content
    post_content = post["commentary"]["text"]["text"]

    print(post_content)

    return {
        "content": post_content
    }, 200

@app.route("/webhook", methods=['GET', 'POST'])
def webhook_entry():
    if request.method == 'GET':
        verify_token = os.environ.get('WEBHOOK_VERIFY_TOKEN')
        if request.args.get("hub.verify_token") == verify_token:
            return request.args.get("hub.challenge"), 200
        return 'Forbidden', 403

    # Immediate acknoledgement to the webhook endpoint to avoid duplicate webhooks
    data = request.get_json()
    
    lambda_client.invoke(
        FunctionName=os.environ.get('WORKER_FUNCTION_NAME'),
        InvocationType='Event',
        Payload=json.dumps(data)
    )
    
    return "OK", 200

@app.route("/buildCookieJar", methods=['POST'])
def build_cookie_jar_from_body():
    """
    Accepts binary bytes OR string representation from DynamoDB 
    in the POST body, constructs the .jr file, and returns cookie metadata.

    ==========================================================================
    TESTING IN POSTMAN (WITH DYNAMODB STRING TEXT):
    1. Set Method to POST.
    2. URL: http://127.0.0.1:5000/buildCookieJar
    3. Go to "Body" -> Select "raw" -> Select "Text" (or "JSON").
    4. Paste the DynamoDB string directly into the text box.
    5. Hit "Send".
    ==========================================================================
    """
    username = os.environ.get('LINKEDIN_EMAIL')
    TMP_DIR = os.environ.get("COOKIES_TMP_DIR")
    cookie_file_path = os.path.join(TMP_DIR, f"{username}.jr")

    # 1. Read body data
    payload = request.get_data()

    if not payload:
        return jsonify({
            "error": "empty_body",
            "message": "No payload provided in the request body."
        }), 400

    raw_bytes = None

    # 2. Convert text string formats to raw bytes
    try:
        # Check if payload is string format like "b'\x80\x04...'" or "\x80\x04..."
        payload_str = payload.decode('utf-8').strip()
        
        if payload_str.startswith("b'") or payload_str.startswith('b"'):
            # Convert Python byte literal string (e.g., b'\x80\x04...') back to bytes
            raw_bytes = ast.literal_eval(payload_str)
        else:
            try:
                # Try Base64 decoding if DynamoDB exported it as Base64 text
                raw_bytes = base64.b64decode(payload_str)
            except Exception:
                # Fallback: treat string as latin-1 escaped bytes
                raw_bytes = payload_str.encode('latin-1')
    except Exception:
        # If payload was already pure binary bytes
        raw_bytes = payload

    try:
        # Ensure target directory exists
        os.makedirs(TMP_DIR, exist_ok=True)

        # 3. Write decoded raw bytes directly to the .jr file
        with open(cookie_file_path, "wb") as f:
            f.write(raw_bytes)

        print(f"Successfully created {cookie_file_path}")

        # 4. Verify cookie jar in memory
        jar_summary = []
        with open(cookie_file_path, "rb") as f:
            cookie_jar = pickle.load(f)
            for cookie in cookie_jar:
                jar_summary.append({
                    "name": cookie.name,
                    "domain": cookie.domain,
                    "expires": cookie.expires
                })

        return jsonify({
            "status": "success",
            "file_path": cookie_file_path,
            "bytes_written": len(raw_bytes),
            "cookies_found": jar_summary
        }), 200

    except pickle.UnpicklingError:
        return jsonify({
            "error": "invalid_format",
            "message": "The payload could not be unpickled into a valid RequestsCookieJar. Check string encoding."
        }), 400
    except Exception as e:
        print(f"Failed to create .jr file: {e}")
        return jsonify({
            "error": "write_failed",
            "message": str(e)
        }), 500

def handler(event, context):
    try:
        return aws_lambda_wsgi.response(app, event, context)
    finally:
        global browser_instance, pw_instance
        if browser_instance:
            browser_instance.close()
        if pw_instance:
            pw_instance.stop()

if __name__ == "__main__":
    app.run()