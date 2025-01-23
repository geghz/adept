import aiohttp
import re
from datetime import datetime

def linkToUrl(link: str) -> str:
    numbers = re.findall(r'\b\d+\b', link)
    object_id = numbers[0]
    journal_id = numbers[1]
    act_id = numbers[2]
    return f"https://adept.irkutskoil.ru/api/objects/{object_id}/journals/{journal_id}/execDoc/{act_id}/acts"

def time_check(date1: str, date2: str) -> bool:
    dttm1 = datetime.strptime(date1.split('T')[0], '%Y-%m-%d')
    dttm2 = datetime.strptime(date2.split('T')[0], '%Y-%m-%d')
    return dttm1 >= dttm2

def compute_status(sign: bool, refuse: str | None, notify: str | None) -> str:
    if sign:
        return 'Выполнена'
    elif refuse and notify:
        if time_check(refuse, notify):
            return 'Отказ'
        else:
            return 'Повторно'
    elif refuse:
        return 'Отказ'
    elif notify:
        return 'Оповещение'
    else:
        return 'Нет оповещения'

async def r6_check(session: aiohttp.ClientSession, link: str, headers: dict) -> tuple[str | None, str | None]:

    url = linkToUrl(link)
    async with session.get(url, headers=headers, ssl=False) as resp:
        data = await resp.json()

    search_str = 'ООО "ИФ ИнтерГазСервис"'
    signatureTypePartners = data.get('signatureTypePartners', [])

    found_partners = []
    for p in signatureTypePartners:
        rep = p.get('representative')
        if not rep:
            continue

        if rep['partner'].get('name') == search_str:
            name = rep.get('fio') or rep.get('name') or 'Неизвестно'
            sign = bool(p.get('signature'))
            refuse = p.get('dateRefuse')
            notify = p.get('dateNotify')

            status = compute_status(sign, refuse, notify)
            found_partners.append({
                'name': name,
                'status': status
            })

    if not found_partners:
        return (None, 'Нет подписантов')

    statuses = [fp['status'] for fp in found_partners]

    if all(s == 'Выполнена' for s in statuses):
        return ('Выполнена', None)
    if all(s == 'Отказ' for s in statuses):
        return ('Отказ', None)
    if all(s == 'Повторно' for s in statuses):
        return (None, 'Повторно')
    if all(s == 'Нет оповещения' for s in statuses):
        return (None, 'Нет оповещения')
    if all(s == 'Оповещение' for s in statuses):
        return (None, None)
    if any(s == 'Повторно' for s in statuses):
        return (None, 'Повторно')
    if any(s == 'Отказ' for s in statuses):
        return ('Отказ', None)
    for fp in found_partners:
        if fp['status'] != 'Выполнена':
            return (None, f'Отсутствует подпись {fp["name"]}')

    return (None, None)
