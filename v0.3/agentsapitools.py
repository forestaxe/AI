from requests import get
import json
from datetime import datetime, date, timedelta


def get_json_news(coin: str):
    url = 'https://newsapi.org/v2/everything'
    params = {
        "q": f"{coin}",
        "from": f"{date.today() - timedelta(days=7)}",
        "to": f"{date.today()}",
        "sortBy": "publishedAt",
        "apiKey": "84ef5e832ed0476094f149843aac48af"
    }

    response = get(url, params=params)

    if response.status_code == 200:
        json_data = response.json()
        with open('response.json', 'w') as file:
            json.dump(json_data, file, indent=4)
        print(json_data)
    else:
        print(f"Failed to get data. Status code: {response.status_code}")


def get_json_currency(coin_id: str, days: int):
    vs_currency = "usd"

    api_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"
    response = get(api_url)

    if response.status_code == 200:
        data = response.json()
        reformatted_data = reformat_json_data(data)
        with open('rfmt_response_prices.json', 'w') as f:
            json.dump(reformatted_data, f, indent=4)
    else:
        print(f"Ошибка при выполнении запроса: {response.status_code}")


def reformat_json_data(json_data):
    reformatted_data = []
    for item in json_data['prices']:
        print(type(item[0]))

        timestamp = item[0] / 1000  # Получаем временную метку из исходных данных в сек из мс
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

        price = item[1]
        reformatted_data.append([date, price])

    return reformatted_data


def calculate_datetime_range():
    with open('response.json', 'r') as f:
        news_data = json.load(f)

    with open('rfmt_response_prices.json', 'r') as f:
        prices_data = json.load(f)

    data = []
    prices_dates = []

    for time in prices_data:
        prices_dates.append(datetime.strptime(time[0], "%Y-%m-%d %H:%M"))

    with open('export_data.json', 'w') as file:
        try:
            for m in range(10000):
                article = news_data['articles'][m]
                published_src = datetime.strptime(news_data['articles'][m]['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                publishedDate = (published_src + timedelta(hours=1)).replace(minute=0, second=0)

                if publishedDate < datetime.strptime('2000-01-01', '%Y-%m-%d'):
                    continue

                dates = (publishedDate - timedelta(hours=1), publishedDate + timedelta(hours=5))
                dateRange = [dates[0] + timedelta(hours=i) for i in range(6)]
                print(dateRange, news_data['articles'][m]['publishedAt'], dates)

                price_range = {}
                for date in dateRange:
                    if date in prices_dates:
                        for item in prices_data:
                            price = item[1]
                            date_item = item[0]

                            if date_item == date.strftime("%Y-%m-%d %H:%M"):
                                price_range.update({date_item: price})

                ranges = [i for i in price_range.values()]
                first = ranges[0]
                last = ranges[-1]

                payload = {"Article": article}
                payload.update({"Prices": price_range.copy()})
                payload.update({"Influence": "{:.4f}".format(float(((first - last) / first) * 100))})

                data.append(payload)

        except IndexError as e:
            print(e)
            x = {"data": data}
            json.dump(x, file, indent=4)


get_json_currency(coin_id="bitcoin", days=30)
get_json_news("bitcoin")

calculate_datetime_range()
