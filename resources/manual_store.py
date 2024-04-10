from sqlalchemy import Column, Integer, String, Date, Boolean
import uuid

import sys
import os
sys.path.append(os.path.abspath('..'))

from base import Base, GUID


class Store(Base):
    __tablename__ = 'stores'

    id = Column(GUID, primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String)
    url = Column(String)
    access_token = Column(String)
    date = Column(Date)
    to_email = Column(String)
    cc_email = Column(String)
    dev_email = Column(String)
    fixy = Column(Boolean)
    fixy_service_id = Column(Integer, nullable=True)
    fixy_client_id = Column(Integer, nullable=True)
    fixy_branch_code = Column(Integer, nullable=True)
    fixy_company = Column(String, nullable=True)
    fixy_sender = Column(String, nullable=True)

