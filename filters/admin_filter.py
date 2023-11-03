from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
import os
from dotenv import load_dotenv

load_dotenv()
adm_list = list(map(int,os.getenv('ADMIN_IDS').split(sep=',')))




