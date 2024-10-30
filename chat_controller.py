import pandas as pd
# from model import generate_amazon_review

def generate_output(action, query = None):
    """ Generate Outputs on HTTP-Requests

    Args:
        action (str): The action what should be done.
        query (str): Additional information for actions (Optional)

    Returns:
        dict: Payload for the request
    """

    if action == 'categories':
        data = pd.read_csv('lists/reviews_for_categories.csv', sep=',', low_memory=False)
        result = {"categories": data.to_dict(orient='records')}
        return result
    elif action == 'top_3':
        data = pd.read_csv('lists/reviews_top_3.csv', sep=',', low_memory=False)
        result = data.to_dict(orient='records')
        return result
    elif action == 'generate':
        # result = {"review": generate_amazon_review(query)}
        result = {"review": 'Currently disabled due to enormous loading times...'}
        return result
    else:
        return {'forbidden': 'action not supported or not provided'}
