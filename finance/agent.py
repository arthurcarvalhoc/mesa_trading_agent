from mesa import Agent, Model
from mesa.time import RandomActivation
import statistics

class BrokerAgent:
    def __init__(self, data):
        self.stocks = data
        self.global_stocks = {item: 10000 for item in list(self.stocks["CODNEG"].unique())}

    def get_stocks(self):
        return self.stocks

    def get_stocks_by_date(self, ref_date, selected_stocks):
        #return self.stocks.loc[self.stocks["DATAPREGAO"] <= ref_date]

        temp = self.stocks.loc[self.stocks["DATAPREGAO"] <= ref_date]
        return temp.loc[temp["CODNEG"].isin(selected_stocks)]

    def get_global_stocks(self):
        return self.global_stocks

class TradingAgent:
    def __init__(self, broker, unique_id, strategy ):
        # agente broker
        self.broker = broker

        self.unique_id = unique_id

        self.strategy = strategy

        self.memory = []

        self.posicao = ''

        self.operations = 0

        # inicializa portfólio
        self.stocks = {item: 0 for item in list(self.broker.get_stocks()["CODNEG"].unique())}

        # valor de investimento inicial
        self.trading_amount = 10000

        # valor total da carteira
        self.portfolio_profit = {item: 0 for item in list(self.broker.get_stocks()["CODNEG"].unique())}

        
    def working_date(self, ref_date):
        self.ref_date = ref_date

    def working_stocks(self, selected_stocks):
        self.selected_stocks = selected_stocks

    def get_stocks(self):
        return self.broker.get_stocks_by_date(self.ref_date, self.selected_stocks)


class TradingAgentSimple(TradingAgent):

    def buy_stock(self, buy_data, qty):
        final_price = buy_data["PREULT"] * qty

        # se houver dinheiro
        if final_price < self.trading_amount:

            self.operations += 1

            # adiciona qtde no portifolio
            self.stocks[buy_data["CODNEG"]] += qty 
            # desconta o valor da compra do amount
            self.trading_amount -= final_price 

            # atualiza a carteira
            # valor = total de acoes no portfolio * valor de ultima negociacao
            self.portfolio_profit[buy_data["CODNEG"]] = self.stocks[buy_data["CODNEG"]] * buy_data["PREULT"]
            
            print('{} \t Agente: {}\t < COMPRA > \t {} \t SMA7 = {:.2f} \t SMA14 = {:.2f}'.format(buy_data["DATAPREGAO"], self.unique_id, buy_data["CODNEG"], buy_data["SMA7"], buy_data["SMA14"]))
        

    def sell_stock(self, sell_data, qty):
        final_price = sell_data["PREULT"] * qty

        # remove qtde no portifolio
        self.stocks[sell_data["CODNEG"]] -= qty 
        self.operations += 1
        
        # retorna o valor da venda do amount
        self.trading_amount += final_price 

        # atualiza a carteira
        # valor = total de acoes no portfolio * valor de ultima negociacao
        self.portfolio_profit[sell_data["CODNEG"]] = self.stocks[sell_data["CODNEG"]] * sell_data["PREULT"]
            
        print('{} \t Agente: {} \t < VENDA > \t {} \t SMA7 = {:.2f} \t SMA14 = {:.2f}'.format(sell_data["DATAPREGAO"], self.unique_id, sell_data["CODNEG"], sell_data["SMA7"], sell_data["SMA14"]))
    

    # cruzamento de medias moveis
    def main_strategy(self):
        # pegando os dados do papel
        hist_data = self.get_stocks()
        
        # verificando o valor atual da ação 
        temp_data = hist_data.loc[hist_data["DATAPREGAO"] == self.ref_date]

        for index, row in temp_data.iterrows():
            if row["SMA7"] > row["SMA14"]:
                # executa compra
                self.buy_stock(row, 100)
            else:
                self.sell_stock(row, 100)

     # padrões gráficos
    def pattern_strategy(self):
        # pegando os dados do papel
        hist_data = self.get_stocks()
        
        # verificando o valor atual da ação 
        temp_data = hist_data.loc[hist_data["DATAPREGAO"] == self.ref_date]

        for index, row in temp_data.iterrows():
            if row["candlestick_pattern"] == 'CDLCLOSINGMARUBOZU_Bear':
                # executa compra
                self.buy_stock(row, 100)
            if row["candlestick_pattern"] == 'CDLCLOSINGMARUBOZU_Bull':
                self.sell_stock(row, 100)


     # retorno à medias moveis
    def bollinger_strategy(self):
        # pegando os dados do papel
        hist_data = self.get_stocks()
        
        # verificando o valor atual da ação 
        temp_data = hist_data.loc[hist_data["DATAPREGAO"] == self.ref_date ]

        for index, row in temp_data.iterrows():
            self.memory.append(row["PREULT"])
            if len(self.memory) > 14:
                sd = statistics.stdev(self.memory[-14:])

                if( row["PREULT"] > row["SMA14"] + (2 * sd) ):
                    self.sell_stock(row, 200)
                    self.posicao = 'v'

                if( row["PREULT"] < row["SMA14"] - (2 * sd) ):
                    self.buy_stock(row, 200)
                    self.posicao = 'c'

                if( row["PREULT"] >= row["SMA14"] and self.posicao == 'c' ):
                    self.buy_stock(row, 200)
                    self.posicao = ''  

                if( row["PREULT"] <= row["SMA14"] and self.posicao == 'v' ):
                    self.buy_stock(row, 200)
                    self.posicao = ''  
                
                
                
        
            
       
