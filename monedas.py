import re
import requests

from operator import itemgetter
from pprint import pprint
from pyquery import PyQuery as pq
from wikipydia import query_text_rendered


def main():
    currencies = get_curencies()
    get_denominations(currencies)

    get_differences(currencies)
    pprint(sorted(currencies, key=itemgetter(3)))


def get_differences(currencies):
    EXC_URL = "https://www.google.com/finance/converter?a=%s&from=%s&to=USD"

    for currency in currencies:
        print currency
        r = requests.get(EXC_URL % (currency[2], currency[0]))
        query = pq(r.text)
        usd = query(".bld").text()
        if len(usd):
            currency.append(float(usd[:-4]))
        else:
            currency.append(None)
        print currency


def get_denominations(currencies):
    for currency in currencies:
        try:
            page = query_text_rendered(currency[1], "en")
            html = page['html']
            query = pq(html)
            ths = query(".infobox:first th")
            for th in ths.items():
                if "Banknotes" in th.text():
                    parent = th.parent()
                    td_text = parent("td:first").text()

                    if td_text != "":
                        denom_text = td_text
                    else:
                        next = parent.next()
                        denom_text = next("td").text()
                    tmp_denom = re.findall("\d+,?\d+", denom_text)
                    denominations = []
                    for denom in tmp_denom:
                        denom = denom.replace(',', "")
                        int_denom = int(denom)
                        if not int_denom:
                            denominations[-1] += denom
                        else:
                            denominations.append(denom)
                    if len(denominations):
                        currency.append(max([int(d) for d in denominations]))
                    else:
                        currency.append(None)

            print currency
        except KeyError:
            pass

def get_curencies():
    currencies = []
    page = query_text_rendered("List_of_circulating_currencies", "en")
    html = page['html']
    query = pq(html)
    table = query("table:first")
    trs = table("tr")
    for tr in trs:
        tds = tr.findall("td")
        if len(tds):
            iso_code =  tds[-3].text
            link = tds[-5].find("a")
            if link is not None and iso_code is not None:
                url = link.attrib['href'][6:]
                currency = [iso_code, url]
                if currency not in currencies:
                    currencies.append(currency)
    return currencies


if __name__ == '__main__':
    main()
