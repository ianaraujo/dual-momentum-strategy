import pandas as pd

def historic_cdi(start: str = '01/07/1994', end: str = '01/07/2024') -> pd.Series:
    """
    Baixa os dados históricos do Banco Central em relação ao rendimento do CDI. 
    """
    api = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={start}&dataFinal={end}'

    response = pd.read_json(api)

    cdi = response.set_index('data').squeeze()
    cdi.index = pd.to_datetime(cdi.index, dayfirst=True).date
    
    cdi_returns = (1 + (cdi / 100)).cumprod()
    cdi_returns = (cdi_returns / cdi_returns.iloc[0])

    return cdi_returns
