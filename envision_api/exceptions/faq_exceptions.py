from fastapi import HTTPException, status


class InvalidCategory(HTTPException):
    def __init__(self, category: str, categories: list):
        categories_str = ', '.join(categories)
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f'ValidationError. Category {category} is not allowed. The allowed categories are: {categories_str}',
                         None)
