# from pydantic import BaseModel, validator
#
#
# class CheckAPIResponse(BaseModel):
#     """Элемент ответа от API"""
#
#     age: int
#     name: str
#
#     # @validator('age')
#     # def check_age(cls, v: int):
#     #     if v <= 10:
#     #         raise ValueError
