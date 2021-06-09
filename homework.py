from __future__ import annotations
import datetime as dt
from typing import Optional, List
import requests
from decimal import Decimal
API_key = 'b60b77c46f793211f140'


def get_rate(cur: str = 'руб') -> float:
    """получаем курс валют с сайта free.currconv.com
    на входе функция принимает код валюты из трех заглавных букв.
    На выходе получаем курс рубля к выбранной валюте. Костыль:
    В случае если переданная валюта - рубль, то возвращаем курс = 1"""
    if (cur == 'руб'):
        return 1
    elif cur == 'Euro':
        cur = 'EUR'
    else:
        cur = cur.upper()
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
        week = dt.timedelta(days=7)
        sum = self.calculate_sum(date=week)
        return sum

    def get_today_stats(self) -> float:
        """Считает сумму портаченных средств за сегодня."""
        today = dt.timedelta(hours=24 - dt.datetime.now().time().hour)
        sum = self.calculate_sum(date=today)
        return sum

    def add_record(self, rec: Record):
        """Добавляет запись."""
        self.records.append(rec)

    def calculate_sum(self, date: Optional[dt.timedelta] = 0) -> float:
        records = self.records
        sum: float = 0
        date_dif = dt.date.today() - date
        print(date_dif)
        for rec in records:
                if(date_dif <= rec.date <= dt.date.today()):
                    sum += rec.amount
        return sum


class CashCalculator(Calculator):
    USD_RATE = get_rate('usd')
    EURO_RATE = get_rate('eur')
    # Оригинальное решение было более изящным, без использования переменных
    # Пришлось костыли ставить чтобы пройти тесты, но курс валюты можно
    # получить вызовом функции get_rate()

    def get_today_cash_remained(self, currency: Optional[str] = 'руб') -> str:
        """Считает разницу лимита и суммы затраченных стредств
            в выбранной валюте"""
        cur_dict = {'USD': [self.USD_RATE, 'USD', 'usd'],
                    'EUR': [self.EURO_RATE, 'Euro', 'eur'],
                    'RUB': [1, 'руб', 'rub']}
        # /\ создаем словарь с курсами валют
        # \/ задаем параметры по умолчанию
        rate = 1
        cur_name = currency
        # \/ ищем нужный курс и название валюты
        for c, tup in cur_dict.items():
            if (currency in tup) or (c == currency):
                rate = tup[0]
                cur_name = tup[1]
        sum = self.get_today_stats()
        # /\ Тут считаем сумму потраченных средств за сегодня
        sum /= rate
        n = self.limit / rate
        # /\ перевели сумму и лимит в нужную валюту
        sum_fin = n - sum
        # /\считаем остаток на счету
        if (Decimal(sum_fin) % 1 == 0):
            sum_fin = int(sum_fin)
        else:
            sum_fin = round((sum_fin), 2)
        # /\проверяем сумму.
        # /\В случае отсутсвия дробной части - представляем ее целым числом
        # /\дробную часть округляем до двух знаков после точки
        if sum < n:

            return (f"На сегодня осталось {sum_fin} {cur_name}")

        elif sum == n:

            return ('Денег нет, держись')

        else:
            sum_fin *= -1
            # задолженность выводим как положительное число
            return ('Денег нет, держись: твой долг - '
                    + str(f'{sum_fin} ' + cur_name))


class CaloriesCalculator(Calculator):
    def __init__(self, limit):
        super().__init__(limit)

    def get_calories_remained(self) -> str:
        """Считает разницу лимита и суммы
            съеденных килоКалорий"""
        sum = self.get_today_stats()
        # /\ считаем сумму калорий за сегодня
        n = self.limit - sum
        if (sum >= self.limit):
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
        if (date is None):
            self.date = dt.date.today()
        else:
            fixdate = dt.datetime.strptime(date, date_format)
            self.date = fixdate.date()
        self.comment = comment
