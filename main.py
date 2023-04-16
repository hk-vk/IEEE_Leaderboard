import firebase_admin
from fastapi import FastAPI, HTTPException, Header, Depends
from firebase_admin import auth
from firebase_admin import credentials, firestore, initialize_app
from google.cloud import firestore
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
default_app = initialize_app(cred)
db = firebase_admin.firestore.client()

# Initialize FastAPI app
app = FastAPI()


# Authentication helper function to verify user's Firebase ID token
async def verify_token(authorization: str = Header(None)):
    """
    Helper function to verify user's Firebase ID token included in the authorization header of the request.
    """
    try:
        # Check if authorization header is present and if it is valid
        if authorization is None:
            raise HTTPException(status_code=401, detail="Authorization header is required")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header must start with Bearer")
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return uid

# Endpoint to register a new team
@app.post("/register")
async def register(email: str, password: str, team_name: str, points: int, members: list,
                   token: dict = Depends(verify_token)):
    """
    Endpoint to register a new team.
    """
    try:
        user_id = token.get("uid")

        # Create a new Firebase Auth user
        user = auth.create_user(
            email=email,
            password=password
        )

        # Validate inputs
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        if len(email) == 0:
            raise HTTPException(status_code=400, detail="Email cannot be empty")
        if len(password) == 0:
            raise HTTPException(status_code=400, detail="Password cannot be empty")
        team_name = team_name.strip()
        if not team_name:
            raise HTTPException(status_code=400, detail="Team name cannot be empty")
        if not members:
            raise HTTPException(status_code=400, detail="Members cannot be empty")
        if len(team_name) > 30:
            raise HTTPException(status_code=400, detail="Team name cannot be more than 30 characters")
        if len(members) > 4 or len(members) < 1:
            raise HTTPException(status_code=400, detail="Team must have between 1 and 4 members")

        # Create a new team in the Firestore database
        new_team_ref = db.collection("teams").document()
        new_team_ref.set({
            "team_name": team_name,
            "points": points,
            "members": members,
            "leader": user_id
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")
    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "Team registered successfully"}))


# Endpoint to retrieve the leaderboard
@app.get("/leaderboard")
async def leaderboard(token: dict = Depends(verify_token)):
    try:
        user_id = token.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        # Retrieve top 10 teams from the Firestore database, ordered by points
        teams = db.collection("teams").order_by("points", direction=firestore.Query.DESCENDING).stream().limit(10)
        leaderboard = {}
        for team in teams:
            leaderboard[team.id] = team.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")
    return JSONResponse(content=jsonable_encoder(leaderboard))


