import datetime

from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field


class SystemItemType(str, Enum):
    FILE = 'FILE'
    FOLDER = 'FOLDER'


class SystemItemImport(BaseModel):
    id: str = Field(description='Уникальный идентфикатор', nullable=False, example='1')
    url: Union[str, None] = Field(description='Ссылка на файл. Для папок поле равнно null.', nullable=False, example='/file/url1')
    parentId: Union[str, None] = Field(description='id родительской папки', nullable=True, example='элемент_1_1')
    type: SystemItemType = Field(description='Тип элемента - папка или файл', example='FILE')
    size: Union[int, None] = Field(description='Целое число, для папок поле должно содержать null.', nullable=True,
                                    example=234)


class SystemItemImportRequest(BaseModel):
    items: List[SystemItemImport] = Field(description='Импортируемые элементы', nullable=False)
    updateDate: datetime.datetime = Field(description='Время обновления добавляемых элементов.', nullable=False,
                                          example="2022-05-28T21:12:01Z", default=datetime.datetime.now())


### response

class SystemItem(BaseModel):
    type: SystemItemType = Field(description='Тип элемента - папка или файл', example='FILE')
    url: Union[str, None] = Field(description='Ссылка на файл. Для папок поле равнно null.', nullable=True, example='/file/url1')
    id: str = Field(description='Уникальный идентфикатор', nullable=False, example="элемент_1_1")
    size: Union[int, None] = Field(description='Целое число, для папки - это суммарный размер всех элеметов.', nullable=True)
    parentId: Union[str, None] = Field(description='id родительской категории', nullable=True, example='элемент_1_1')
    date: str = Field(description='Время последнего обновления элемента.', nullable=False,
                      example='2022-05-28T21:12:01Z')

    children: Union[list, None]
