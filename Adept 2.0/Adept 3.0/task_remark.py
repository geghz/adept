import aiohttp
import re

def linkToUrl(link: str) -> str:
    numbers = re.findall(r'\b\d+\b', link)
    object_id = numbers[0]
    remark_id = numbers[-1]
    url = f"https://adept.irkutskoil.ru/api/objects/{object_id}/remarks/{remark_id}"
    return url

async def remark_check(session: aiohttp.ClientSession, link: str, headers: dict):

    url = linkToUrl(link)

    async with session.get(url, headers=headers) as resp:
        data_json = await resp.json()
    д
    data = data_json['remark']

    eliminator      = bool(data['eliminator'])
    elim_sign       = bool(data['eliminator_sign'])
    verif_sign      = bool(data['verificator_sign'])

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
