import aiohttp
from datetime import datetime
import re

def time_check(date1: str, date2: str) -> bool:

    dttm1 = datetime.strptime(date1.split('T')[0], '%Y-%m-%d')
    dttm2 = datetime.strptime(date2.split('T')[0], '%Y-%m-%d')
    return dttm1 >= dttm2

def linkToUrl(link: str) -> str:
    
    numbers = re.findall(r'\b\d+\b', link)
    object_id = numbers[0]
    journal_id = numbers[1]
    act_id = numbers[2]
    url = f'https://adept.irkutskoil.ru/api/objects/{object_id}/entrance-journals/{journal_id}/acts/{act_id}/content'
    return url

async def arvk_check(
    session: aiohttp.ClientSession,
    link: str,
    headers: dict
) -> tuple[str | None, str | None]:
    
    search_str = 'ООО "ИФ ИнтерГазСервис"'
    url = linkToUrl(link)

    async with session.get(url, headers=headers, ssl=False) as resp:
        data_json = await resp.json()

    partners = data_json['signatureTypePartners']

    partner_item = next(
        (
            p for p in partners
            if p.get('representative')
            and p['representative']['partner'].get('name') == search_str
        ),
        None
    )
    if not partner_item:
        return None, 'Нет в подписантах'

    signature = partner_item.get('signature')
    date_refuse = partner_item.get('dateRefuse')
    date_notify = partner_item.get('dateNotify')

    if signature:
        return 'Выполнена', None
    if date_refuse and date_notify:
        if time_check(date_refuse, date_notify):
            return 'Отказ', None
        else:
            return None, 'Повторно'
    if date_refuse:
        return 'Отказ', None
    if date_notify:
        return None, None
    else:
        return None, 'Нет оповещения'
