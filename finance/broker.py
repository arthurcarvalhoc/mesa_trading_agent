class BrokerAgent:
    """ Agente do tipo Broker que retem as informações dos dados
        da Bovespa
    """
    def __init__(self, data):
        self.stocks = data
        self.global_stocks = {item: 10000 for item in list(self.stocks["CODNEG"].unique())}

    def get_stocks(self):
        return self.stocks

    def get_stocks_by_date(self, ref_date, selected_stocks):

        temp = self.stocks.loc[self.stocks["DATAPREGAO"] <= ref_date]
        return temp.loc[temp["CODNEG"].isin(selected_stocks)]

    def get_global_stocks(self):
        return self.global_stocks  