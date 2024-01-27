import json
import os

from crewai import Agent, Task, Crew
from langchain_core.tools import tool
from requests import get
import ast

os.environ["OPENAI_API_KEY"] = "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"

from langchain.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()


class readTool():
    @tool("Read the Dataset")
    def read(self):
        """read the dataset containing list of news articles, crypto prices and price change
        for the 6 hours after article was posted. This data should help you estimate how
        much did the news article affect the cryptocurrency exchange rate. If the price reducing - news are bad for currency."""
        with open('export_data.json', 'r') as f:
            data = json.load(f)
        i = 0
        lists = list(data['data'])

        lists[0] = {'inf'}
        try:
            for row in data['data']:
                print(row['Influence'])
            positive = [row for row in data['data'] if float(row['Influence']) > 0]
            negative = [row for row in data['data'] if float(row['Influence']) < 0]
        except Exception as er:
            print(er)


        positive.sort(key=fu)
        negative.sort(key=fu, reverse=True)

        res = []
        x = 0
        prices = []

        for row in negative:
            if row['Influence'] not in prices:
                prices.append(row['Influence'])
                x+=1

        counter_prices = 0
        while len(res) < 3:
            for minusitem in negative:
                if counter_prices < 4:
                    cur_price = prices[counter_prices]
                    counter_prices+=1
                else:
                    counter_prices=0
                    cur_price = prices[counter_prices]

                if minusitem['Influence']==cur_price and minusitem not in res:
                    res.append(minusitem)

                    if len(res)>9:
                        return res

        return res


def fu(e):
    return e['Influence']


class CurrencyTool():

    @tool("Get currency difference for the time period. Input format: {'coin_id': 'bitcoin', 'days': 7}. Replace 'days' value"
          "with provided days amount, replace the 'coin_id' value with provided currency coingecko id"
          "if necessary.")

    def get_json_currency(self: str):
        "Input format dict. {'coin_id': currency-coingecko-id, 'days': int-amount-of-days}"

        dict_input = ast.literal_eval(self)
        coin_id = dict_input['coin_id']
        days = dict_input['days']
        vs_currency = "usd"

        api_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"
        response = get(api_url)

        if response.status_code == 200:
            data = response.json()
            return {"start price": data['prices'][0], "end price": data['prices'][-1]}
        else:
            print(f"Ошибка при выполнении запроса: {response.status_code}")


executor = Agent(
    role='''Manager''',
    goal='''Provide an answer to the question''',
    backstory='''
        You have the instruments to read the currency related news articles in correlation 
        with currency price changes and estimated persentage of influence the articles had
        on the currency price; instrument to get the currency price change for the provided
        period: amout of days, and coingecko coin_id, which are passed to the tool as the 
        dict of parameters. Using all the provided instruments answer the question defined 
        in your task. Use serach_tool to read the news more, try to disprove provided news.
        Replace the news with valid from the internet if necessary. use serach_tool. DO NO VERIFY ARTICLES
        SEARCH FOR NEW ONES. try and expand on the subject, find some additional data
         and comare it to the data mentioned in the dataset. 
    ''',
    verbose=True,
    allow_delegation=False,
    tools=[readTool.read, CurrencyTool.get_json_currency, search_tool]
)

execute = Task(
    description='Tell me how much did the bitcoin price change for the past 7 days? Explain why based on the related news and price dynamic at the time provided by the given tools. List the news, provide explanation afterwards. Disprove incorrect news.',
    agent=executor
)


crew = Crew(
    agents=[executor],
    tasks=[execute],
    verbose=2
)

result = crew.kickoff()

print("######################")
print(result)