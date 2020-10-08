from mesa import Agent, Model
from mesa.time import RandomActivation
import matplotlib as plt
import pandas as pd
import numpy as np
import backtrader as bt
from mesa.datacollection import DataCollector
from .agent import TradingAgentSimple, BrokerAgent

class MoneyAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, list_stocks, strategy = 'main'):
        super().__init__(unique_id, model)
        
        self.strategy = strategy 
        self.broker = BrokerAgent(self.model.dados)
        self.simple_agent = TradingAgentSimple(self.broker, unique_id, strategy)
        self.simple_agent.working_stocks(list_stocks)
        self.amount = 10000
        self.operations = 0
        

    def step(self):
        # obtem o dia útil do modelo
        day = None
        if len(self.model.days) > self.model.count:
            day = self.model.days[self.model.count]

        #print("Valor disponível para investimentos:", self.simple_agent.trading_amount)
        #print("Valorização da carteira:", sum(self.simple_agent.portfolio_profit.values()))
        
        #print("Data - Tipo Op. - Sigla - SMA7 - SMA14 \n")

        if day is not None:
            self.simple_agent.working_date(day)

            if self.strategy == 'pattern':
                self.simple_agent.pattern_strategy()
            if self.strategy == 'main':
                self.simple_agent.main_strategy()
            if self.strategy == 'bollinger':
                self.simple_agent.bollinger_strategy()

        self.amount = sum(self.simple_agent.portfolio_profit.values()) + self.simple_agent.trading_amount
        self.operations = self.simple_agent.operations

        if day is not None and day.day == 1 :
            print('\n####### AGENTE {} ########'.format(self.unique_id))
            print("Valor disponível para investimentos:", self.simple_agent.trading_amount)
            print("Valor da carteira:", sum(self.simple_agent.portfolio_profit.values()))
            print("Valorização total: ", sum(self.simple_agent.portfolio_profit.values()) + self.simple_agent.trading_amount)
            

class MoneyModel(Model):
    """A model with some number of agents."""
    def __init__(self):        
        self.schedule = RandomActivation(self)
        self.running = True
        
        self.dados, self.days = self.setup()
        self.count = 0


        a = MoneyAgent(5, self, ["VALE3"], 'bollinger')
        self.schedule.add(a)

        a = MoneyAgent(4, self, ["ITSA4", "BBDC4"], 'pattern')
        self.schedule.add(a)

        a = MoneyAgent(3, self, ["MGLU3", "VVAR3"], 'pattern')
        self.schedule.add(a)


        a = MoneyAgent(2, self, ["ITSA4", "BBDC4"])
        self.schedule.add(a)

        a = MoneyAgent(1, self, ["MGLU3", "VVAR3"])
        self.schedule.add(a)

         # see datacollector functions above
        self.datacollector = DataCollector(            {
                
                "agent1": lambda m: self.count_type(m, 1),
                "agent2": lambda m: self.count_type(m, 2),
                "agent3": lambda m: self.count_type(m, 3),
                "agent4": lambda m: self.count_type(m, 4),
                "agent5": lambda m: self.count_type(m, 5),
                "amount_agent1": lambda m: self.amount(m, 1),
                "amount_agent2": lambda m: self.amount(m, 2),
                "amount_agent3": lambda m: self.amount(m, 3),
                "amount_agent4": lambda m: self.amount(m, 4),
                "amount_agent5": lambda m: self.amount(m, 5)
            }
        )
        self.datacollector.collect(self)

    def step(self):
        '''Advance the model by one step.'''
        self.count = self.count + 1
        self.schedule.step()
        self.datacollector.collect(self)

    def setup(self):
        print('loading data ...')
        dados = pd.read_csv("finance/data/acoes_indice_bovespa_indicadores.csv")
        dados["DATAPREGAO"] = pd.to_datetime(dados['DATAPREGAO'])

        start_at = pd.to_datetime("2019-01-15")
        end_at = pd.to_datetime("2019-12-31")

        days = list(pd.date_range(start_at, end_at))

        return dados, days

    @staticmethod
    def count_type(model, a):       
        count = 0
        for agent in model.schedule.agents:            
            if agent.unique_id == a:                
                return agent.operations 
            count += agent.operations 
        return count

    @staticmethod
    def amount(model, a):       
        count = 0
        for agent in model.schedule.agents:            
            if agent.unique_id == a:                
                return abs(agent.amount) 
            count += agent.amount 
        return abs(count)