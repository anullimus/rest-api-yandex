from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.db.db_postgres import get_by_parentId_and_type, get_by_id
from app.business_logic.business_process import SystemItem

router_nodes = APIRouter()


@router_nodes.get("/nodes/{id}", response_model=SystemItem, tags=['Базовые задачи'], description="""
       Получить информацию об элементе по идентификатору. 
       При получении информации о папке также предоставляется информация о её дочерних элементах.
       
        - для пустой папки поле children равно пустому массиву, а для файла равно null
        - размер папки - это суммарный размер всех её элементов. 
        - Если папка не содержит элементов, то размер равен 0. 
        - При обновлении размера элемента, суммарный размер папки, которая содержит этот элемент, тоже обновляется.
      """,
                  status_code=200)
async def nodes(id: str = Field(description='Идентификатор элемента', example='3fa85f64-5717-4562-b3fc-2c963f66a333')):
    print(f'id = {id}')

    # session = Session_lite()  # создание сессии
    try:
        idbase = get_by_id(id )
        print(f'idbase = {idbase}')

        if idbase == None:  # если не найден id
            print(f'не найден id')
            raise ValueError('404')

        elif idbase[3] == 'FOLDER':  # Если папка то ищем все дочерние элементы
            parentCat = get_by_parentId_and_type(id, 'FOLDER')  # ищем все дочерние элементы
            print(f'parentCat = {parentCat}')

            if len(parentCat) == 0:  # если дочерние элементы не найдены
                print(f'для пустой папки поле children равно пустому массиву, а для файла равно null')
                parentOff = get_by_parentId_and_type(id, 'FILE')
                if len(parentOff) == 0:  # если файлы в папке не найдены
                    return SystemItem(id=idbase[0], url=idbase[1],
                                      date=str(idbase[5]).replace(' ', 'T') + "Z", parentId=idbase[2],
                                      type=idbase[3],
                                      size=None, children=[])
                else:  # иначе обрабатываем файлы

                    allSize = sum([q[4] for q in parentOff])
                    # добавляем в массив все размеры каждого элемента
                    print(f'^^^^^' * 10)
                    print(allSize)

                    childrenOff = []  # дочерние элементы
                    for file in parentOff:
                        childrenOff.append(
                            SystemItem(type=file[3], url=file[1], id=file[0], parentId=idbase[0],
                                       size=file[4],
                                       date=str(file[5]).replace(' ', 'T') + "Z", children=None))

                    return SystemItem(id=idbase[0], url=idbase[1],
                                      date=str(idbase[5]).replace(' ', 'T') + "Z", parentId=idbase[2],
                                      type=idbase[3],
                                      size=allSize, children=[childrenOff])

            else:  # если у категории есть дочерние элементы
                print(f'дочерние папки {parentCat}')
                childrenCat = []  # массив дочерних элементов

                sizeOff = []  # массив для размеров файлов
                for i in parentCat:  # обрабатываю дочерние элементы
                    print(f'обрабатываю папки {i}')
                    parentOff = get_by_parentId_and_type(i[0], 'FILE')
                    print(f'файлы = {parentOff}')

                    if len(parentOff) == 0:  # если папка не содержит элементов
                        print('Если папка не содержит элементы, то ее размер равен 0.)')
                        childrenCat.append(
                            SystemItem(type=i[3], url=i[1], id=i[0], parentId=idbase[0], size=0,
                                       date=str(i[5]).replace(' ', 'T') + "Z", children=None))


                    else:  # если папка содержит элементы то ищем размер всех
                        allSize = sum([q[4] for q in parentOff])
                        # сумма вех размеров элементов
                        print(f'allSize = {allSize}')

                        # добавляем все размеры элементов в массив
                        [sizeOff.append(q[4]) for q in
                         parentOff]  # добавляем в массив все размеры каждого элемента

                        childrenOff = []  # дочерние элементы
                        # теперь нужно создать массив файлов
                        for file in parentOff:
                            print(f'файл = {file}')
                            childrenOff.append(SystemItem(type=file[3], url=file[1], id=file[0], parentId=i[0],
                                                          size=file[4],
                                                          date=str(file[5]).replace(' ', 'T') + "Z",
                                                          children=None))

                        # после массив файлов кладем в папку
                        childrenCat.append(
                            SystemItem(type=i[3], url=i[1], id=i[0], parentId=idbase[0], size=allSize,
                                       date=str(i[5]).replace(' ', 'T') + "Z", children=childrenOff))

                '''Целое число, для папки - это суммарный размер всех элеметов.'''

                mediumCatSize = sum([size for size in sizeOff])
                print(f'mediumCatSize = {mediumCatSize}')
                return SystemItem(type=idbase[3], url=idbase[1], id=idbase[0], parentId=idbase[2],
                                  size=mediumCatSize, date=str(idbase[5]).replace(' ', 'T') + "Z",
                                  children=childrenCat)

        elif idbase[3] == 'FILE':  # Если файл

            print(f'для пустой папки поле children равно пустому массиву'
                  f'а для файла равно null')
            return SystemItem(id=idbase[0], url=idbase[1], date=str(idbase[5]).replace(' ', 'T') + "Z",
                              parentId=idbase[2], type=idbase[3],
                              size=idbase[4], children=None)

    except Exception as err:
        print(f'err = {err}')
        if err.args[0] == '404':  # возвращаю нужную ошибку
            raise HTTPException(status_code=404, detail="Папка/файл не найден(-а).")
        else:
            raise HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны.")

