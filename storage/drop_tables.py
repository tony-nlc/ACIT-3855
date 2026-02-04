from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

ENGINE = create_engine("sqlite:///fitness-app.db")
def make_session():
    return sessionmaker(bind=ENGINE)

models.Meal.metadata.drop_all(ENGINE)
models.Exercise.metadata.drop_all(ENGINE)