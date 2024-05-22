import requests

def call_send_message(message_text):
    url = 'http://localhost:8080/send_message'
    params = {'message': message_text}
    try:
        response = requests.get(url, params=params)
        print(f'Status Code: {response.status_code}')
        print(f'Response Body: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    call_send_message("厳しいって")
    