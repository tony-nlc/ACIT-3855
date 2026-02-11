from sqlalchemy import Integer,BigInteger, String, DateTime
from sqlalchemy.orm import mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Exercise(Base):
    __tablename__ = "exercise"
    id = mapped_column(Integer, primary_key=True)
    trace_id = mapped_column(String(36))
    user_id = mapped_column(String(50), index=True) # Added length
    source_device = mapped_column(String(100), nullable=True)
    exercise_id = mapped_column(String(50), unique=True)
    record_timestamp = mapped_column(DateTime)
    batch_timestamp = mapped_column(DateTime)
    type = mapped_column(String(100))
    duration_min = mapped_column(Integer)
    avg_heart_rate = mapped_column(Integer)
    peak_heart_rate = mapped_column(Integer, nullable=True)
    
    def to_dict(self):
            dict_rec = self.__dict__.copy()
            if '_sa_instance_state' in dict_rec:
                del dict_rec['_sa_instance_state']
            dict_rec['record_timestamp'] = self.record_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            dict_rec['batch_timestamp'] = self.batch_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            return dict_rec
class Meal(Base):
    __tablename__ = "meal"
    id = mapped_column(Integer, primary_key=True)
    trace_id = mapped_column(String(36))
    user_id = mapped_column(String(50), index=True) # Added length
    source_device = mapped_column(String(100), nullable=True)
    meal_id = mapped_column(String(50), unique=True)
    record_timestamp = mapped_column(DateTime)
    batch_timestamp = mapped_column(DateTime)
    calories = mapped_column(Integer)
    meal_type = mapped_column(String(100))
    carbs_g = mapped_column(Integer, nullable=True)
    protein_g = mapped_column(Integer, nullable=True)
    fat_g = mapped_column(Integer, nullable=True)
    
    def to_dict(self):
            dict_rec = self.__dict__.copy()
            if '_sa_instance_state' in dict_rec:
                del dict_rec['_sa_instance_state']
            dict_rec['record_timestamp'] = self.record_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            dict_rec['batch_timestamp'] = self.batch_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            return dict_rec