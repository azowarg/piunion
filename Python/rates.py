import requests as re
import time

kraken_api_url = "https://api.kraken.com/0"
flatqube_api_url = "https://api.flatqube.io/v1"
crb_api_url = "https://www.cbr-xml-daily.ru/"


def kraken_get_rates(pair: str) -> float:
    """
    Get rates for the pair from Kraken public API
    Kraken public API doc https://docs.kraken.com/rest/
    json data
    (str) -> num
    """
    parameters = {"pair": pair, "since": int(time.time())}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; '
               'Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'}

    response = re.get(kraken_api_url + "/public/OHLC",
                      params=parameters, headers=headers)
    if not response.ok:
        print("Server don't response")
        return
    pair_rate = response.json()['result'][pair][0][3]
    return float(pair_rate)


def flatqube_get_rates(base_id: str) -> float:
    """
    Get rates for the pair from flatqube public API
    You can get base_id from https://api.flatqube.io/v1/cmc/dex
    json data
    (str) -> num
    """
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; '
               'Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'}

    response = re.post(flatqube_api_url + "/currencies/" + base_id,
                       headers=headers)
    if not response.ok:
        print("Server don't response")
        return
    rate = response.json()['price']
    return float(rate)


def cb_get_rates(currency: str) -> float:
    """
    Get rates from central bank site
    json data
    (str) -> num
    """
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; '
               'Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'}

    response = re.get(crb_api_url + "/daily_json.js", headers=headers)
    if not response.ok:
        print("Server don't response")
        return
    rate = response.json()['Valute'][currency]['Value']
    return float(rate)
