import asyncio
import aiohttp

import task_remark
import task_prescriptions
import task_arvk
import task_r6
import task_insp
import task_doc

headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiN2QyMTcyM2UyNzFiYTkwNWFhYTgxMTMxMzZkNTM5YjI1YWI1N2RmNTQxZWYyNDU3MTQxY2ViNWUxMTBlZTVlODU5OTcwYWI5MDI4MzIyMDkiLCJpYXQiOjE3Mzc2MDY2NDUuNjE4OTQ0LCJuYmYiOjE3Mzc2MDY2NDUuNjE4OTUsImV4cCI6MTczNzY0OTg0NS40ODUwNiwic3ViIjoiNDg5Iiwic2NvcGVzIjpbXX0.FGJSHvHGKgHReZNNME7KZMYM1s-WjcgwbdLTN6jj4iDE0RTNpw3LeDxb5zCPQsiOQRC0V4ue4Dvu1mBC0EOJlgfgJugDdKT4qMFhfUTcS0LSaTW2Gr7AL19JF2yHr5_nc2u9ykpkto7l-y5wMUnj-Xe2AOpbzo93e4M5RcWM38Z58iQAVCCOYElf27zdNDehqxtTrE-yue4tF5c3OWdRzS3ejyV7HDaLT7ZTkaaFRGl2nMv0Yq0sRWbKcD8wuD5IygekXYIzxF_xV7n4y1uVECg1cDt_krnBve1XWRhOw-QLdymhmGXF9uU0R4JhnkYPlxBrdLvHWIkdYB861PQ9Ju-yB-qzNpsMd7egiARrslJYm9qHzO7bb6b81TgQY1IdnbGgmczrFX8-1kriuZN5paACePpDosnUgfk6aM5qfAoSvfv-yh_WPRv9CZtHmo6cSBznuuAfQwSPDuMD4x9eOoHWSUh4353LJ9QDdxlGCNzE0e5TusXp8tyzCjX9_OWPe7EqtNOqEtMDLLlBEDktPGIpNG7E3l1pDM67Dd6v7k2ll7Nc7dYYuBecYmzCspb22NwAzz3jBIfC0B79vK-7fmAZNMhC6-qrfbk_xv3frylfAAmthZ6-fsPg01AjghFWP9HyR6tBI3CbmJUFy5t9HqSI4DCTEgA3zveM3nNXacE',
}

async def main():
    module_name = "doc"
    engineer_fio = "Черданцев Дмитрий Витальевич"
    link = "https://adept.irkutskoil.ru/objects/287/docs/tree/0/113593?folder=113594&tab=agreements" 

    async with aiohttp.ClientSession() as session:
        if module_name == "remark":
            status, comment = await task_remark.remark_check(session, link, headers)
        elif module_name == "prescriptions":
            status, comment = await task_prescriptions.prescription_check(session, link, headers)
        elif module_name == "arvk":
            status, comment = await task_arvk.arvk_check(session, link, headers)    
        elif module_name == "r6":
            status, comment = await task_r6.r6_check(session, link, headers)
        elif module_name == "insp":
            status, comment = await task_insp.insp_check(session, link, headers)
        elif module_name == "doc":
            status, comment = await task_doc.doc_check(session, link, headers, engineer_fio)
        else:
            status, comment = (None, f"Неизвестный модуль: {module_name}")

    print(f"Модуль: {module_name}")
    print(f"Ссылка: {link}")
    print(f"Статус: {status}")
    print(f"Комментарий: {comment}")


if __name__ == "__main__":
    asyncio.run(main())
