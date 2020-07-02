import sqlalchemy as sa

# импортируем метод для поиска места вставки элемента в отсортированный список
from bisect import bisect_left

from datetime import datetime

# импортируем модуль "users.py" для возможности добавлять новых пользователей
import users as u

Base = u.Base

class Athelete(Base):
    """
    Описывает необходимую структуру таблицы athelete для использования данных об атлетах
    """
    # задаем название таблицы
    __tablename__ = 'athelete'

    # идентификатор пользователя, первичный ключ
    id = sa.Column(sa.Integer, primary_key=True)
    # имя
    birthdate = sa.Column(sa.Text)
    # рост
    height = sa.Column(sa.REAL)



def nearest(datalist, value):
    """ возвращает ближайшего "соседа" value в отсортированном списке datalist, а также его позицию """

    if value in datalist:
        # если такое значение совпадает с имеющимся в списке, то выбираем это значение
        index = datalist.index(value)
        result = datalist[index]
    else:
        if value < datalist[0]:
            # если значение меньше первого элемента списка, то выбираем первый элемент
            result = datalist[0]
            index = 0
        elif value > datalist[len(datalist)-1]:
            # если значение больше последнего элемента списка, то выбираем последний элемент
            result = datalist[len(datalist)-1]
            index = len(datalist)-1
        else:
            # ищем для заданного значения предполагаемое подходящее место в списке
            index = bisect_left(datalist, value)
            # далее определяем, какой сосед ближе - слева или справа
            if (value - datalist[index-1]) < (datalist[index] - value):
                result = datalist[index-1]
                index = index-1
            else:
                result = datalist[index]

    # если результат имеет тип datetime, преобразовываем его в дату в виде строки
    if isinstance(result, datetime):
        result = result.strftime("%Y-%m-%d")
    
    return result, index

def main():
    """
    Осуществляет взаимодействие с пользователем, обрабатывает пользовательский ввод
    """
    session = u.connect_db()
    # просим пользователя выбрать режим
    mode = input("Выбери режим.\n1 - выбрать пользователя по индентификатору\n2 - добавить нового пользователя\n")
    # проверяем режим
    if mode == "1":
        query_user = session.query(u.User)
        # выгружаем список идентификаторов таблицы user
        user_ids = [user.id for user in query_user.all()]
        
        query_athelete = session.query(Athelete)
        # выгружаем список идентификаторов таблицы athelete
        athelete_ids = [user.id for user in query_athelete.all()]
        # создаем словарь, где ключ - это идентификатор пользователя, а значение - дата рождения
        athelete_birthdates = {user.id: user.birthdate for user in query_athelete.all()}
        # сортируем словарь по значениям(по дате рождения)
        athelete_birthdates = sorted(athelete_birthdates.items(), key=lambda kv:kv[1])
        # создаем словарь, где ключ - это идентификатор пользователя, а значение - рост
        athelete_heights = {user.id: user.height for user in query_athelete.all()}
        # если рост у атлета не указан - принимаем его рост равным нулевому значению
        for key, value in athelete_heights.items():
            if athelete_heights[key] is None:
                athelete_heights[key] = 0
        # сортируем словарь по значениям(по росту)
        athelete_heights = sorted(athelete_heights.items(), key=lambda kv:kv[1])
        
        # запрашиваем идентификатор пользователя
        user_id = int(input("Введите идентификатор пользователя: "))
        if user_id in user_ids:
            # если такой пользователь существует - ищем ему атлета, ближайшего по дате рождения, по росту
            query = session.query(u.User).filter(u.User.id == user_id).first()
            # сохраним дату рождения пользователя
            birthdate = query.birthdate
            # сохраним рост пользователя
            height = query.height
            print("Выбранный пользователь родился {}, его рост: {}\n".format(birthdate, height))
            # формируем список дат рождения атлетов, при этом преобразовывая даты в тип datetime
            datalist = []
            for item in athelete_birthdates:
                datalist.append(datetime.strptime(item[1], "%Y-%m-%d"))
            # получаем в переменной res значение ближайшей даты, а в ind - значение, по которму определим идентификатор атлета
            res, ind = nearest(datalist, datetime.strptime(birthdate, "%Y-%m-%d"))
            print("Ближайший атлет по дате рождения:{}, его дата {}".format(athelete_birthdates[ind][0], res))

            # далее по аналогии делаем то же самое с ростом
            datalist.clear()
            for item in athelete_heights:
                datalist.append(item[1])
            res, ind = nearest(datalist, height)
            print("Ближайший атлет по росту:{}, его рост {}".format(athelete_heights[ind][0], res))
        else:
            print("К сожалению, пользователя с таким идентификатором в базе нет :(")
    elif mode == "2":
        # запрашиваем данные пользоватлея
        user = u.request_data()
        # добавляем нового пользователя в сессию
        session.add(user)
        # сохраняем все изменения, накопленные в сессии
        session.commit()
        print("Спасибо, данные сохранены!")
    else:
        print("Некорректный режим:(")

if __name__ == "__main__":
    main()







