# Slackbot for Incident Classification using Amazon Bedrock (Claude 3 Haiku)

## Overview
This project implements an intelligent Slackbot that listens to messages in Slack (such as user-reported incidents), classifies them using Claude 3 Haiku on Amazon Bedrock, and responds with a suggested category (e.g., Network Issue, Application Bug, Security Alert).

## Built with:

- AWS Lambda (serverless backend)
- API Gateway (Slack Event URL endpoint)
- Slack Events API
- Amazon Bedrock (Claude 3 Haiku via Messages API)
- Python (runtime + Bedrock client)

## Use Case
Why this project?
- Many DevOps and SRE teams rely on Slack for reporting incidents.
- Classifying and routing issues manually slows down triage.
- This bot automates classification and improves response times using LLMs (Claude 3)

## Architecture
Slack → API Gateway → Lambda → Claude 3 (Amazon Bedrock)
                             ↘ Slack reply via chat.postMessage

### 1. User sends a message in Slack mentioning the bot
### 2. Slack sends the event to API Gateway → Lambda
### 3. Lambda cleans the text, classifies it using Claude 3 via Bedrock Messages API
### 4. The bot responds in Slack with a classification

##  Tech Stack

| Layer            | Technology / Service                     | Description                                  |
|------------------|-------------------------------------------|----------------------------------------------|
| Chat Interface   | Slack (Bot + Events API)                 | Handles message events and replies           |
| Compute          | AWS Lambda (Python 3.10+)                | Serverless function for classification logic |
| API Gateway      | HTTP API (proxy integration, payload v2) | Exposes Lambda to Slack securely             |
| AI/ML Engine     | Amazon Bedrock - Claude 3 Haiku          | Classifies incident messages                 |
| Auth & Security  | Slack OAuth + Signing Secret             | Verifies Slack signatures and tokens         |
| Observability    | AWS CloudWatch                           | Logs, metrics, and debugging                 |


## Features
- Slackbot listens to @mentions
- Classifies incident messages into categories:
  - Network Issue
  - Application Bug
  - Security Alert
  - Other
- Replies directly in Slack
- Deduplicates Slack retries
- Handles Bedrock model errors gracefully
- Lightweight, serverless, and low latency (~1–2s)

## Getting Started
## 1. Clone this repository
```bash
git clone https://github.com/sandhya19/slackbot-bedrock.git
cd slackbot-bedrock
```
## 2. Set Up Slack App
- Create a new Slack app
- Enable Event Subscriptions
- Subscribe to:
  - app_mention
- Add OAuth scopes:
  - chat:write
  - app_mentions:read
- Install app to your workspace
- Get SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET

## 3. Deploy Lambda Function
- Create a Lambda with Python 3.10+
- Add environment variables:
  - SLACK_BOT_TOKEN
  - SLACK_SIGNING_SECRET
- Set IAM policy to allow bedrock:InvokeModel
- Connect via API Gateway (proxy integration, payload v2)

## 4. Grant Bedrock Access
- Use modelId: anthropic.claude-3-haiku-20240307-v1:0
- Opt-in via AWS Console → Bedrock → Model access

## Directory Structure

```bash
.
├── lambda_function.py       # Main Lambda handler
├── requirements.txt         # (Optional: for packaging)
├── test_event.json          # Sample Slack event payload
├── README.md                # This file
```
## Sample Message & Bot Response
# Input:
```bash
@chatbot the application is not responding
```

# Response:
```bash
Incident classified as: *Based on the incident message provided, "the application is not responding, this would be classified as an Application Bug.
The message indicates that a specific application is not functioning properly, which suggests an issue with the application itself rather than a network problem or a security alert.*
```


## License
MIT License


