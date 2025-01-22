import requests
import re

def linkToUrl(link):
    numbers = re.findall(r'\b\d+\b', link)
    object_id = numbers[0]
    remark_id = numbers[-1]
    url = f'https://adept.irkutskoil.ru/api/objects/{object_id}/remarks/{remark_id}'
    return url

def remark_check(link, headers):

    url = linkToUrl(link)
    resp = requests.get(url, headers=headers, verify=False)
    data = resp.json()['remark']

    if data['eliminator']:
        eliminator = True
    else:
        eliminator = False

    if data['eliminator_sign']:
        elim_sign = True
    else:
        elim_sign = False

    if data['verificator']:
        verificator = True
    else:
        verificator = False

    if data['verificator_sign']:
        verif_sign = True
    else:
        verif_sign = False

    if elim_sign and verif_sign:
        task = 'Выполнена'
        remark = None
    elif elim_sign:
        task = None
        remark = None
    elif eliminator:
        task = None
        remark = 'Нет подписи ПО'
    else:
        task = None
        remark = 'Не указан ответственный за устранение'

    return task, remark