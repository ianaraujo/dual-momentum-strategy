import warnings
import requests
import pandas as pd
import numpy as np
import yfinance as yf

from datetime import datetime
from typing import Optional


STAR_DATE = '2004-01-01'
END_DATE = datetime.today().strftime('%Y-%m-%d')


def historic_cdi(start: Optional[str] = None, end: Optional[str] = None) -> pd.Series:
    """
    Baixa os dados históricos do Banco Central em relação ao rendimento do CDI. 
    """
    api = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json'

    try:
        response = requests.get(api)
        response.raise_for_status()

        data = response.json()
    
    except requests.HTTPError as e:
        raise e

    cdi = pd.DataFrame(data)

    cdi = cdi.set_index('data')
    cdi.index = pd.to_datetime(cdi.index, dayfirst=True).date

    if start:
        start = datetime.strptime(start, '%Y-%m-%d').date()
        cdi = cdi.loc[cdi.index >= start]

    if end:
        end = datetime.strptime(end, '%Y-%m-%d').date()
        cdi = cdi.loc[cdi.index <= end]

    cdi = cdi.sort_index()
    
    cdi_returns = (1 + (cdi.astype(float) / 100)).cumprod()
    cdi_returns = (cdi_returns / cdi_returns.iloc[0])

    return cdi_returns.squeeze()


def historic_imab5(start: Optional[str] = None, end: Optional[str] = None) -> pd.Series:
    """
    Baixa os dados históricos da ANBIMA em relação ao rendimento do índica IMA-B 5. 
    """
    historico = 'https://adata-precos-prod.s3.amazonaws.com/arquivos/indices-historico/IMAB5-HISTORICO.xls'

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data = pd.read_excel(historico)

    imab = data[['Data de Referência', 'Número Índice']]
    
    imab = imab.set_index('Data de Referência')
    imab.index = pd.to_datetime(imab.index).date

    if start:
        start = datetime.strptime(start, '%Y-%m-%d').date()
        imab = imab.loc[imab.index >= start]

    if end:
        end = datetime.strptime(end, '%Y-%m-%d').date()
        imab = imab.loc[imab.index <= end]

    imab = imab.sort_index()
    
    imab_normalized = (imab / imab.iloc[0])

    return imab_normalized.squeeze()


def historic_sp500(start: Optional[str] = None, end: Optional[str] = None, brl: bool = False) -> pd.Series:
    
    SP500 = yf.Ticker('^GSPC')

    sp500_prices = SP500.history(start=start, end=end)['Close']
    sp500_prices.index = pd.to_datetime(sp500_prices.index).date

    if brl:    

        start = datetime.strptime(start, '%Y-%m-%d').strftime('%m-%d-%Y')
        end = datetime.strptime(end, '%Y-%m-%d').strftime('%m-%d-%Y')

        api = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{start}'&@dataFinalCotacao='{end}'&$format=json"

        try:
            response = requests.get(api)
            response.raise_for_status()

            data = response.json()
    
        except requests.HTTPError as e:
            raise e

        dolar = pd.DataFrame(data['value'])
        dolar = dolar.set_index('dataHoraCotacao')

        dolar.index = pd.to_datetime(dolar.index).date

        sp500_dolar = dolar.join(sp500_prices.to_frame(), how='right')
        
        sp500_dolar['SP500 BRL'] = sp500_dolar['Close'] * sp500_dolar['cotacaoVenda'] 

        return sp500_dolar['SP500 BRL'].squeeze()

    return sp500_prices


if __name__ == '__main__':
    sp500 = historic_sp500(start='2004-01-01', end='2024-09-09', brl=True)
    print(sp500)
