## Deployment & Debugging

---

## Essential Environment Variables

| Variable Name           | Description                                   |
| ----------------------- | --------------------------------------------- |
| `PIN_TABLE_NAME`        | Auto-linked DynamoDB table                    |
| `WORKER_FUNCTION_NAME`  | Pointer for the fire-and-forget refresh logic |
| `WHATSAPP_BEARER_TOKEN` | Long-term Meta System User token              |
| `HOME=/tmp`             | Critical for Chrome write-access in Lambda    |

---

## Important Notes

* **Webhook Issues**
  If you register a new test number and don't receive webhooks, verify your subscription fields in the Meta App Dashboard (ensure `messages` is enabled).

* **Storage**
  The system uses `/tmp` for ephemeral file processing. Persistent data belongs in DynamoDB.

---

## Deployment-Created Environment Variables

The following environment variables are **auto-created during deployment** via `template.yaml`:

```text
PIN_TABLE_NAME
WORKER_FUNCTION_NAME
```

---

## WhatsApp Bearer Token Setup

For the `WHATSAPP_BEARER_TOKEN` (long-term Personal Access Token), follow **Step 4** in the official Meta documentation:

```text
https://developers.facebook.com/micro_site/url/?click_from_context_menu=true&country=KW&destination=https%3A%2F%2Fdevelopers.facebook.com%2Fdocs%2Fwhatsapp%2Fbusiness-management-api%2Fusing-the-api%231--acquire-an-access-token-using-a-system-user-or-facebook-login&event_type=click&last_nav_impression_id=0Qxb77GXOgDYYCSr9&max_percent_page_viewed=100&max_viewport_height_px=811&max_viewport_width_px=1440&orig_http_referrer=https%3A%2F%2Fdevelopers.facebook.com%2Fapps%2F3163004767191586%2Fwhatsapp-business%2Fwa-settings%2F%3Fbusiness_id%3D1003746238297566&orig_request_uri=https%3A%2F%2Fdevelopers.facebook.com%2Fajax%2Fpagelet%2Fgeneric.php%2FDeveloperAppDashboardContentPagelet%3Ffb_dtsg_ag%3D--sanitized--%26data%3D%257B%2522app_id%2522%253A%25223163004767191586%2522%252C%2522page%2522%253A%2522whatsapp-business%2522%252C%2522tab%2522%253A%2522wa-settings%2522%252C%2522app_locale%2522%253Anull%252C%2522id%2522%253Anull%252C%2522a_n%2522%253Anull%252C%2522c_n%2522%253Anull%252C%2522alert_id%2522%253Anull%252C%2522ref%2522%253Anull%252C%2522dev_listing_id%2522%253Anull%252C%2522use_case_enum%2522%253Anull%252C%2522add_on_enum%2522%253Anull%252C%2522is_go_live_modal_shown%2522%253Afalse%252C%2522show_uba_opt_in%2522%253Afalse%257D%26jazoest%3D24763&region=emea&scrolled=false&session_id=1RZTj8ZJ1W7cxHOzC&site=developers
```

---

## Lambda Runtime Configuration

The following environment variable **must be explicitly set in AWS Lambda**:

```text
HOME=/tmp
```

This is required to allow Chrome and Playwright write access in the Lambda execution environment.

---

## Webhook Debugging

### Issue: No Webhooks After Registering a New WhatsApp Test Number

If webhooks stop triggering after registering a new test number, refer to the following solution:

```text
https://stackoverflow.com/questions/79175537/whatsapp-business-api-messages-webhook-not-triggering-even-with-manual-testin
```

---

## Build & Deployment Commands

```bash
sam build --use-container --no-cached
sam deploy
```

---
