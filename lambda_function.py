import os
import re
import json
import time
import hmac
import hashlib
import threading
import boto3
import requests

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

# --- Claude 3 classification ---
def classify_with_bedrock(prompt_text):
    bedrock = boto3.client("bedrock-runtime", region_name="eu-west-2")
    print("prompt_text:", prompt_text)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.3,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Please classify the following incident message into one of these categories:
                                [Network Issue, Application Bug, Security Alert, Other]
                                Incident: "{prompt_text}" """
                    }
                ]
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response['body'].read())
    return result["content"][0]["text"].strip()


# --- Send message to Slack ---
def post_to_slack(channel, message):
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "channel": channel,
            "text": message
        }
    )


# --- Async handler for classification and response ---
def handle_event_async(body):
    try:
        event = body["event"]
        print("async event:", json.dumps(event))
        raw_text = event.get("text", "")
        text = re.sub(r"<@[^>]+>\s*", "", raw_text).strip()
        channel = event.get("channel", "")
        
        classification = classify_with_bedrock(text)
        print("classification:", classification)
        reply = f"Incident classified as: *{classification}*"
        print("reply:", reply)
        post_to_slack(channel, reply)

    except Exception as e:
        print("Async error:", str(e))


# --- Signature verification ---
def verify_slack_signature(headers, body):
    timestamp = headers.get("x-slack-request-timestamp")
    slack_signature = headers.get("x-slack-signature")

    if not timestamp or not slack_signature:
        print("Missing Slack signature headers")
        return False

    # Prevent replay attacks
    if abs(time.time() - int(timestamp)) > 60 * 5:
        print("Timestamp too old")
        return False

    sig_basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)


# --- Main Lambda handler ---
def lambda_handler(event, context):
    headers = event.get("headers", {})
    body_str = event.get("body", "{}")
    body = json.loads(body_str)

    # Handle Slack URL verification
    if body.get("type") == "url_verification":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"challenge": body["challenge"]})
        }

    # Verify Slack signature
    if not verify_slack_signature(headers, body_str):
        return {"statusCode": 401, "body": "Invalid signature"}

    # Handle retries (Slack may resend the same message)
    # if headers.get("x-slack-retry-num"):
    #     print("Duplicate retry from Slack, skipping.")
    #     return {"statusCode": 200, "body": "Retry acknowledged"}

    # Handle app mentions (or other events)
    if body.get("type") == "event_callback":
        threading.Thread(target=handle_event_async, args=(body,)).start()
        return {"statusCode": 200, "body": "OK"}

    return {"statusCode": 200, "body": "Unhandled event"}
