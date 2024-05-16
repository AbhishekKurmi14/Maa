import schemas
import models
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import Base, engine, SessionLocal

import schemas
import models
import jwt
from datetime import datetime 
from models import User,TokenTable
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from auth_bearer import JWTBearer
from functools import wraps
from utils import create_access_token,create_refresh_token,verify_password,get_hashed_password
from moviepy.editor import VideoFileClip
from fastapi.middleware.cors import CORSMiddleware

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"   # should be kept secret
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"
# Create the FastAPI app instance

Base.metadata.create_all(engine)
# Create a Passlib CryptContext object
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Endpoint for user registration
@app.post("/register")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_db)):
    # Check if the mobile number or WhatsApp number already exist
    existing_user = session.query(models.User).filter(
        (models.User.mobile_number == user.mobile_number) |
        (models.User.whatsapp_number == user.whatsapp_number) |
        (models.User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number or WhatsApp number or email already registered")

    # Hash the password
    hashed_password = get_hashed_password(user.password)

    # Create a new user
    new_user = models.User(first_name=user.first_name,last_name = user.last_name,email = user.email, mobile_number=user.mobile_number,
                    whatsapp_number=user.whatsapp_number, password=hashed_password)

    # Add the new user to the session, commit, and refresh
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    response =  {
        "status_code": status.HTTP_201_CREATED,
        "message": "User registered successfully",
        "data": {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "mobile_number": new_user.mobile_number,
            "whatsapp_number": new_user.whatsapp_number,
        }
    }
    
    return response



from jose import jwt
from fastapi.responses import JSONResponse
@app.post("/login", response_model=schemas.TokenSchema)
def login(request: schemas.requestdetails, session: Session = Depends(get_db)):
    # Retrieve user by email
    user = session.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify password
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    # Encode user ID in the access token payload
    access_token_payload = {"user_id": user.id}
    access_token = jwt.encode(access_token_payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    # Encode user ID in the refresh token payload
    refresh_token_payload = {"user_id": user.id}
    refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    # Return the tokens along with the user's details
    return JSONResponse(content={
        "status_code": status.HTTP_200_OK,
        "message": "User logged in successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "data": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "mobile_number": user.mobile_number,
            "whatsapp_number": user.whatsapp_number
            # Include other user details if needed
        }
    })


from auth_bearer import JWTBearer

@app.get('/getusers')
def getusers( dependencies=Depends(JWTBearer()),session: Session = Depends(get_db)):
    user = session.query(models.User).all()

    response =  {
        "status_code": status.HTTP_201_CREATED,
        "message": "Users list",
        "data": {
            "user_list": user
        }
    }
    return response


@app.post('/change-password')
def change_password(request: schemas.changepassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
    
    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()
    
    response =  {
        "status_code": status.HTTP_201_CREATED,
        "message": "Password changed successfully",
        "data": {
            "old_password":request.old_password,
            "new_password": user.password
        }
    }
    return response

@app.post('/rikshaw_login')
def rikshaw_login(user: schemas.RikshawUser, session: Session = Depends(get_db)):
    # Check if all required fields are provided
    if not user.rikshaw_no or not user.area or not user.password  or not user.name or not user.contact_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All fields are required")
    
    # Predefined password (this should ideally be stored securely, not hardcoded)
    predefined_password = "xyz$#1234$#abc$#678"
    
    # Check if the password matches the predefined password
    if user.password != predefined_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    
    # Create a new instance of the RikshawUser model and add it to the session
    db_user = models.RikshawUser(
        rikshaw_no=user.rikshaw_no,
        area=user.area,
        name=user.name,
        contact_number=user.contact_number
    )
    session.add(db_user)
    session.commit()

    response =  {
        "status_code": status.HTTP_201_CREATED,
        "message": "Rikshaw user logged in successfully",
        "data": {
            "id": db_user.id,  # Return the ID of the newly created rickshaw user
            "rikshaw_no": db_user.rikshaw_no,
            "area": db_user.area,
            "name": db_user.name,
            "contact_number": db_user.contact_number
        }
    }
    
    return response


import boto3
from botocore.exceptions import ClientError

# Configure AWS credentials
AWS_ACCESS_KEY_ID = 'AKIA2UC3BSG7WK7KCY5D'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
S3_BUCKET_NAME = 'pro-2'

@app.post("/video_upload/{user_id}")
async def upload(user_id: int, file: UploadFile = File(...), session: Session = Depends(get_db)):
    # Check if the uploaded file is a video
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only video files are allowed")

    # Upload the video file to S3 bucket
    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, file.filename)
    except ClientError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file to S3")

    # If upload is successful, save the file path and user_id in the database
    video_data = models.Video(file_path=f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file.filename}", user_id=user_id)
    session.add(video_data)
    session.commit()

    response = {
        "status_code": status.HTTP_201_CREATED,
        "message": "Video uploaded successfully",
        "data": {
            "id": video_data.id,
            "file_path": f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file.filename}",
            "user_id": user_id,
        }
    }

    return response

def get_video_duration(video_path: str) -> int:
    # Get the duration of the video using moviepy library
    try:
        video = VideoFileClip(video_path)
        duration = int(video.duration)
        video.close()
        return duration
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting video duration: {str(e)}")

    return 0  # Default value if duration retrieval fails

@app.get("/show_video")
def get_videos(session: Session = Depends(get_db)):
    get_videos = session.query(models.Video).all()

    response =  {
        "status_code": status.HTTP_201_CREATED,
        "message": "video list",
        "data": {
            "video_list": get_videos
        }
    }
    return response


@app.post("/video_play/{video_id}/{user_id}")
async def play_video(video_id: int, user_id: int, session: Session = Depends(get_db)):
    # Check if the user has an active subscription
    user_subscription = session.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == user_id,
        models.UserSubscription.status == "Accepted"
    ).first()

    if not user_subscription:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have an active subscription")

    # Get the video from the database
    video = session.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Video not found")

    # Increment the play count and store the play date
    video_play = session.query(models.VideoPlay).filter(
        models.VideoPlay.user_id == user_id,
        models.VideoPlay.file_path == video.file_path
    ).first()

    if video_play:
        video_play.play_count += 1
    else:
        video_play = models.VideoPlay(
            title="Video Title",
            file_path=video.file_path,
            play_count=1,
            user_id=user_id,
            play_date=datetime.now()  # Store the current date and time
        )
        session.add(video_play)
    session.commit()

    response = {
        "status_code": status.HTTP_201_CREATED,
        "message": "Video played successfully",
        "data": {
            "title": video_play.title,
            "file_path": video_play.file_path,
            "counter": video_play.play_count,
            "play_date": video_play.play_date  # Include the play date in the response
        }
    }

    return response


import boto3
from botocore.exceptions import ClientError

# Assuming you have already configured your AWS credentials and S3 bucket name

@app.delete("/video/{video_id}")
async def delete_video(video_id: int, session: Session = Depends(get_db)):
    # Retrieve the video data from the database
    video_data = session.query(models.Video).filter(models.Video.id == video_id).first()
    if not video_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # Delete the video file from S3 bucket
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=video_data.file_path.split('/')[-1])
    except ClientError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file from S3")

    # Delete the video data from the database
    session.delete(video_data)
    session.commit()

    response = {
        "status_code": status.HTTP_200_OK,
        "message": "Video deleted successfully",
        "data": {
            "id": video_data.id,
            "file_path": video_data.file_path,
        }
    }

    return response



from sqlalchemy import func, extract
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from collections import defaultdict

@app.get("/user_play_subscription_count/{user_id}", response_model=models.UserPlaySubscriptionCount)
async def get_user_play_subscription_count(user_id: int, session: Session = Depends(get_db)):
    # Query the database to get all video plays for the user
    video_plays = session.query(models.VideoPlay).filter(models.VideoPlay.user_id == user_id).all()

    # Calculate the total play count
    total_play_count = sum(video_play.play_count for video_play in video_plays)

    # Query the database to get the count of subscriptions for the user
    subscription_count = session.query(func.count(models.UserSubscription.id)).filter(
        models.UserSubscription.user_id == user_id
    ).scalar()

    # Calculate the start and end dates for each week in the month
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    end_of_month = start_of_month.replace(day=1, month=start_of_month.month + 1) - timedelta(days=1)

    # Group the weekly play counts into broader periods like "Week 1", "Week 2", etc.
    weeks = defaultdict(int)
    while start_of_month <= end_of_month:
        week_start = start_of_month.strftime("%Y-%m-%d")
        week_end = (start_of_month + timedelta(days=6)).strftime("%Y-%m-%d")
        week_number = (start_of_month.day - 1) // 7 + 1  # Calculate the week number
        week_play_count = sum(video_play.play_count for video_play in video_plays if
                              week_start <= video_play.play_date.strftime("%Y-%m-%d") <= week_end)
        weeks[f"Week {week_number}"] += week_play_count
        start_of_month += timedelta(days=7)

    # Prepare the response
    response = models.UserPlaySubscriptionCount(
        user_id=user_id,
        total_play_count=total_play_count,
        subscription_count=subscription_count,
        weekly_play_counts=dict(weeks)  # Convert defaultdict to regular dict
    )

    return response



@app.post("/subscribe/")
async def subscribe_to_plan(subscription: schemas.Subscription, session: Session = Depends(get_db)):
    try:
        db_subscription = models.Subscription(**subscription.dict())
        session.add(db_subscription)
        session.commit()
        session.refresh(db_subscription)
        return db_subscription
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")
    

from typing import List
@app.get("/subscriptions/", response_model=List[schemas.Subscription])
async def get_all_subscriptions(session: Session = Depends(get_db)):
    subscriptions = session.query(models.Subscription).all()
    return subscriptions


from database import SessionLocal

@app.post("/user-subscription-details/{sub_id}/{user_id}", response_model=dict)
async def get_user_subscription_details(sub_id: str, user_id: int, session: Session = Depends(get_db)):
    # Retrieve user by user_id
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve subscription by sub_id
    subscription = session.query(models.Subscription).filter(models.Subscription.sub_id == sub_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Create a new UserSubscription instance and add it to the session
    user_subscription = models.UserSubscription(user_id=user.id, subscription_id=subscription.id)
    session.add(user_subscription)
    session.commit()

    # Convert SQLAlchemy models to Pydantic schemas
    user_data = schemas.UserCreate.from_orm(user)
    subscription_data = schemas.Subscription.from_orm(subscription)

    # Combine user and subscription data into a single dictionary
    user_subscription_details = {
        "user": user_data.dict(),
        "subscription": subscription_data.dict(),
        "msg": "Request send successfully"
    }

    return user_subscription_details


from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import schemas
                                                           

# Endpoint for admin to accept a subscription request
@app.post("/accept-subscription/{user_id}/{sub_id}")
async def accept_subscription(user_id: int, sub_id: str, session: Session = Depends(get_db)):
    # Retrieve user subscription by user_id and sub_id
    user_subscription = session.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == user_id,
        models.UserSubscription.subscription_id == sub_id,
        models.UserSubscription.status == "Pending"
    ).first()
    
    print("User Subscription:", user_subscription)  # Debugging print statement

    if not user_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update the status of the subscription to "Accepted"
    user_subscription.status = "Accepted"
    session.commit()

    # Retrieve user and subscription details
    user = user_subscription.user
    subscription = user_subscription.subscription

    # Convert SQLAlchemy models to Pydantic schemas
    user_data = schemas.UserCreate.from_orm(user)
    subscription_data = schemas.Subscription.from_orm(subscription)

    # Combine user and subscription data into a single dictionary
    accepted_subscription_details = {
        "user": user_data.dict(),
        "subscription": subscription_data.dict()
    }

    return accepted_subscription_details



from fastapi import HTTPException
from dateutil.relativedelta import relativedelta

@app.post("/calculate-subscription-details/{user_id}/{sub_id}", response_model=schemas.SubscriptionDetails)
async def calculate_subscription_details(user_id: int, sub_id: str, session: Session = Depends(get_db)):
    # Retrieve user subscription by user_id and sub_id
    user_subscription = session.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == user_id,
        models.UserSubscription.subscription_id == sub_id
    ).first()
    
    if not user_subscription:
        raise HTTPException(status_code=404, detail="User subscription not found")

    # Check if the status of the subscription is "Accepted"
    if user_subscription.status != "Accepted":
        raise HTTPException(status_code=400, detail="Subscription is not accepted")

    # Retrieve subscription details
    subscription = session.query(models.Subscription).filter(models.Subscription.sub_id == sub_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Get the current date
    current_date = datetime.now()
    print("Subscription Month:", subscription.month)

    # Calculate the end date based on the subscription month
    end_date = current_date + relativedelta(months=int(subscription.month))

    # Prepare the response data
    response_data = {
        "user_id": user_id,
        "sub_id": sub_id,
        "start_date": current_date,
        "end_date": end_date,
        "total_price": subscription.amount,
        "no_of_play": 0,
        "plan_type": subscription.month,
        "status": "Paid"
    }

    # Store the subscription details in the database
    db_subscription = models.SubscriptionDetails(**response_data)
    session.add(db_subscription)
    session.commit()

    return response_data


@app.get("/user-subscriptions/{user_id}", response_model=dict)
async def get_user_subscriptions(user_id: int, session: Session = Depends(get_db)):
    # Retrieve user by user_id
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve user subscriptions by user_id
    user_subscriptions = session.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == user_id
    ).all()

    # List to store subscription details for the user
    subscription_details_list = []

    # Initialize adve_id
    adve_id = 1

    for user_subscription in user_subscriptions:
        # Retrieve subscription details
        subscription = user_subscription.subscription
        if subscription:
            # Get the current date
            current_date = datetime.now()

            # If the subscription is accepted, calculate the end date
            if user_subscription.status == "Accepted":
                end_date = current_date + relativedelta(months=int(subscription.month))
            else:
                # Set start and end date to None if subscription is not accepted
                start_date = None
                end_date = None

            # Retrieve start and end dates from SubscriptionDetails table
            if user_subscription.status == "Accepted":
                subscription_details = session.query(models.SubscriptionDetails).filter(
                    models.SubscriptionDetails.user_id == user_id,
                    models.SubscriptionDetails.sub_id == subscription.sub_id
                ).first()
                if subscription_details:
                    start_date = subscription_details.start_date
                    end_date = subscription_details.end_date

            # Prepare the response data
            subscription_details = {
                "user_id": user_id,
                "adve_id": adve_id,  # Add adve_id field
                "sub_id": subscription.sub_id,
                "start_date": start_date,
                "end_date": end_date,
                "total_price": subscription.amount,
                "no_of_play": 0,  # You may need to update this value based on your logic
                "plan_type": subscription.month,
                "status": user_subscription.status
            }

            subscription_details_list.append(subscription_details)
            adve_id += 1  # Increment adve_id
    response =  {
        "status_code": status.HTTP_201_CREATED,
        "message": "Subscripion list",
        "data": {
            "subscription_list": subscription_details_list
        }
    }
    return response


@app.post("/contact_us", response_model=schemas.ContactMessage)
def contact_us(message: schemas.ContactMessageCreate, db: Session = Depends(get_db)):
    db_message = models.ContactMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Step 3: Implement a GET API endpoint to retrieve all messages
@app.get("/contact_messages", response_model=List[schemas.ContactMessage])
def get_contact_messages(db: Session = Depends(get_db)):
    messages = db.query(models.ContactMessage).all()
    return messages

# Step 4: Add functionality to update the status of a message when reviewed by the admin
@app.put("/review_message/{message_id}", response_model=schemas.ContactMessage)
def review_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(models.ContactMessage).filter(models.ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    message.status = "seen"
    db.commit()
    return message



@app.post("/feedback", response_model=schemas.FeedbackMessage)
def contact_us(message: schemas.FeedbackMessageCreate, db: Session = Depends(get_db)):
    db_message = models.FeedbackMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Step 3: Implement a GET API endpoint to retrieve all messages
from sqlalchemy.orm import joinedload

@app.get("/feedback_messages", response_model=List[schemas.FeedbackMessage])
def get_contact_messages(db: Session = Depends(get_db)):
    messages = (
        db.query(models.FeedbackMessage)
        .options(joinedload(models.FeedbackMessage.user))
        .all()
    )
    return messages

# Step 4: Add functionality to update the status of a message when reviewed by the admin
@app.put("/review_feedback_message/{message_id}", response_model=schemas.FeedbackMessage)
def review_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(models.FeedbackMessage).filter(models.FeedbackMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    message.status = "seen"
    db.commit()
    return message



from fastapi import HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session


@app.post("/update_location/{id}", response_model=schemas.RikshawLocationUpdate)
def update_location(
    id: int = Path(..., title="Rikshaw User ID", description="The ID of the rikshaw user"),
    location: schemas.RikshawLocationUpdate = Body(..., title="Location", description="The location data to update"),
    session: Session = Depends(get_db)
):
    # Check if the rikshaw user with the provided ID exists
    rikshaw_user = session.query(models.RikshawUser).filter(models.RikshawUser.id == id).first()
    if not rikshaw_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rikshaw user not found")

    # Check if the location entry for the user ID already exists
    existing_location = session.query(models.RikshawLocation).filter(models.RikshawLocation.rikshaw_user_id == id).first()
    if existing_location:
        # Update the existing location entry
        existing_location.latitude = location.latitude
        existing_location.longitude = location.longitude
        session.commit()
        return {
            "latitude": existing_location.latitude,
            "longitude": existing_location.longitude,
            "rikshaw_user_id": existing_location.rikshaw_user_id
        }
    else:
        # Create a new location entry
        db_location = models.RikshawLocation(
            latitude=location.latitude,
            longitude=location.longitude,
            rikshaw_user_id=id
        )
        session.add(db_location)
        session.commit()
        return {
            "latitude": db_location.latitude,
            "longitude": db_location.longitude,
            "rikshaw_user_id": db_location.rikshaw_user_id
        }

# Define the get_location endpoint
@app.get("/get_all_locations", response_model=schemas.GetLocationsResponse)
def get_all_locations(session: Session = Depends(get_db)):
    # Retrieve all location records from the database
    locations = session.query(models.RikshawLocation).all()
    if not locations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No locations found")

    # Prepare the response data
    data = [{"id": loc.id, "rikshaw_user_id": loc.rikshaw_user_id, "latitude": loc.latitude, "longitude": loc.longitude} for loc in locations]

    # Prepare the response
    response = {
        "status_code": status.HTTP_200_OK,
        "message": "Location update",
        "data": {
            "locations": data
        }
    }
    return response

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends

# Configure AWS credentials
AWS_ACCESS_KEY_ID = 'AKIA2UC3BSG7WK7KCY5D'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
S3_BUCKET_NAME = 'pro-2'

def upload_image_to_s3(image: UploadFile, name: str, session: Session):
    try:
        # Upload image to S3
        s3_response = s3_client.upload_fileobj(image.file, S3_BUCKET_NAME, image.filename)
        # Get the S3 URL of the uploaded image
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{image.filename}"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image to S3")

    # Save data to the database
    try:
        db_data = models.Image(name=name, s3_url=s3_url)
        session.add(db_data)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data to database")

    return {"message": "Image uploaded successfully", "s3_url": s3_url}

# Define the API endpoint
@app.post("/our_client/")
def our_client(image: UploadFile = File(...), name: str = Form(...), session: Session = Depends(get_db)):
    return upload_image_to_s3(image, name, session)

@app.get("/our_clients/", response_model=schemas.OurClientsResponse)
def get_our_clients(session: Session = Depends(get_db)):
    # Query the database to get the image data
    images = session.query(models.Image).all()
    
    # Format the response
    response_data = {
        "status_code": status.HTTP_200_OK,
        "message": "Location update",
        "data": {
            "our_clients": [{"name": image.name, "s3_url": image.s3_url} for image in images]
        }
    }
    
    return response_data



@app.post('/logout')
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    token=dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_record = db.query(models.TokenTable).all()
    info=[]
    for record in token_record :
        print("record",record)
        if (datetime.utcnow() - record.created_date).days >1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
        db.commit()
        
    existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id, models.TokenTable.access_token==token).first()
    if existing_token:
        existing_token.status=False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message":"Logout Successfully"} 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

