from fastapi import APIRouter, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
from pydantic import Field
from app.db.db_postgres import init_cursor, get_by_id, get_by_parentId_and_type, delete_by_parentId, \
    delete_by_id

router_delete = APIRouter()


@router_delete.delete("/delete/{id}", tags=['Базовые задачи'], description="""
        - Удалить элемент по идентификатору. При удалении папки удаляются все дочерние элементы. 
        - Доступ к статистике (истории обновлений) удаленного элемента невозможен.

        - Обратите, пожалуйста, внимание на этот обработчик. При его некорректной работе тестирование может быть невозможно.""")
               # dependencies=[Depends(RateLimiter(times=1000, seconds=60))])
async def delete_(id: str = Field(description='Идентификатор', example='3fa85f64-5717-4562-b3fc-2c963f66a333')):
    print(f'id = {id}')

    init_cursor()
    try:
        idbase = get_by_id(id)  # поиск id в базе
        print(f'idbase = {idbase}')

        if idbase is None:  # если не найден id
            return HTTPException(status_code=404, detail="Папка/файл не найден(-а).")
        elif idbase[3] == 'FOLDER':  # Если папка
            print(f'При удалении папки удаляются все дочерние элементы.')
            # ищем все дочерние папки и удаляем их
            parentCat = get_by_parentId_and_type(id, 'FOLDER')
            if parentCat != None:  # если есть дочерние папки
                for i in parentCat:  # ищем все дочерние элементы в этих папках
                    delete_by_parentId(i[0])

                delete_by_parentId(id)
                delete_by_id(id)


            else:  # если нет дочерних папок то удаляем все файлы внутри папки
                delete_by_parentId(id)
                delete_by_id(id)

            return HTTPException(status_code=200, detail="Удаление прошло успешно.")


        elif idbase[3] == 'FILE':  # Если файл
            delete_by_id(id)

            return HTTPException(status_code=200, detail="Удаление прошло успешно.")
    except Exception as err:
        print(f'Невалидная схема документа или входные данные не верны.')
        print(err)
        raise HTTPException(status_code=400, detail="Невалидная схема документа или входные данные не верны.")
