import datetime as _dt

import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt
import passlib.hash as _hash
import sqlalchemy.orm as _orm

import database as _database
import models as _models
import schemas as _schemas

JWT_SECRET = "123"
oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    print("Yes")
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(email, db)
    if not user or not user.verify_password(password):
        return False
    return user


async def create_token(user: _models.User) -> _schemas.Token:
    user_obj = _schemas.User.from_orm(user)
    token = _jwt.encode(user_obj.dict(), JWT_SECRET)
    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2_scheme),
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(
            status_code=401, detail="Incorrect email or password"
        )

    return _schemas.User.from_orm(user)


async def create_lead(user: _schemas.User, db: _orm.Session, lead: _schemas.LeadCreate):
    lead = _models.Lead(**lead.dict(), owner_id=user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return _schemas.Lead.from_orm(lead)


async def get_leads(user: _schemas.User, db: _orm.Session):
    leads = db.query(_models.Lead).filter_by(owner_id=user.id)
    return list(map(_schemas.Lead.from_orm, leads))


async def _lead_selector(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = (
        db.query(_models.Lead)
        .filter_by(owner_id=user.id)
        .filter(_models.Lead.id == lead_id)
        .first()
    )

    if lead is None:
        raise _fastapi.HTTPException(status_code=404, detail="Lead does not exist")

    return lead


async def get_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = await _lead_selector(lead_id=lead_id, user=user, db=db)
    return _schemas.Lead.from_orm(lead)


async def delete_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = await _lead_selector(lead_id=lead_id, user=user, db=db)
    db.delete(lead)
    db.commit()


async def update_lead(
    lead_id: int, lead: _schemas.LeadCreate, user: _schemas.User, db: _orm.Session
):
    selected_lead = await _lead_selector(lead_id=lead_id, user=user, db=db)
    selected_lead.first_name = lead.first_name
    selected_lead.last_name = lead.last_name
    selected_lead.email = lead.email
    selected_lead.company = lead.company
    selected_lead.note = lead.note
    selected_lead.date_last_updated = _dt.datetime.now()

    db.commit()
    db.refresh(selected_lead)
    return _schemas.Lead.from_orm(selected_lead)
