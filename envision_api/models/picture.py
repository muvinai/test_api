response.pyfrom typing import Optional

from models.envisionBaseModel import EnvisionBaseModel


class PictureModel(EnvisionBaseModel):
    original: Optional[str] = None
    thumbnail: Optional[str] = None
    local: Optional[str] = None
    alt: Optional[str] = ''