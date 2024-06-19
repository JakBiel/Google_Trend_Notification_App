import os

import functions_framework
import google.generativeai as genai
from pytrends.request import TrendReq
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def fetch_trending_searches():
    # Creating a pytrends instance
    pytrends = TrendReq(
        hl="en", tz=360
    )  # Setting the language to English and time zone (e.g., UTC+1 for Poland)

    # Fetching the most popular searches from the last 24 hours
    trending_list = pytrends.trending_searches()

    # Calling the function and printing the results
    print("Most popular phrases globally in the last 24 hours:")
    print(trending_list)

    return trending_list


def gemini_querying(trends):
    my_api_key = os.getenv("GEMINI_TOKEN")

    genai.configure(api_key=my_api_key)
    # The Gemini 1.5 models are versatile and work with both text-only and multimodal prompts
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"""I attached below a list of trends. Please make each trend's name started and ended with "*" sign. Please attach to a trend in each row a proper category [define it short (max 3 words)]
                                    Dont't add any additional explainations to the list. Also, don't forget
                                    about showing the index of each element on the list. What's the last, please
                                    add related emoji at the end of each trend's row (which means not
                                    right after the trend's name.)
                                    Here is an example of 3 first rows, how they should be formatted and look like (regarding their form, not the content):
                                    1.  *Fort Lauderdale state of emergency*  -  News :rotating_light:
                                    2.  *Boston Celtics*  -  Sports :basketball:
                                    3.  *The Boys Season 4*  -  TV :male_superhero:
                                    {trends}"""
    )
    print(response.text)

    return response.text


def send_slack_notification(message):
    token = os.getenv("MY_SLACK_TOKEN")
    channel = "#jakub_channel"

    client = WebClient(token=token)
    try:
        client.chat_postMessage(
            channel=channel,
            text="This is a fallback text with *bold* text",
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": message}}],
        )
        print("Message sent successfully")
    except SlackApiError as e:
        print(f"Failed to send message: {e.response['error']}")


@functions_framework.http
def main(request):
    trends = fetch_trending_searches()
    results = gemini_querying(trends)
    send_slack_notification(
        f"THIS is generated, analyzed and modified by Gemini:\n\n Most popular trends in Google browser in last 24 hours: \n {results}"
    )
    return "Success", 200
