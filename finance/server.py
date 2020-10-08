from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

import pandas as pd


from .model import MoneyModel

COLORS = {"wallet": "#00AA00", "stock": "#080888"}

COLORS2 = { "total": "#00AA00", 
            "agent1": "#080888",
            "agent2": "#900088",
            "agent3": "#F00F00",
            "agent4": "#9F5858",
            "agent5": "#F88808",
            }

COLORS3 = {
            "amount_agent1": "#080888",
            "amount_agent2": "#900088",
            "amount_agent3": "#F00F00",
            "amount_agent4": "#9F5858",
            "amount_agent5": "#F88808",
            }


amount_chart = ChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS3.items()]
)

tree_chart = BarChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS2.items()]
)


model_params = {
    "height": 100,
    "width": 100,
    "density": UserSettableParameter("slider", "Tree density", 0.65, 0.01, 1.0, 0.01),
}


server = ModularServer(
    MoneyModel, [ amount_chart, tree_chart ], "Finance Agents"
)