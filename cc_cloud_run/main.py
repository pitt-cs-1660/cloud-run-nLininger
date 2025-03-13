from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore
from typing import Annotated
import datetime

app = FastAPI()

# mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/template")

# init firestore client
db = firestore.Client()
votes_collection = db.collection("votes")


@app.get("/")
async def read_root(request: Request):
    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # stream all votes; count tabs / spaces votes, and get recent votes

    # streaming all votes
    votes = votes_collection.stream()

    # variables to hold vote counts
    recent_votes = []
    spaces_count = 0
    tabs_count = 0

    # counting votes logic
    for vote in votes:
        
        # format vote data
        vote_data = vote.to_dict()
        
        # determine if vote is tab or space, then tabulate the vote
        if vote_data["team"] == "TABS":
            tabs_count += 1
        elif vote_data["team"] == "SPACES":
            spaces_count += 1
        
        # store vote in recent votes
        recent_votes.append({
            "team": vote_data["team"],
            "time_cast": vote_data["time_cast"]
        })

    # format recent votes to record first 5 in desc order
    recent_votes = sorted(recent_votes, key=lambda x: x["time_cast"], reverse=True)[:5]
    
    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tabs_count": tabs_count,
        "spaces_count": spaces_count,
        "recent_votes": recent_votes
    })


@app.post("/")
async def create_vote(team: Annotated[str, Form()]):
    if team not in ["TABS", "SPACES"]:
        raise HTTPException(status_code=400, detail="Invalid vote")

    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # create vote and store in Firestore
    vote_data = {
        "team": team,
        "time_cast": datetime.datetime.utcnow().isoformat()
    }
    votes_collection.add(vote_data)

    # create a new vote document in firestore
    return {"detail": "Vote creation success!"}

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
