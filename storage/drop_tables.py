from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

ENGINE = create_engine("mysql+mysqldb://admin:password@127.0.0.1:3306/fitness-app")
def make_session():
    return sessionmaker(bind=ENGINE)

models.Meal.metadata.drop_all(ENGINE)
models.Exercise.metadata.drop_all(ENGINE)