import json
from datetime import datetime

from pymysql import TIMESTAMP
from sqlalchemy import Column, Integer, String, func, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relation, DeclarativeMeta, registry

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Comments(BaseModel):
    __tablename__ = "comments"

    email = Column(String(320), nullable=False)
    text = Column(String(500), nullable=False)

    files = relation("Files")


class Files(BaseModel):
    __tablename__ = "files"

    uri = Column(String(1000), nullable=False)
    comment_id = Column(ForeignKey('comments.id', ondelete='CASCADE'))


def new_alchemy_encoder(revisit_self = False, fields_to_expand = []):
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if revisit_self:
                    if obj in _visited_objs:
                        return None
                    _visited_objs.append(obj)

                # go through each field in this SQLalchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    val = obj.__getattribute__(field)

                    # is this field another SQLalchemy object, or a list of SQLalchemy objects?
                    if isinstance(val.__class__, DeclarativeMeta) or (isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__, DeclarativeMeta)):
                        # unless we're expanding this field, stop here
                        if field not in fields_to_expand:
                            # not expanding this field: set it to None and continue
                            fields[field] = None
                            continue

                    if isinstance(val, datetime):
                        fields[field] = val.strftime("%H:%M %m.%d.%Y")
                        continue
                    elif isinstance(val, registry):
                        continue

                    fields[field] = val
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder
