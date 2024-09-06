import pandas as pd

def historic_cdi() -> pd.Series:
    """
    Baixa os dados históricos do Banco Central em relação ao rendimento do CDI. 
    """
    api = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json'

    response = pd.read_json(api)

    cdi = response.set_index('data').squeeze()
    cdi.index = pd.to_datetime(cdi.index, dayfirst=True).date
    
    cdi_returns = (1 + (cdi / 100)).cumprod()

    return cdi_returns
