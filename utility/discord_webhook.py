import requests
import json

def send_discord_message(
    webhook_url,
    message
):
    # Create the payload for the webhook
    payload = {
        "content": message
    }

    # Convert the payload to JSON
    data = json.dumps(payload)

    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }

    # Send the POST request to the webhook URL
    response = requests.post(
        webhook_url,
        data=data,
        headers=headers
    )

    # Check if the request was successful
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(
            f"Failed to send message. "
            f"Status code: {response.status_code}"
        )
        print(f"Response: {response.text}")


def send_rich_discord_message(
    webhook_url,
    content=None,
    username=None,
    avatar_url=None,
    embeds=None
):
    payload = {}

    if content:
        payload["content"] = content
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url
    if embeds:
        payload["embeds"] = embeds

    data = json.dumps(payload)
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        webhook_url,
        data=data,
        headers=headers
    )
    return response
