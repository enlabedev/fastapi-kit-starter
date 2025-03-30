from typing import Any, Dict, Generic, List, Type, TypeVar, Union, Optional
from pydantic import BaseModel
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.base import Base
from app.config.database import SessionLocal

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ControllerBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def q(self, *criterion, db: Session):
        """
        Filter by criterion, ex: User.q(User.name=='Thuc', User.status==1)
        :param criterion:
        :return:
        """
        if criterion:
            return db.query(self.model).filter(*criterion)
        return db.query(self.model)

    def q_by(self, db: Session = SessionLocal(), **kwargs):
        """
        Filter by named params, ex: User.q(name='Thuc', status=1)
        :param kwargs:
        :return:
        """
        return db.query(self.model).filter_by(**kwargs)

    def first(self, *criterion):
        """
        Get first by list of criterion, ex: user1 = User.first(User.name=='Thuc1')
        :param criterion:
        :return:
        """
        return self.q(*criterion).first()

    def first_or_error(self, *criterion):
        """
        Get first by list of criterion, ex: user1 = User.first(User.name=='Thuc1')
        if according to where condition no data match than it gives not found page
        :param criterion:
        :return:
        """
        response = self.first(*criterion)
        if not response:
            raise HTTPException(status_code=404, detail="Item not found")
        return response

    def all(self, *criterion):
        """
        Get all of the records by list of criterion, ex: user1 = User.first(User.name=='Thuc1')
        if according to where condition no data match than it gives not found page
        :param criterion:
        :return:
        """
        return self.q(*criterion).all()

    def get(
        self, id: Any, db: Session = SessionLocal(), error_out: bool = False
    ) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj and error_out:
            raise HTTPException(status_code=404, detail="Item not found")
        return obj

    def create(self, db: Session, *, schema: CreateSchemaType) -> ModelType:
        try:
            item_data = jsonable_encoder(schema)
            model = self.model(**item_data)
            db.add(model)
            db.commit()
            db.refresh(model)
            return model
        except IntegrityError as e:
            db.rollback()
            message = str(e.orig).split(":")[-1].replace("\n", "").strip()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message
            )

    def read(self, db: Session, *, skip: int = 0, limit: int = 5000) -> List[ModelType]:
        return (
            db.query(self.model).order_by(self.model.id).offset(skip).limit(limit).all()
        )

    def update(
        self,
        db: Session = SessionLocal(),
        *,
        model: ModelType,
        schema: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        item_data = jsonable_encoder(model)
        if isinstance(schema, dict):
            update_data = schema
        else:
            update_data = schema.model_dump(exclude_unset=True)
        for field in item_data:
            if field in update_data:
                setattr(model, field, update_data[field])
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def delete(self, db: Session = SessionLocal(), *, id: str) -> ModelType:
        obj = db.query(self.model).filter(self.model.id == id).first()
        db.delete(obj)
        db.commit()
        return obj
