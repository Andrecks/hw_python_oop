from __future__ import annotations
import datetime as dt
from typing import Optional, Union, List
import requests

Datedict = Optional[Union[str, dt.date, None]]
# тип данных, передоваемый в функцию calculate_sum

API_key = '102617f25bb6e1bf867d'  # Ключ API для сайта с курсами валют


class Calculator:
    def __init__(self, limit: int):
        self.limit = limit
        self.records: List[Record] = []

    def get_week_stats(self) -> float:
        week = dt.date.today() - dt.timedelta(days=7)
        sum = self.calculate_sum(date1=week)
        return sum

    def get_today_stats(self) -> float:
        today = dt.date.today()
        sum = self.calculate_sum(date1=today)
        return sum

    def date_format(self, date: str) -> dt.date:
        """Форматируем дату из строки в тип date."""
        date_format = '%d.%m.%Y'
        if (type(date) == dt.date):
            return date
        # splitter = date.split('.')
        self.fixdate = dt.datetime.strptime(date, date_format)
        """ dt.date(day=int(splitter[0]),
                               month=int(splitter[1]),
                               year=int(splitter[2])) """
        return self.fixdate.date()

    def add_record(self, rec: Record):
        """Добавляет запись. В случае отсутвия даты - ставим сегодняшнюю."""
        if rec.date:
            rec.date = self.date_format(rec.date)
        else:
            rec.date = dt.date.today()
        self.records.append(rec)

    def calculate_sum(self, date1: Datedict = None,
                      date2: Datedict = None) -> float:
        records = self.records
        sum: float = 0
        for rec in records:
            if (date1 and date2):
                date1 = self.date_format(date1)
                date2 = self.date_format(date2)
                if(date1 <= rec.date <= date2):
                    sum += rec.amount
            elif(date1 and not date2):
                date1 = self.date_format(date1)
                if (date1 <= rec.date):
                    sum += rec.amount
            elif(date2 and not date1):
                date2 = self.date_format(date2)
                if (date2 >= rec.date):
                    sum += rec.amount
            else:
                sum += rec.amount
        return sum


class CashCalculator(Calculator):

    def __init__(self, limit):
        super().__init__(limit)
        self.USD_RATE = self.get_rate('usd')
        self.EUR_RATE = self.get_rate('eur')

    def get_week_stats(self) -> str:
        return ('За неделю было потрачено ',
                f'{super().get_week_stats()} руб')

    def get_today_stats(self) -> str:
        return ('За сегодня было потрачено ',
                f'{super().get_today_stats()} руб')

    def get_rate(self, cur: str = 'руб') -> float:
        """получаем курс валют с сайта free.currconv.com
        на входе функция принимает код валюты из трех заглавных букв.
        На выходе получаем курс рубля к выбранной валюте. Костыль:
        В случае если переданная валюта - рубль, то возвращаем курс = 1"""
        if (cur in ['rub', 'RUB', 'Руб', 'руб']):
            return 1
        rate: str = ''
        i = 0
        if cur == 'Euro':
            self.cur = 'EUR'
        else:
            self.cur = cur.upper()
        url = 'https://free.currconv.com/api/v7/convert'
        param = f'?q={self.cur}_RUB&compact=ultra&apiKey={API_key}'
        response = requests.get(url + param)
        res = response.text.split(':')[1].strip('}')
        # от строчки типа {"USD_RUB":72.863797} берем часть
        # что идет после символа ":" и убираем символ "}"
        # преобразуем в тип float и таким образом получаем курс валюты
        return (float(res))

    def get_today_cash_remained(self, currency: Optional[str] = 'руб') -> str:
        self.currency = currency
        sum = self.calculate_sum(date1=dt.date.today())
        # Тут считаем сумму потраченных средств за сегодня
        sum /= self.get_rate(currency)
        # и переводим в нужную нам валюту
        n = self.limit / self.get_rate(currency)
        # Тут переводим наш лимит в нужную валюту

        if sum < n:

            return (f"На сегодня осталось {round((n - sum), 2)} {currency}")

        elif sum == n:

            return ('Денег нет, держись')

        else:

            return ('Денег нет, держись: твой долг - ',
                    f'{round(sum - n, 2)} {currency}')

class CaloriesCalculator(Calculator):
    def __init__(self, limit):
        super().__init__(limit)

    def get_calories_remained(self) -> str:
        sum = self.calculate_sum()
        n = self.limit - sum
        if (sum > self.limit):
            return ('Хватит есть!')
        else:
            return ('Сегодня можно съесть что-нибудь ещё, ',
                    f'но с общей калорийностью не более {n} кКал')

    def get_week_stats(self) -> str:
        return ('За неделю было сьедено ',
                f'{super().get_week_stats()} Ккал')

    def get_today_stats(self):
        return ('За сегодня было съедено ',
                f'{super().get_today_stats()} Ккал')


class Record:
    def __init__(self, amount: float, comment: Optional[str],
                 date: Optional[dt.date] = None) -> None:
        self.amount = amount
        self.date = date
        self.comment = comment
        