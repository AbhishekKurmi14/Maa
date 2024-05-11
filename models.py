from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger 
from database import Base
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True,nullable = False)
    mobile_number = Column(String, unique=True, index=True, nullable = False)
    whatsapp_number = Column(String, unique=True, index=True, nullable = False) 
    password = Column(String, index=True, nullable = False)

    subscriptions = relationship("UserSubscription", back_populates="user")
    video_plays = relationship("VideoPlay", back_populates="user")
    videos = relationship("Video", back_populates="user")
    feedback_messages = relationship("FeedbackMessage", back_populates="user")
    
class TokenTable(Base):
    __tablename__ = "token"
    user_id = Column(Integer)
    access_token = Column(String(450), primary_key=True)
    refresh_token = Column(String(450),nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
# from sqlalchemy import Column, Integer, Float, DateTime, func
# class Location(Base):
#     __tablename__ = "locations"

#     id = Column(Integer, primary_key=True, index=True)
#     latitude = Column(Float)
#     longitude = Column(Float)

class RikshawUser(Base):
    __tablename__ = 'rikshaw_user'

    id = Column(Integer, primary_key=True)
    rikshaw_no = Column(String)
    area = Column(String)
    password = Column(String)
    name = Column(String)  # Make sure this line is included
    contact_number = Column(String)
    # # Define a one-to-one relationship with the Location model
    # location = relationship("Location", back_populates="rikshaw_user", uselist=False)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="videos")
# class VideoPlay(Base):
#     __tablename__ = "videos_play"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String)
#     file_path = Column(String)
#     play_count = Column(Integer, default=0)

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, ForeignKey
class VideoPlay(Base):
    __tablename__ = "video_plays"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String, index=True)
    play_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))  # Add user_id foreign key
    play_date = Column(DateTime, default=func.now())

    # Define a relationship with the User model
    user = relationship("User", back_populates="video_plays")

from pydantic import BaseModel
from typing import Dict

class UserPlaySubscriptionCount(BaseModel):
    user_id: int
    total_play_count: int
    subscription_count: int
    weekly_play_counts: Dict[str, int]

from sqlalchemy import Column, Integer, String, ForeignKey
class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(String)
    month = Column(String)
    month_type = Column(String)
    sub_id = Column(String)

    users = relationship("UserSubscription", back_populates="subscription")


from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    status = Column(String, default="Pending")  # Added status field

    user = relationship("User", back_populates="subscriptions")
    subscription = relationship("Subscription", back_populates="users")


class SubscriptionDetails(Base):
    __tablename__ = "subscription_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sub_id = Column(Integer, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_price = Column(Integer)
    no_of_play = Column(Integer)
    plan_type = Column(Integer)
    status = Column(String)


from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
# Step 1: Define a model for the contact us messages
class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(Text)
    status = Column(String, default="pending")


from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
# Step 1: Define a model for the contact us messages
class FeedbackMessage(Base):
    __tablename__ = "feedback_messages"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey('users.id'))  # Assuming the foreign key relationship with the users table

    # Define the relationship with the User model
    user = relationship("User", back_populates="feedback_messages")


from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

class RikshawLocation(Base):
    __tablename__ = 'rikshaw_location'

    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    rikshaw_user_id = Column(Integer, ForeignKey('rikshaw_user.id'))

    # Relationship with RikshawUser
    rikshaw_user = relationship("RikshawUser", back_populates="location")

from typing import List, Dict
from pydantic import BaseModel

class SubscriptionResponse(BaseModel):
    status_code: int
    message: str
    data: List[Dict]




# class Location(Base):
#     __tablename__ = 'locations'

#     id = Column(Integer, primary_key=True, index=True)
#     device_id = Column(String, index=True, nullable=False)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)
#     created_at = Column(DateTime, default=func.now())