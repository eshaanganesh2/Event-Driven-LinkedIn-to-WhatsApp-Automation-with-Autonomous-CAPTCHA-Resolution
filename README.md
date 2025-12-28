## LinkedIn to WhatsApp Daily Notifier

This project fetches the latest LinkedIn post from a specified profile and sends it as a WhatsApp message to one or more contacts **every day at 8:30 AM UTC**. The backend is built using Python, Flask, and AWS Lambda with SAM for serverless deployment.

In addition, the system includes a **secure, semi-manual cookie refresh mechanism** to handle LinkedIn login challenges without permanently storing credentials or bypassing security checks.

---

## Features

* Flask-based API to retrieve latest LinkedIn post using `linkedin-api`
* Sends formatted WhatsApp messages using Meta’s WhatsApp Cloud API
* Scheduled execution every day at 11:30 AM UTC time via EventBridge
* Serverless deployment using AWS Lambda and AWS SAM
* Environment-driven configuration for credentials and recipients
* **Webhook-based LinkedIn session recovery flow**
* **Manual verification support via WhatsApp when LinkedIn challenges occur**
* Cookie reuse across days to minimize repeated logins

---

## Tech Stack

* **Backend**: Python 3.12, Flask
* **Deployment**: AWS Lambda + API Gateway (AWS SAM)
* **Scheduling**: EventBridge (cron)
* **Messaging**: WhatsApp Cloud API (Meta Graph API)
* **LinkedIn Access**: `linkedin-api` (unofficial)
* **Session Handling**: Cookies persisted to temporary storage
* **Verification Channel**: WhatsApp (manual user input)

---

## Architecture Overview

```
┌───────────────────────┐
│ LinkedIn (Web/Login)  │
└──────────┬────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Flask API (AWS Lambda)        │
│ - Fetch LinkedIn post         │
│ - Handle login & cookies     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ linkedin-api library          │
│ - Uses stored cookies         │
│ - Raises ChallengeException   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ WhatsApp Cloud API            │
│ - Sends post                  │
│ - Sends verification prompts  │
│ - Receives verification code  │
└──────────────────────────────┘
```

---

## Cookie & Challenge Handling

LinkedIn may periodically invalidate sessions or trigger security challenges when cookies expire or when activity is detected from a new environment (e.g., AWS Lambda).

This project handles such cases **gracefully and transparently** using a webhook-driven verification flow.

### 🔄 Cookie Refresh Flow

1. **Normal Operation**

   * The system uses previously saved LinkedIn cookies to fetch posts.
   * Cookies are stored in a temporary directory and reused across executions.

2. **Challenge Detected**

   * If `linkedin-api` raises a `ChallengeException`, the system:

     * Stops automated execution
     * Sends a **WhatsApp notification** indicating cookies have expired

3. **User-Initiated Refresh**

   * The WhatsApp message includes an option to **“Refresh cookies now”**
   * When selected, a refresh script is triggered

4. **Verification Code Delivery**

   * LinkedIn sends a **one-time verification code** to the account inbox (email/app)
   * The system prompts the user (via WhatsApp) to submit the code

5. **Manual Verification via WhatsApp**

   * The user replies in WhatsApp using the format:

     ```
     verification code=123456
     ```
   * The backend submits the code to LinkedIn

6. **Cookies Updated**

   * Upon successful verification:

     * Login completes
     * `linkedin-api` automatically saves fresh cookies to disk
     * Future executions reuse these cookies without additional login

📌 **No credentials are shared via WhatsApp**, and verification is only triggered when LinkedIn explicitly requires it.

---

## How It Works

### `/getLatestPost` (Flask API)

* Uses `linkedin-api` with stored cookies to fetch the latest post
* If cookies are valid → returns post content
* If cookies are expired → raises challenge and triggers WhatsApp notification

---

### Orchestrator Lambda

* Scheduled via EventBridge
  `cron(30 8 * * ? *)`
* Invokes `/getLatestPost`
* Sends the LinkedIn post to WhatsApp recipients
* Gracefully exits if a challenge is pending

---

## Folder Structure

```
├── LinkedIn_to_WhatsApp.py   # Flask API (Lambda entrypoint)
├── refreshCookies.py        # Login & verification handling
├── orchestrator.py          # Scheduled execution logic
├── template.yaml            # AWS SAM template
├── tmp/                     # Directory for LinkedIn cookies
├── dependencies-layer.zip   # Lambda layer with dependencies
```

---

## Security Notes

* Cookies are stored temporarily and refreshed only when required
* Verification codes are never persisted
* No attempt is made to bypass LinkedIn security mechanisms
* All sensitive values are injected via environment variables

---

## Acknowledgments

* [linkedin-api](https://github.com/tomquirk/linkedin-api)
* [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp)
* [AWS SAM](https://docs.aws.amazon.com/serverless-application-model)

---
