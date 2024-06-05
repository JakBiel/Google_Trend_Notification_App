import os

import functions_framework
import google.generativeai as genai
from pytrends.request import TrendReq
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def fetch_trending_searches():
    # Creating a pytrends instance
    pytrends = TrendReq(hl='en', tz=360)  # Setting the language to English and time zone (e.g., UTC+1 for Poland)

    # Fetching the most popular searches from the last 24 hours
    trending_list = pytrends.trending_searches()

    # Calling the function and printing the results
    print("Most popular phrases globally in the last 24 hours:")
    print(trending_list)

    return trending_list


def gemini_querying(trends):
    my_api_key = os.getenv('GEMINI_TOKEN')

    genai.configure(api_key=my_api_key)
    # The Gemini 1.5 models are versatile and work with both text-only and multimodal prompts
    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(f"""The attached below list of trends is a table now. 
                                    Please create from the list a table. Please attach to
                                    it a new column with a name Category. 
                                    In this new column, please define a short (max 3 words) 
                                    category for each element from the table. Dont't add explainations
                                    to the categories names below the response table. Also, don't forget
                                    about showing the index of each element. {trends}""")
    print(response.text)

    return response.text


def send_slack_notification(message):
    token = os.getenv('MY_SLACK_TOKEN')
    channel = "#jakub_channel"

    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        print("Message sent successfully")
    except SlackApiError as e:
        print(f"Failed to send message: {e.response['error']}")

## deployment confirmation comment

@functions_framework.http
def main(request):
    trends = fetch_trending_searches()
    results = gemini_querying(trends)
    send_slack_notification(f"This is generated, analyzed and modified by Gemini:\n\n Most popular trends in Google browser in last 24 hours: \n {results}")
    return "Success", 200

