import asyncio
import aiohttp
import pandas as pd

# Ваши исходные заголовки
headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiNmMyZjM0YTI5NGU5NWNjNWNmZDFkMGYyMGIyNDQ0YTkxNDUyOTNkMzAxZDhiZmYzYzA2ZDlmNTI0YzUwOTVlOWZkOGFjYzk4MDA2NDAwMTQiLCJpYXQiOjE3MzczOTI1ODMuOTYzNCwibmJmIjoxNzM3MzkyNTgzLjk2MzQwNiwiZXhwIjoxNzM3NDM1NzgzLjgwNzg1NSwic3ViIjoiNDg5Iiwic2NvcGVzIjpbXX0.fJoNBfP1cvOlweeipS7OOCTPtm2ogs86feScLz4lXGVyabced2zd98ZlqWbx_aGQ04HRLU7zc9C-VSrvQs3-wrE6i8FHVQuiiqgPyGZrf-gUfuLftLu9fn95Nw5mbY519W4VDGGIaJlhatpHKJvbC-QZA36yiupCZpOacitgt21uZ_EGYv0vxGKru9l19bsrS8C-btxANPaVkdwFsVq3uzXOagNGFF3SnYOV9CEqopXo-wdYY26iUM9-6RPeQok-yyx1y6Meotg1-vSe9SNy9iwYq3yDpubrdiKq2_hvFC5rxSPHOWn2RLPrCDVHS-hQF2IYXffc-D0Z8TvaPu-AtxNKWbnD2C1MhlEwkapp-6jap34F1OWp708vYOv3Bnik8MocyrDojKtBaHjIzY13mrnKne4RR-p-sLGtog_Hdwp-aOaPZ-NBoiRNxMqALFbPvfqmbrXvEzBNKWR35M_8F0vh-k4b4sNJ6GJ2W9bQPDtS5voV_4HIEU-A3Om8dWJz3ozHoRmd4MC8Z3JzvT4d6u2BSkb9lenAtihuIDaqhlMffB-TZJLx4bq0I4iWvny0LXHzN2V6vlRp70eUuG8r_Dn1RB3dUsp7FOk1FFvh-WwHxLlJh48Ac7yOFlXbKIDXr8XSiovK5Ubj1BYmTd1Nx4T0SYmSt3QEtn9_gCw_cVM',
}

BASE_URL = "https://adept.irkutskoil.ru/api/companies/2/organization/16/tasks"
PARAMS = "?page={page}&count=100&search=&isMyTasks=false"

SEM = asyncio.Semaphore(5)  # максимум 5 запросов одновременно

async def fetch_json(session, url):
    async with SEM:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
        

async def get_tasks_data():

    async with aiohttp.ClientSession(headers=headers) as session:
        # Сначала получим первую страницу, чтобы узнать количество страниц
        url_page1 = BASE_URL + PARAMS.format(page=1)
        data = await fetch_json(session, url_page1)
        
        max_pages = int(data['paginate']['lastPage'])
        df_main = pd.json_normalize(data['tasks'], max_level=1)

        tasks = []
        for page_num in range(2, max_pages + 1):
            url = BASE_URL + PARAMS.format(page=page_num)
            tasks.append(fetch_json(session, url))

        results = await asyncio.gather(*tasks)

        for res in results:
            df_load = pd.json_normalize(res['tasks'], max_level=1)
            df_main = pd.concat([df_main, df_load], ignore_index=True)

        return df_main

def main():
    df = asyncio.run(get_tasks_data())
    df.to_pickle("data.pkl")
    print("Сохранено в data.pkl")
    print(df)

if __name__ == "__main__":
    main()