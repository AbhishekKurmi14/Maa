from pydantic import BaseModel, Field
import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name:str
    email:str
    mobile_number: str
    whatsapp_number: str
    password: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class requestdetails(BaseModel):
    email:str
    password:str
        
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class changepassword(BaseModel):
    email:str
    old_password:str
    new_password:str

class TokenCreate(BaseModel):
    user_id:str
    access_token:str
    refresh_token:str
    status:bool
    created_date:datetime.datetime

class RikshawUser(BaseModel):
    rikshaw_no: str
    area: str
    password: str
    name: str  # Add name field
    contact_number: str  # Add contact number field

class VideoUpload(BaseModel):
    file_path:str

class VideoBase(BaseModel):
    title: str
    file_path: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int
    play_count: int

    class Config:
        orm_mode = True


class Subscription(BaseModel):
    amount : int
    month: int
    month_type: str
    sub_id: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
      
from typing import Optional
class UserSubscriptionBase(BaseModel):
    user_id: int
    subscription_id: int
    status: Optional[str] = "Pending"

class UserSubscriptionCreate(UserSubscriptionBase):
    pass

class UserSubscription(UserSubscriptionBase):
    id: int

    class Config:
        orm_mode = True

class SubscriptionDetails(BaseModel):
    user_id: int
    sub_id: str
    start_date: datetime
    end_date: datetime
    total_price: int
    no_of_play: int
    plan_type: int
    status: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class RikshawLocationUpdate(BaseModel):
    latitude: float
    longitude: float
class GetLocationsResponse(BaseModel):
    status_code: int
    message: str
    data: dict

class ContactMessageBase(BaseModel):
    name: str
    email: str
    message: str

class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessage(ContactMessageBase):
    id: int
    status: str

    class Config:
        orm_mode = True


class FeedbackMessageBase(BaseModel):
    message: str

class FeedbackMessageCreate(FeedbackMessageBase):
    user_id: int

class FeedbackMessage(FeedbackMessageBase):
    id: int
    status: str

    class Config:
        orm_mode = True

class ImageBase(BaseModel):
    name: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    s3_url: str

    class Config:
        orm_mode = True

from typing import List, Optional,Dict
from pydantic import BaseModel
class ImageInfo(BaseModel):
    name: str
    s3_url: str

class OurClientsResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[Dict[str, List[ImageInfo]]]
