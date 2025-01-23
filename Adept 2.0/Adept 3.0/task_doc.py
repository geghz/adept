import aiohttp
import re

SEARCH_ORG = 'ООО "ИФ ИнтерГазСервис"'

import re

def linkToUrl(link: str) -> str:
    numbers = re.findall(r'\b\d+\b', link)
    if not numbers or len(numbers) < 2:
        return ""  # или вернуть None, если не можем распарсить

    object_id = numbers[0]
    doc_or_folder_id = numbers[-1]

    if 'folder=' in link:
        type_id = 'document-folder'
    else:
        type_id = 'document'

    url = f"https://adept.irkutskoil.ru/api/objects/{object_id}/{type_id}/{doc_or_folder_id}/agreements"
    return url



async def doc_check(
    session: aiohttp.ClientSession,
    link: str,
    headers: dict,
    engineer_fio: str | None = None
) -> tuple[str | None, str | None]:

    url = linkToUrl(link)
    async with session.get(url, headers=headers, ssl=False) as resp:
        data = await resp.json()

    agreements = data.get('agreements', [])
    if not agreements:
        return (None, "Нет согласования")

    # Собираем подписантов организации
    all_org_signers = collect_all_org_signers(agreements, SEARCH_ORG)
    if not all_org_signers:
        return (None, "Нет в подписантах")

    if engineer_fio:
        engineer_signers = filter_signers_by_fio(all_org_signers, engineer_fio)
        if engineer_signers:
            last_signer = max(engineer_signers, key=lambda s: s["stage_index"])
            return analyze_last_signer(last_signer)
        else:
            return fallback_check(all_org_signers, missing_fio=engineer_fio)
    else:
        return fallback_check(all_org_signers)


def collect_all_org_signers(agreements: list[dict], org_name: str) -> list[dict]:

    results = []
    for idx, ag in enumerate(agreements):
        parts = ag.get('parts', [])
        is_started = bool(ag.get('is_started', False))
        stage_status = ag.get('stage')  # Напр. 'active', 'closed', ...
        for p in parts:
            rep = p.get('responsible')
            if not rep:
                continue
            partner = rep.get('partner', {})
            if partner.get('name') == org_name:
                fio_val = rep.get('fio', "").strip()
                name_val = rep.get('name', "").strip() 
                sign = bool(p.get('responsible_sign'))
                results.append({
                    "fio": fio_val,
                    "name": name_val,
                    "stage_index": idx,
                    "responsible_sign": sign,
                    "is_started": is_started,
                    "stage_status": stage_status
                })
    return results


def filter_signers_by_fio(signers: list[dict], engineer_fio: str) -> list[dict]:
    ef = engineer_fio.strip()
    matches = []
    for s in signers:
        if ef == s["fio"] or ef == s["name"]:
            matches.append(s)
    return matches


def analyze_last_signer(signer: dict) -> tuple[str | None, str | None]:

    if signer["responsible_sign"]:
        return ("Выполнена", None)

    stage_status = signer["stage_status"]   # напр. 'active', 'closed'
    is_started = signer["is_started"]       # bool

    if not is_started and stage_status not in ["active"]:
        return (None, "Этап завершён/не запущен без подписи")
    elif stage_status == "closed":
        return (None, "Этап закрыт без подписи")
    else:
        return (None, "Поставить ЭЦП")


def fallback_check(signers: list[dict], missing_fio: str | None = None) -> tuple[str | None, str | None]:

    active = []
    for s in signers:
        if s["stage_status"] == "active" or s["is_started"]:
            active.append(s)

    if not active:
        # Ни одного активного => всё закрыто/не запущено
        if missing_fio:
            return (None, f"Инженер '{missing_fio}' не найден. Согласование закрыто/не запущено.")
        else:
            return (None, "Согласование закрыто/не запущено.")

    # Нужно, чтобы все active имели подпись
    if all(s["responsible_sign"] for s in active):
        return ("Выполнена", None)

    # Иначе найдём, кто не подписал
    missing_list = [f"{x['fio'] or x['name']}" for x in active if not x["responsible_sign"]]
    missing_str = ", ".join(set(missing_list))

    if missing_fio:
        return (None, f"Нет подписи: {missing_str}")
    else:
        return (None, f"Нет подписи: {missing_str}")
