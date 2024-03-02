from typing import List
import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm

import service as _services, schemas as _schemas

app = _fastapi.FastAPI()


@app.post("/api/users")
async def create_user(user: _schemas.UserCreate,
                      db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")
    await _services.create_user(user, db)

    return await _services.create_token(user)


@app.post("/api/token")
async def create_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
                       db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Creeditionals")

    return await _services.create_token(user)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.post("/api/leads", response_model=_schemas.Lead)
async def create_lead(lead: _schemas.LeadCreate,
                      user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                      db: _orm.Session = _fastapi.Depends(_services.get_db)
                      ):
    return await _services.create_lead(user=user, lead=lead, db=db)


@app.get("/api/leads", response_model=List[_schemas.Lead])
async def get_leads(user: _schemas.User = _fastapi.Depends(_services.get_current_user), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_leads(user=user, db=db)


