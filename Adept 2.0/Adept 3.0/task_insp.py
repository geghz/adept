import aiohttp
import re

SEARCH_STR = 'ООО "ИФ ИнтерГазСервис"'

def linkToUrl(link: str) -> str:

    numbers = re.findall(r'\b\d+\b', link)
    object_id = numbers[0]
    insp_id = numbers[1]
    url = f"https://adept.irkutskoil.ru/api/objects/{object_id}/inspections/{insp_id}?author_id=489"
    return url

def parse_supervisor(data: dict) -> tuple[bool, bool, bool]:

    supervisors = data.get('supervisors') or []
    if not supervisors:
        # Нет записей => этап не нужен
        return (False, False, False)

    s = supervisors[0]
    
    done_supervisor = bool(s.get('signatureAgreement'))
    cancel_supervisor = bool(s.get('cancelDate'))
    need_supervisor = True
    
    return (need_supervisor, done_supervisor, cancel_supervisor)

def parse_representative(data: dict) -> tuple[bool, bool, bool, bool]:

    representatives = data.get('representatives') or []
    if not representatives:
        return (False, False, False, False)
    
    for item in representatives:
        rep = item.get('representative')
        if rep and rep['partner'].get('name') == SEARCH_STR:

            cancel_participation = bool(item.get('cancelDate'))
            confirmed_participation = bool(item.get('isConfirmed'))
            
            st = item.get('status')
            st_name = st.get('name') if st else None

            done_result = bool(st_name and st_name != 'В работе')
            
            return (True, confirmed_participation, done_result, cancel_participation)
    
    # Не нашли SEARCH_STR => этап не нужен
    return (False, False, False, False)

def combine_insp(
    need_supervisor: bool, done_supervisor: bool, cancel_supervisor: bool,
    need_participation: bool, confirmed_participation: bool, done_result: bool, cancel_participation: bool
) -> tuple[str | None, str | None]:

    if cancel_supervisor or cancel_participation:
        return ("Отклонено", None)
    
    sup_ok = (not need_supervisor) or (need_supervisor and done_supervisor)
    par_ok = (not need_participation) or (confirmed_participation and done_result)
    
    if sup_ok and par_ok:
        return ("Выполнена", None)
    
    missing = []
    
    if need_supervisor and not done_supervisor:
        missing.append("Поставить подпись согласования")
    
    if need_participation:
        if not confirmed_participation and not done_result:
            missing.append("Подтвердить участие и поставить результат инспекции")
        else:
            if not confirmed_participation:
                missing.append("Подтвердить участие")
            if not done_result:
                missing.append("Поставить статус инспекции")
    
    comment = ". ".join(missing) if missing else None
    return (None, comment)

async def insp_check(session: aiohttp.ClientSession, link: str, headers: dict) -> tuple[str | None, str | None]:

    url = linkToUrl(link)
    async with session.get(url, headers=headers, ssl=False) as resp:
        data = await resp.json()
    
    # Согласование
    need_sup, done_sup, cancel_sup = parse_supervisor(data)
    # Участие
    need_par, confirmed_par, done_res, cancel_par = parse_representative(data)
    
    return combine_insp(
        need_sup, done_sup, cancel_sup,
        need_par, confirmed_par, done_res, cancel_par
    )
