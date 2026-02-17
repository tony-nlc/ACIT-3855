from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

ENGINE = create_engine("mysql+mysqldb://admin:password@127.0.0.1:3306/fitness-app")
def make_session():
    return sessionmaker(bind=ENGINE)

models.Meal.metadata.create_all(ENGINE)
models.Exercise.metadata.create_all(ENGINE)
