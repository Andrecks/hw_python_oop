from __future__ import annotations
import datetime as dt
from typing import Optional, List
import requests
from decimal import Decimal
API_key = 'b60b77c46f793211f140'


def get_rate(cur: str = 'RUB') -> float:
    """получаем курс валют с сайта free.currconv.com
    на входе функция принимает код валюты из трех заглавных букв.
    На выходе получаем курс рубля к выбранной валюте. Костыль:
    В случае если переданная валюта - рубль, то возвращаем курс = 1"""
    url = 'https://free.currconv.com/api/v7/convert'
    param = f'?q={cur}_RUB&compact=ultra&apiKey={API_key}'
    response = requests.get(url + param).json()
    res = float(response[f'{cur}_RUB'])
    # получаем json, выбираем нужное нам значение
    # преобразуем в тип float окрунояем до двух знаков
    return round(res, 2)


class Calculator:

    def __init__(self, limit: int):
        self.limit = limit
        self.records: List[Record] = []

    def get_week_stats(self) -> float:
        """Считает сумму портаченных средств за неделю."""
        week = dt.timedelta(weeks=1)
        sum_week = self.calculate_sum(date=week)
        return sum_week

    def get_today_stats(self) -> float:
        """Считает сумму портаченных средств за сегодня."""
        today = dt.timedelta(days=1)
        sum_today = self.calculate_sum(date=today)
        return sum_today

    def add_record(self, rec: Record):
        """Добавляет запись."""
        self.records.append(rec)

    def calculate_sum(self, date: Optional[dt.timedelta]
                      = dt.date.today()) -> float:
        today = dt.date.today()
        records = self.records
        date_dif = dt.date.today() - date
        sum_list: List[float]
        sum_list = [x.amount for x in records if (date_dif < x.date <= today)]
        return sum(sum_list)


class CashCalculator(Calculator):
    USD_RATE = get_rate('USD')
    EURO_RATE = get_rate('EUR')

    def get_today_cash_remained(self, currency: Optional[str] = 'руб') -> str:
        """Считает разницу лимита и суммы затраченных стредств
            в выбранной валюте"""
        cur_dict = {'usd': [self.USD_RATE, 'USD'],
                    'eur': [self.EURO_RATE, 'Euro'],
                    'rub': [1, 'руб']}
        # /\ создаем словарь с курсами валют
        # \/ задаем параметры по умолчанию
        rate = cur_dict[currency][0]
        cur_name = cur_dict[currency][1]
        sum_today = self.get_today_stats()
        # /\ Тут считаем сумму потраченных средств за сегодня
        sum_fin = self.limit - sum_today
        sum_fin /= rate
        # /\ перевели в нужную валюту
        if (Decimal(sum_fin) % 1 == 0):
            sum_fin = sum_fin
        # /\проверяем сумму.
        # /\В случае отсутсвия дробной части - представляем ее целым числом
        # /\дробную часть округляем до двух знаков после точки
        if sum_today < self.limit:

            return (f"На сегодня осталось {sum_fin:.2f} {cur_name}")

        elif sum_today == self.limit:

            return ('Денег нет, держись')

        sum_fin = abs(sum_fin)
        # задолженность выводим как положительное число
        return ('Денег нет, держись: твой долг - '
                + f'{sum_fin:.2f} ' + cur_name)


class CaloriesCalculator(Calculator):

    def get_calories_remained(self) -> str:
        """Считает разницу лимита и суммы
            съеденных килоКалорий"""
        sum_today = self.get_today_stats()
        # /\ считаем сумму калорий за сегодня
        n = self.limit - sum_today
        if (sum_today >= self.limit):
            return 'Хватит есть!'
        return ('Сегодня можно съесть что-нибудь ещё, '
                + f'но с общей калорийностью не более {n} кКал')


class Record:
    def __init__(self, amount: float, comment: Optional[str],
                 date=None) -> None:
        # PyTest не предусматривает аннотацию типа переменной date :(
        self.amount = amount
        date_format = '%d.%m.%Y'
        # \/проверка и форматирование даты
        if date is None:
            self.date = dt.date.today()
        else:
            fixdate = dt.datetime.strptime(date, date_format)
            self.date = fixdate.date()
        self.comment = comment
