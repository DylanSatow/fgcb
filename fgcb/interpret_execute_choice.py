import time
import requests
import random

url = "http://127.0.0.1:8000"

# Define the endpoints
endpoints = {
    "prev": url + "/press_up",
    "next": url + "/press_down",
    "pause": url + "/click"
}

def scroll_maybe(prob) -> bool:
    """
    Returns whether to scroll or not scroll based on probability.

    Returns:
        bool: scroll (True) or don't scroll (False)
    """

    if not (0.0 <= prob <= 1.0):
        raise ValueError("Bad probability")

    rand_num = random.random() 

    # Scroll
    if rand_num >= prob:
        return True
    # Don't scroll
    else:
        return False


def send_request(endpoint_url, data=None, json=None):
    """Sends an HTTP POST request to the specified endpoint."""
    try:
        response = requests.post(endpoint_url, data=data, json=json)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        # print(f"POST request to {endpoint_url} successful. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request to {endpoint_url}: {e}")


if __name__ == "__main__":
    p = 0.3

    while True:
        if scroll_maybe(p):
            send_request(endpoints["next"])
        time.sleep(2)