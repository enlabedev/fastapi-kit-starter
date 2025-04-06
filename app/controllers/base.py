from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
)

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session


# Protocol to enforce the presence of an `id` attribute
class Identifiable(Protocol):
    id: Any


ModelType = TypeVar("ModelType", bound=Identifiable)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ControllerBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    def q(self, *criterion: Any, db: Session) -> Query:
        """
        Filter by criterion, ex: User.q(User.name=='Thuc', User.status==1)
        """
        if criterion:
            return db.query(self.model).filter(*criterion)
        return db.query(self.model)

    def q_by(self, db: Session, **kwargs: Any) -> Query:
        """
        Filter by named params, ex: User.q(name='Thuc', status=1)
        """
        return db.query(self.model).filter_by(**kwargs)

    def first(self, db: Session, *criterion: Any) -> Optional[ModelType]:
        """
        Get first by list of criterion.
        """
        result = self.q(*criterion, db=db).first()
        return cast(Optional[ModelType], result)

    def first_or_error(self, db: Session, *criterion: Any) -> ModelType:
        """
        Get first by list of criterion or raise 404 error.
        """
        response = self.first(db, *criterion)
        if not response:
            raise HTTPException(status_code=404, detail="Item not found")
        return response

    def all(self, db: Session, *criterion: Any) -> List[ModelType]:
        """
        Get all records by list of criterion.
        """
        return self.q(*criterion, db=db).all()

    def get(self, id: Any, db: Session, error_out: bool = False) -> Optional[ModelType]:
        """
        Get a single record by ID.
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj and error_out:
            raise HTTPException(status_code=404, detail="Item not found")
        return obj

    def create(self, db: Session, *, schema: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        """
        try:
            item_data = jsonable_encoder(schema)
            model = self.model(**item_data)  # type: ignore
            db.add(model)
            db.commit()
            db.refresh(model)
            return model
        except IntegrityError as e:
            db.rollback()
            message = str(e.orig).split(":")[-1].replace("\n", "").strip()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=message,
            )

    def read(self, db: Session, *, skip: int = 0, limit: int = 5000) -> List[ModelType]:
        """
        Read multiple records with pagination.
        """
        result = (
            db.query(self.model).order_by(self.model.id).offset(skip).limit(limit).all()
        )
        return result

    def update(
        self,
        db: Session,
        *,
        model: ModelType,
        schema: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update an existing record.
        """
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

    def delete(self, db: Session, *, id: Any) -> ModelType:
        """
        Delete a record by ID.
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(obj)
        db.commit()
        return obj
