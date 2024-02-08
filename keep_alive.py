import requests
import time

def keep_alive():
    # Send a request to the server to keep the session alive
    try:
        response = requests.post('http://your-server/keep-alive-endpoint', json={})
        response.raise_for_status()
        print('Keep-alive request sent successfully')
    except requests.exceptions.RequestException as e:
        print(f'Error sending keep-alive request: {e}')

# Set up an interval to send the keep-alive request every, for example, 5 minutes
while True:
    keep_alive()
    time.sleep(5 * 60)  # Sleep for 5 minutes
