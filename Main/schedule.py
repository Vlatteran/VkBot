import time
import datetime
import re


class Schedule:
    schedule = {
        'понедельник': {
            'числитель': {
                '18:50 - 20:20': 'Интеграллы и диффиеренциальные уравнения - практика',
                '20:30 - 22:00': 'Инженерная и компьютерная графика - лекция'
            },
            'знаменатель': {
                '18:50 - 20:20': 'Интеграллы и диффиеренциальные уравнения - практика',
                '20:30 - 22:00': 'Дискретная математика - лекция'
            }
        },
        'вторник': {
            'числитель': {
                '18:50 - 20:20': 'Инженерная и компьютерная графика - практика',
                '20:30 - 22:00': 'Инженерная и компьютерная графика - практака'
            },
            'знаменатель': {
                '18:50 - 20:20': 'Технологии программирования - практика',
                '20:30 - 22:00': 'Технологии программирования - практика'
            }
        },
        'среда': {
            'числитель': {
                '18:50 - 20:20': 'Физическая культура',
            },
            'знаменатель': {
                '18:50 - 20:20': 'Физическая культура',
            }
        },
        'четверг': {
            'числитель': {
                '18:50 - 20:20': 'Философия - лекция',
                '20:30 - 22:00': 'Дискретная математика - практика'
            },
            'знаменатель': {
                '18:50 - 20:20': 'Философия - практика',
                '20:30 - 22:00': 'Дискретная математика - практика'
            }
        },
        'пятница': {
            'числитель': {
                '18:50 - 20:20': 'Интеграллы и диффиеренциальные уравнения - лекция',
                '20:30 - 22:00': 'Иностраннный язык'
            },
            'знаменатель': {
                '18:50 - 20:20': 'Технологии программирования - лекция',
                '20:30 - 22:00': 'Иностраннный язык'
            }
        }
    }
    dec_ru = {
        0: 'понедельник',
        1: 'вторник',
        2: 'среда',
        3: 'четверг',
        4: 'пятница',
    }
    ru_dec = {
        'понедельник': 0,
        'вторник': 1,
        'среда': 2,
        'четверг': 3,
        'пятница': 4,
    }

    def show(self, day=''):
        date_regex = r'(\b(0?[1-9]|[1-2][0-9]|3[0-1])[\.\\]([1][0-2]|0?[1-9])\b)'
        if re.match(date_regex, day):
            days = re.split(r'[.\\]', day)
            times = datetime.datetime(day=int(days[0]), month=int(days[1]), year=2021).timetuple()
            day = ''
        else:
            times = time.localtime()
        is_even = 'числитель' if (times.tm_yday - 32) // 7 % 2 == 0 else 'знаменатель'
        print(day, times)
        if day in ('сегодня', '') and 0 <= times.tm_wday < 5:
            result = f'Расписсание на {times.tm_mday}/{times.tm_mon}/{times.tm_year}:'
            for i in self.schedule[self.dec_ru[times.tm_wday]][is_even]:
                result += f'\n{i}: {self.schedule[self.dec_ru[times.tm_wday]][is_even][i]}'
        elif day == 'завтра' and times.tm_wday < 4:
            result = f'Расписсание на {times.tm_mday + 1}/{times.tm_mon}/{times.tm_year} ' \
                     f'({self.dec_ru[times.tm_wday + 1]}/{is_even}):'
            for i in self.schedule[self.dec_ru[times.tm_wday + 1]][is_even]:
                result += f'\n{i}: {self.schedule[self.dec_ru[times.tm_wday + 1]][is_even][i]}'
        elif day == 'завтра' and times.tm_wday == 6:
            is_even = 'числитель' if is_even == 'знаменатель' else 'знаменатель'
            result = f'Расписсание на {times.tm_mday + 1}/{times.tm_mon}/{times.tm_year} (понедельник/{is_even}):'
            for i in self.schedule[self.dec_ru[0]][is_even]:
                result += f'\n{i}: {self.schedule[self.dec_ru[0]][is_even][i]}'
        elif day in ('понедельник', 'вторник', 'среда', 'четверг', 'пятница'):
            if self.ru_dec[day] < times.tm_wday:
                week = 'следующей'
                is_even = 'числитель' if is_even == 'знаменатель' else 'знаменатель'
            else:
                week = 'этой'
            result = f'Расписсание на {day if day[-1] != "а" else day[:len(day) - 1] + "у"} {week} недели:'
            for i in self.schedule[day][is_even]:
                result += f'\n{i}: {self.schedule[day][is_even][i]}'
        else:
            result = 'Не удалось найти рассписание на указаный день'
        return result


if __name__ == '__main__':
    a = Schedule()
    print(a.show('1.2'))
