import json, asyncio, requests, pprint, aiohttp, time, pandas, matplotlib.pyplot as plt
from numpy.core.defchararray import title
from requests.models import Response
from requests.sessions import PreparedRequest


class Crypto: 
    def __init__ (self, id, name):
        self.id = id
        self.price_list = []
        self.name = name 
        self.rsi_value = None
        self.mooving_average_value = None

    async def get_periods(self, nb_periods):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={self.name}&tsym=USD&limit={nb_periods}&api_key=4a6601d2ebd6b909fdd91bbfc7f45016438a536204390ee6bbb01f30e2cee65b") as response:
                json = await response.json()
                if json["Response"] == "Success":
                    data = json["Data"]["Data"]

                    for period in data:
                        self.price_list.append(period["close"])
                else:
                    print(json["Message"])
    
    @property
    def mooving_average(self):
        if self.mooving_average_value is None:
            if len(self.price_list) != 0:
                return sum(self.price_list) / len(self.price_list)
            return "NaN"
        return self.mooving_average_value
    
    @property
    def rsi(self, periods=14, ema = True):
        if self.rsi_value is None:
            df = pandas.DataFrame(self.price_list)
            close_delta = df.diff()
            
            up = close_delta.clip(lower=0)  
            down = -1 * close_delta.clip(upper=0)

            if ema == True:
                ma_up = up.ewm(com = periods -1, adjust=True, min_periods = periods).mean()
                ma_down = down.ewm(com = periods -1, adjust=True, min_periods = periods).mean()
            else:
                ma_up = up.rolling(window=periods).mean()
                ma_down = down.rolling(window=periods).mean()
            
            rsi = ma_up / ma_down
            rsi = 100 - (100/(1 + rsi))
            
            #rsi.plot(title=self.name)
            #plt.show()
            self.rsi_value = round(rsi[0].iloc[-1], 2)

        return self.rsi_value

    def is_ready(self, indicator):
        if self.price_list:
            if indicator == "RSI":
                if self.rsi < 50:
                    return True
            if indicator == "MA":
                if abs(self.mooving_average - self.price_list[-1]) / self.price_list[-1] < 0.05:
                    return True
            if indicator == "ALL":
                if self.rsi < 50 and abs(self.mooving_average - self.price_list[-1]) / self.price_list[-1] < 0.05:
                    return True
        return False

    @staticmethod
    def create_with_info(info):
        return Crypto(info["Id"], info["Name"])

    def __str__(self):
        return f"{self.name}"