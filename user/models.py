from user import auth
from datetime import timedelta
from fastapi import status, HTTPException
from user import schemas
from db import db
import uuid



async def check_user_exists(new_username,new_email):
    username_check = await db.user.find_one({"username":new_username})
    if username_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken.")
    
    email_check = await db.user.find_one({"email": new_email})
    print(new_email)
    if email_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with given e-mail already exists")
    return False


async def add_user(request):
    user_data = request.dict()
    user_exists =await check_user_exists(user_data["username"], user_data["email"])
    if not user_exists:
        user_data["password"] = auth.Hash.get_password_hash(user_data["password"])
        user_data["_id"] = uuid.uuid4().hex
        new_user = await db.user.insert_one(user_data)
        created_user = await db.user.find_one({"_id":new_user.inserted_id})
        return created_user




async def login(request):
    user = await db.user.find_one({"username": request.username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid credentials")
    if not auth.Hash.verify_password(request.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid password")
       
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
        )
    return {"access_token": access_token, "token_type": "bearer"}


#this function is only for fastapi swagger ui authorization can delete it 
async def swagger_auth(request):
    user = await db.user.find_one({"username": request.username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid credentials")
    if not auth.Hash.verify_password(request.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid password")
       
    access_token = auth.create_access_token(
        data={"sub": user["username"]}, 
        )
    return {"access_token": access_token, "token_type": "bearer"}



def allowed_to_create(model_name):
    if model_name == schemas.TypeModel.Customer:
        return ["Visitor"]
    if model_name == schemas.TypeModel.Admin:
        return ["Admin", "Agent", "Customer", "Visitor"]
    if model_name == schemas.TypeModel.Agent:
        return ["Customer", "Visitor"]
    return []

#function to fix
def allowed_to_edit(user, current_user, record = {}):
    if current_user["userType"] == "Admin":
        return True
    elif current_user["userType"] == "Agent" and user["created_by"] == current_user["_id"]:
        return True
    elif record.get("owner") == current_user["_id"]:
        return True
    elif record.get("created_by") == current_user["_id"]:
        return True




async def update_user(id, data):
    if len(data) < 1:
        return False
    user = await db.user.find_one({"_id": id})
    if user:
# implement below to check if the user exists in the database while excluding the current user ...
        # user_exists =await check_user_exists(data["username"], data["email"])
        # if not user_exists:
            if data.get("password"):
                data["password"] = auth.Hash.get_password_hash(data["password"])
            updated_user = await db.user.update_one(
                {"_id": id}, {"$set": data}
            )
            if updated_user:
                return data
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User not updated")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with that id not found")



async def delete_user(id: str):
    user = await db.user.find_one({"_id":id})
    if user:
        await db.user.delete_one({"_id":id})
        return True



def get_user_details(id):
    user = db.users.find_user_by_id(id)
    user["kiosks"] = [i for i in db.kiosks.find({"owner": id})]
    user["users"] = users_created_by(user)
    return user

def users_created_by(current_user):
    users = [current_user["username"]]
    cursor = db.users.find({"$or": [
        {"created_by": current_user["_id"]},
        {"owner": current_user["username"]}]})
    users.extend([user["username"] for user in cursor])
    return users


async def all_users():
    users = []
    async for user in db.user.find():
        users.append(user)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No users available")
    return users

    
def admin_list():
    cursor = db.users.find({"userType": "Admin"})
    return [user for user in cursor]

def agent_list():
    cursor = db.users.find({"userType": "Agent"})
    return [user for user in cursor]

async def find_user(user):
    users = []
    async for user in db.user.find({"name":user}):
        users.append(user)
    return users

async def find_user_by_id(id):
    user = await db.user.find_one({"_id": id})
    return user

def get_user_kiosks(current_user):
    cursor = db.kiosks.find({"owner": current_user["_id"]})
    return [kiosk for kiosk in cursor]
