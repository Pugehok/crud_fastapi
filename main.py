from typing import List
import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm

import service
import service as _services, schemas as _schemas
from fastapi.middleware.cors import CORSMiddleware as _CORS


app = _fastapi.FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8002",
]

app.add_middleware(
    _CORS,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/users")
async def create_user(
    user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
) -> _schemas.Token:
    db_user = await _services.get_user_by_email(user.email, db=db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")
    created_user = await _services.create_user(user, db)
    return await _services.create_token(created_user)


@app.post("/api/token")
async def create_token(
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):

    print('Отработала')
    user = await _services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Creeditionals")

    return await _services.create_token(user)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.post("/api/leads", response_model=_schemas.Lead)
async def create_lead(
    lead: _schemas.LeadCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.create_lead(user=user, lead=lead, db=db)


@app.get("/api/leads", response_model=List[_schemas.Lead])
async def get_leads(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_leads(user=user, db=db)


@app.get("/api/lead/{lead_id}", status_code=200)
async def get_lead_by_id(
    lead_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_lead(lead_id, user, db)


@app.get("/api/message")
async def get_messages():

    return "Hello World"


@app.delete("/api/lead/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    await _services.delete_lead(lead_id, user, db)
    return {"message", "Successfully deleted lead"}


@app.put("/api/lead/{lead_id}", status_code=200)
async def update_lead(
    lead_id: int,
    lead: _schemas.LeadCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    await service.update_lead(lead_id, lead, user, db)
    return {"message": "Successfully updated"}
