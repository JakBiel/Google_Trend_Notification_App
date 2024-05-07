import base64


def hello_world(event, context):
    """
    Function triggered by Pub/Sub events.
    :param event: Contains the encoded Pub/Sub message data.
    :param context: Metadata for the invocation, such as ID and timestamp.
    """
    # Decode the Pub/Sub message data
    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    else:
        pubsub_message = 'No data found in Pub/Sub message'

    # Additional information (attributes) of the message
    attributes = event.get('attributes', {})
    
    # Print received data (replace this with function logic)
    print(f'Message: {pubsub_message}')
    print(f'Attributes: {attributes}')
