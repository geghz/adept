# task_prescriptions.py

import aiohttp
import re

def linkToUrl(link: str) -> str:
    numbers = re.findall(r'\b\d+\b', link)
    object_id = numbers[0]
    prescription_id = numbers[-1]
    
    if 'warning-possible-stop-cmp' in link:
        type_id = 'warning-possible-stop-cmp'
    else:
        type_id = 'prescription-stop-cmp'
    
    url = f'https://adept.irkutskoil.ru/api/objects/{object_id}/prescriptions/{type_id}/{prescription_id}'
    return url

async def prescription_check(
    session: aiohttp.ClientSession,
    link: str,
    headers: dict
) -> tuple[str | None, str | None]:

    url = linkToUrl(link)
    
    async with session.get(url, headers=headers, ssl=False) as resp:
        data_json = await resp.json()

    data = data_json['prescriptionCard']

    if data['repBuildControlSign']:
        task = 'Выполнена'
        remark = None
    else:
        task = None
        remark = None

    return task, remark
