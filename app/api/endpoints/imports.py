from fastapi import APIRouter, HTTPException

from app.db.db_postgres import get_by_id, init_cursor, insert_to_bd, update_date_by_id, \
    update_values_by_id
from app.business_logic.business_process import SystemItemImportRequest

router_imports = APIRouter()


@router_imports.post("/imports", tags=['Базовые задачи'], description="""
        Импортирует элементы файловой системы. Элементы импортированные повторно обновляют текущие.
        Изменение типа элемента с папки на файл и с файла на папку не допускается.
        Порядок элементов в запросе является произвольным.

          - id каждого элемента является уникальным среди остальных элементов
          - поле id не может быть равно null
          - родителем элемента может быть только папка
          - принадлежность к папке определяется полем parentId
          - элементы могут не иметь родителя (при обновлении parentId на null элемент остается без родителя)
          - поле url при импорте папки всегда должно быть равно null
          - размер поля url при импорте файла всегда должен быть меньше либо равным 255
          - поле size при импорте папки всегда должно быть равно null
          - поле size для файлов всегда должно быть больше 0
          - при обновлении элемента обновленными считаются **все** их параметры
          - при обновлении параметров элемента обязательно обновляется поле **date** в соответствии с временем обновления
          - в одном запросе не может быть двух элементов с одинаковым id
          - дата обрабатывается согласно ISO 8601 (такой придерживается OpenAPI). Если дата не удовлетворяет данному формату, ответом будет код 400.

        Гарантируется, что во входных данных нет циклических зависимостей и поле updateDate монотонно возрастает. Гарантируется, что при проверке передаваемое время кратно секундам.
      """)
             # dependencies=[Depends(RateLimiter(times=1000, seconds=60))])
async def import_post(Data: SystemItemImportRequest):
    used_id = []  # массив для id \\ id - файла/FILE или папки/FOLDER является уникальным среди файлов и папок
    init_cursor()
    try:
        for el in Data.items:  # обаратываем каждый элемент файлов
            if el.id in used_id:
                print(f'в одном запросе не может быть двух элементов с одинаковым id {el.id}')
                return HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны "
                                                             "(id должен быть уникальным)")
            elif el.type == 'FILE' and (el.url is None or len(el.url) > 255):
                print(f'размер поля url при импорте файла всегда должен быть меньше либо равным 255')
                return HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны"
                                                             "(у поля url при импорте файла всегда должен быть <= 255 и не быть None)")
            elif el.type == 'FOLDER' and el.url is not None:
                print(f'поле url при импорте папки всегда должно быть равно null')
                return HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны"
                                                             "(у папки url должен быть 'null')")
            elif (el.size is None or el.size <= 0) and el.type == 'FILE':
                print(f'поле size для файлов всегда должно быть больше 0.')
                return HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны"
                                                             "(размер не может быть отрицательным или 'null')")
            elif el.type == 'FOLDER' and el.size is not None:
                print(f'поле size при импорте папки всегда должно быть равно null')
                return HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны"
                                                             "(у папки размер должен быть 'null')")

            try:
                # isodate = Data.updateDate.isoformat()
                pass
            except:
                print('дата должна обрабатываться согласно ISO 8601 (такой придерживается OpenAPI). '
                      'Если дата не удовлетворяет данному формату, необходимо отвечать 400.')
                return HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны."
                                                             "(дата должна обрабатываться согласно ISO 8601)")

            used_id.append(el.id)  # проверка на то был ли такой id в запросе

            id_base = get_by_id(el.id)
            print(f'id в базе {id_base}')


            if id_base is None:  # Если айди нету в базе то создаем
                print(f'создание id в базе')
                parent_id_base = get_by_id(el.parentId)
                print(f'родитель = {parent_id_base}')
                print(f'родитель.id = {el.parentId}')

                if parent_id_base == None:  # если нет родительского id
                    insert_to_bd(id=el.id, url=el.url, parentId=el.parentId, type=el.type,
                                               size=el.size, updateDate=Data.updateDate)

                elif parent_id_base[3] == 'FILE':  # Если тип родителя файл
                    print('родителем/parentId элемента может быть только папка')
                    return HTTPException(status_code=400,
                                         detail="Невалидная схема документа или входные данные не верны"
                                                "(родителем элемента может быть только папка)")

                else:  # если есть родитель(и)
                    insert_to_bd(id=el.id, url=el.url, parentId=el.parentId, type=el.type,
                                               size=el.size, updateDate=Data.updateDate)
                    try:
                        print(f'обновляем метку у всех файлов в данной папке')
                        update_date_by_id(el.parentId, Data.updateDate)

                        try:  # обновление главной папки
                            print(f'el id= {el}')
                            print(f'id_base = {id_base}')

                            parent_id = get_by_id(el.parentId) # поиск id папки выше
                            print(f'**************' * 30)
                            print(f'parent_id = {parent_id}')
                            update_date_by_id(parent_id[2], Data.updateDate)
                        except:
                            print(f'ошибка обновления папки 0')
                    except:
                        print(f'ошибка обновления папки 1')



            else:  # Если id есть в базе, то меняем его
                print(f'обновляем id')

                if el.type != id_base[3]:  # Если попытаются поменять тип элемента
                    print(f'''Импортирует элементы файловой системы. Элементы импортированные повторно обновляют текущие.
                                Изменение типа элемента с папки на файл и с файла на папку не допускается. ''')
                    return HTTPException(status_code=400,
                                         detail="Невалидная схема документа или входные данные не верны."
                                                "(Изменение типа элемента не допускается)")
                else:
                    """    
                    - принадлежность к категории определяется полем parentId
                    - элементы могут не иметь родителя (при обновлении parentId на null, элемент остается без родителя)
                    - при обновлении элемента обновленными считаются **все** их параметры
                    - при обновлении параметров элемента обязательно обновляется поле **date** в соответствии с временем обновления
                    """

                    print(f'обновляем в бд')
                    if id_base[3] == 'FILE':
                        print(f'обновляем файл')
                        update_values_by_id(el.id, el.url, el.parentId, el.type, el.size, Data.updateDate)
                        print(f'обновляем время у самой папки')
                        update_date_by_id(el.parentId, Data.updateDate)
                        try:  # обновление главной папки
                            parent_id = get_by_id(el.parentId)  # поиск id папки выше
                            update_date_by_id(parent_id[2], Data.updateDate)
                        except Exception as err:
                            print(err)
                            print(f'ошибка обновления папки 2')

                    else:  # если обновляется папка то обновляем время у папки выше
                        print(f'обновление папки')
                        update_values_by_id(el.id, el.url, el.parentId, el.type, el.size, Data.updateDate)

                        if id_base[5] != Data.updateDate:  # новая метка времен
                            print(f'обновляю метку у самой папки')
                            update_date_by_id(el.parentId, Data.updateDate)

                            try:  # обновление главной папки
                                print(f'el id= {el}')
                                print(f'id_base = {id_base}')
                                parent_id = get_by_id(el.parentId)  # поиск id папки выше
                                print(f'**************' * 30)
                                print(f'parent_id = {parent_id}')
                                update_date_by_id(parent_id[2], Data.updateDate)
                            except:
                                print(id_base[5])
                                print(Data.updateDate)
                                print(f'ошибка обновления папки 3')

        return HTTPException(status_code=200, detail="Вставка или обновление прошли успешно.")
    except Exception as err:
        print(f'Невалидная схема документа или входные данные не верны.')
        print(err)
        raise HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны.")
