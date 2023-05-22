from typing import Optional, List
from pydantic import Field, root_validator
from datetime import datetime
from enum import Enum

from models.envisionBaseModel import EnvisionBaseModel, PyObjectId
from models.picture import PictureModel


class CMSStatusEnum(str, Enum):
    approved = 'Approve and Publish'
    review = 'Review'


class NameLogoModel(EnvisionBaseModel):
    has_logo: bool
    logo: Optional[str]
    replace_name: bool
    alt: Optional[str] = ''


class MediaInfoModel(EnvisionBaseModel):
    url: Optional[str]
    embed: Optional[str]
    description: Optional[str]


class MediaModel(EnvisionBaseModel):
    instagram: MediaInfoModel = MediaInfoModel()
    youtube: MediaInfoModel = MediaInfoModel()
    soundcloud: MediaInfoModel = MediaInfoModel()
    spotify: MediaInfoModel = MediaInfoModel()


class TalentModel(EnvisionBaseModel):
    id: PyObjectId
    name: str
    slogan: Optional[str]
    main_category: Optional[str]
    title: Optional[str]
    approved_tracks: Optional[str]
    pillars: Optional[List[str]]
    online_content: Optional[bool]
    envision_festival: bool
    media: MediaModel
    country: Optional[str]
    short_bio: Optional[str]
    long_bio: Optional[str]
    name_logo: Optional[NameLogoModel]
    message: Optional[str]
    picture: Optional[PictureModel]
    email: Optional[str]
    phone: Optional[str]
    contact_name: Optional[str]
    slug: str
    main_stage: Optional[PyObjectId]
    flags: List[str]
    cms_id: Optional[str]
    cms_status: Optional[CMSStatusEnum]
    ethos_id: Optional[int]
    archived: bool = Field(alias='_archived')
    draft: bool = Field(alias='_draft')
    deleted: bool
    last_modified: datetime
    date_created: datetime


class CreateTalentRequest(EnvisionBaseModel):
    name: str
    main_category: str = None
    slogan: str = None
    title: str = None
    approved_tracks: str = None
    pillars: List[str] = []
    online_content: bool = None
    envision_festival: bool
    media: MediaModel = MediaModel()
    country: str = None
    short_bio: str = None
    long_bio: str = None
    name_logo: NameLogoModel = None
    message: str = None
    picture: PictureModel = PictureModel()
    email: str = None
    phone: str = None
    contact_name: str = None
    slug: str
    main_stage: PyObjectId = None
    flags: List[str] = []
    cms_status: CMSStatusEnum = CMSStatusEnum.review
    ethos_instructor: bool = False
    archived: bool = Field(alias='_archived', default=False)
    draft: bool = Field(alias='_draft', default=False)


class UpdateTalentRequest(EnvisionBaseModel):
    name: Optional[str]
    main_category: Optional[str]
    slogan: Optional[str]
    title: Optional[str]
    approved_tracks: Optional[str]
    pillars: Optional[List[str]]
    online_content: Optional[bool]
    envision_festival: Optional[bool]
    media: Optional[MediaModel]
    country: Optional[str]
    short_bio: Optional[str]
    long_bio: Optional[str]
    name_logo: Optional[NameLogoModel]
    message: Optional[str]
    picture: Optional[PictureModel]
    email: Optional[str]
    phone: Optional[str]
    contact_name: Optional[str]
    slug: Optional[str]
    main_stage: Optional[PyObjectId]
    flags: Optional[List[str]]
    archived: Optional[bool] = Field(alias='_archived')
    draft: Optional[bool] = Field(alias='_draft')

    @root_validator(pre=True)
    def prevent_none(cls, values):
        for f in TalentModel.schema().get('required', []):
            if f in values and values[f] is None:
                raise ValueError(f'{f} cannot be null')
        return values
