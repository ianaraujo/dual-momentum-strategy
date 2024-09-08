import warnings
import requests
import pandas as pd

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


if __name__ == '__main__':
    imab = historic_imab5()
    print(imab)