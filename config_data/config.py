from dotenv import load_dotenv
from dataclasses import dataclass
import os

@dataclass
class Db_config:
    host : str
    db_name : str
    user : str
    password : str

@dataclass
class Bot_config:
    token : str
    admin_ids : list[int]

@dataclass
class Config:
    tg_bot : Bot_config
    db : Db_config

load_dotenv()
 
config = Config(
    tg_bot=Bot_config(
        token = os.getenv('TOKEN'),
        admin_ids = list(map(int,os.getenv('ADMIN_IDS').split(sep=',')))
        ),

    db=Db_config(
        db_name = os.getenv('DB_NAME'),
        host = os.getenv('HOST'),
        user = os.getenv('USER'),
        password = os.getenv('PASSWORD')
    )
    
)


