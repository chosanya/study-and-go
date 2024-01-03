import requests
import time

api_url = 'https://api.telegram.org/bot'
cat_api_url = 'https://random.dog/woof.json'
bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'
er_text = 'тут должна быть картинка с псиной, но у разраба руки из жопы'
mxk = 100

offset = -2
counter = 0
cat_resp: requests.Response
cat_link: str
chat_id: int

while counter < mxk:
    print('attemp =', counter)
    updates = requests.get(f'{api_url}{bot_token}/getUpdates?offset={offset+1}').json()

    if updates['result']:
        for result in updates['result']:
            offset = result['update_id']
            chat_id = result['message']['from']['id']
            cat_resp = requests.get(cat_api_url)
            if cat_resp == 200:
                cat_link = cat_resp.json()[0]['url']
                requests.get(f'{api_url}{bot_token}/sendPhoto?chat_id={chat_id}&photo={cat_link}')
            else: requests.get((f'{api_url}{bot_token}/sendMessage?chat_id={chat_id}&text={er_text}'))


    time.sleep(1)
    counter+=1