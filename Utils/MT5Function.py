import MetaTrader5 as mt5
import pandas as pd
from ta import momentum, trend


class MT5Function:
    def __init__(self, account):
        
        self.account = account
        
        # if not mt5.initialize(login=self.account, server=self.server, password=self.password):
        #     print("initialize() failed")
        #     mt5.shutdown()

    def connect(self, account, server, password):
        result = mt5.initialize(login=account, password=password, server=server)

        if result == True:
            self.account = account
            self.password = password
            self.server = server
        
        return result


    def order(self, symbol, volume, buysell, slpercent, tppercent, magic, comment):
        if buysell == "buy":
            ordertype = mt5.ORDER_TYPE_BUY
        elif buysell == 'sell':
            ordertype = mt5.ORDER_TYPE_SELL

        price = mt5.symbol_info_tick(symbol).ask
        sl = self.getSL(symbol, buysell, slpercent)
        tp = self.getTP(symbol, buysell, tppercent)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": ordertype,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 0,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        order = mt5.order_send(request)
        
        return order

    def getSL(self, symbol, buysell, percentage):
        info_tick = mt5.symbol_info_tick(symbol)
        sl = 0

        if buysell == "buy":
            sl = info_tick.bid * (1 - percentage)

        elif buysell == "sell":
            sl = info_tick.ask * (1 + percentage)

        return sl

    def getTP(self, symbol, buysell, percentage):
        info_tick = mt5.symbol_info_tick(symbol)
        tp = 0

        if buysell == "buy":
            tp = info_tick.bid * (1 + percentage)

        elif buysell == "sell":
            tp = info_tick.ask * (1 - percentage)


        return tp

    def closeAll(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        for i in range(len(positions)):
            mt5.Close(symbol, ticket=positions[i][0])

    def closePosition(self, symbol, position):
        positions = mt5.positions_get(symbol=symbol)

        for i in range(len(positions)):
            if position == "buysell":
                mt5.Close(symbol, ticket=positions[i][0])                

            if position == "buy":
                if positions[i].type == 0:
                    mt5.Close(symbol, ticket=positions[i][0])

            if position == "sell":
                if positions[i].type == 1:
                    mt5.Close(symbol, ticket=positions[i][0])

    def closePositionTicket(self, symbol, ticket):
        mt5.Close(symbol=symbol, ticket=ticket)

        




    def positions_total(self):
        return mt5.positions_total()
    
    def positions_get(self, symbol):
        if symbol == '':
            return mt5.positions_get()
        else:
            return mt5.positions_get(symbol=symbol)

    def positions_count(self, symbol, buysell):
        positions = mt5.positions_get(symbol=symbol)
        cnt = 0
        
        if buysell == "buy":
            for i in range(len(positions)):
                if positions[i].type == 0:
                    cnt += 1

        elif buysell == "sell":
            for i in range(len(positions)):
                if positions[i].type == 1:
                    cnt += 1

        return cnt



    def getOHLC(self, symbol, timeframe, count):
        if timeframe == 1:
            timeframe = mt5.TIMEFRAME_M1
        elif timeframe == 5:
            timeframe = mt5.TIMEFRAME_M5
        elif timeframe == 15:
            timeframe = mt5.TIMEFRAME_M15
        elif timeframe == 60:
            timeframe = mt5.TIMEFRAME_H1
        elif timeframe == 240:
            timeframe = mt5.TIMEFRAME_H4

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        return rates_frame

    def getRSI(self, df, window):
        return momentum.RSIIndicator(close=df['close'], window=window, fillna=False).rsi()

    def getRSISMA(self, df, window):
        return trend.sma_indicator(close=df['RSI'], window=window)

    def getCCI(self, df, window):
        return trend.CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=window).cci()


    def getCCISMA(self, df, window):
        return trend.sma_indicator(close=df['CCI'], window=window)

    def getOrdertype(self, symbol):
        position = mt5.positions_get(symbol=symbol)

        if position[0].type == 0:  # Buy
            return 1
        elif position[0].type == 1:  # Sell
            return -1

    def account_info(self):

        return mt5.account_info()





