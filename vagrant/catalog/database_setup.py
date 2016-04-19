# coding=utf-8
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, BLOB
import re
import uuid
from werkzeug.security import generate_password_hash,\
                              check_password_hash

Base = declarative_base()

class Category(Base):
  __tablename__ = 'category'
  
  parent_flag = False
  selected_flag = False
  
  id = Column(
    Integer,
    primary_key = True
  )
  name = Column(
    String,
    nullable = False
  )
  parent = Column(
    id.type
  )

  @classmethod
  def get_root(cls):
    """ Return a root category object from database.
    
    The root category is which has value 0 in parent field.
    """
    root = session.query(cls).filter_by(parent = 0).first()
    return root
  
  @classmethod
  def get_children(cls, id, count_items = False):
    """ Return children categories of Category ID from argument.
    
    If count_items has value True, 
    All children category will try to get counted number of 
    items that belong to.
    """
    instance_list = []
    
    fetched_children = session.query(cls).\
                               filter_by(parent = id).all()
    if len(fetched_children) > 0:
      instance_list += fetched_children
    
    if count_items == True:
      for i in instance_list:
        i.count = Item.count_by_category(i.id)
      
    return instance_list
  
  @classmethod
  def get_by_id(cls, id, count_items = False):
    """ Return a category fetched by a category ID from argument
    
    If count_items has value True, 
    category will try to get counted number of items that belongs to.
    """
    base_instance = session.query(cls).filter_by(id = id).first()
    if not base_instance and count_items == True:
      base_instance.count = Item.count_by_category(base_instance.id)
    return base_instance
  
  def has_child(self):
    """ Return True if category has at least one child category,
        otherwise return False
    """
    count = session.query(func.count(self.__class__.id)).filter_by(parent = self.id).first()[0]
    if count > 0:
      return True
    else:
      return False
  
  def add(self):
    """ Insert a category instance to database.
    """
    return session.add(self)
    
  def update(self):
    """ Update(or merge) a category instance to database.
    """
    return session.merge(self)
    
  def delete(self):
    """ Delete a category instance from database.
    """
    return session.delete(self)

  def __repr__(self):
    str = '__repr__ ' + self.__class__.__name__
    str += ' <'
    str += 'id = %s, name = %s, parent = %s'
    str += '>'
    return str % (self.id, self.name, self.parent)

class User(Base):
  __tablename__ = 'user'
  
  id = Column(
    String,
    primary_key = True
  )
  uuid = Column(
    String(32)
  )
  last_name = Column(
    String
  )
  first_name = Column(
    String
  )
  password = Column(
    String
  )
  deleted = Column(
    String(1)
  )
  
  def add(self):
    """ Insert a user instance to database.
    """
    self.uuid = uuid.uuid4().hex
    return session.add(self)
  
  def merge(self):
    """ Update a user instance to database.
    """
    return session.merge(self)
    
  def commit(self):
    """ Commit the current transaction.
    """
    return session.commit()
    
  @classmethod
  def get_by_id(cls,user_id):
    """ Return a user instance fetched by a user ID from argument
    """
    return session.query(cls).filter_by(id = user_id).first()

  def password_encode(self, password_text):
    """ Return hashed password string using texted password string  """
    self.password = generate_password_hash(password_text)
    return self.password
  
  def verify_password(self, password_text):
    """ Verify if the saved password and received password is equal,
        if both are equal then return True, otherwise False.
    """
    return check_password_hash(self.password, password_text)
  
  def __repr__(self):
    str = '__repr__ ' + self.__class__.__name__
    str += ' <'
    str += 'uuid = %s, id = %r, last_name = %r, first_name = %r, '
    str += 'password = %r, deleted = %r'
    str += '>'
    return str % (self.uuid, self.id, 
                  self.last_name, self.first_name, 
                  self.password, self.deleted)

class Item(Base):
  __tablename__ = 'item'
  category = relationship(Category)
  user = relationship(User)
  
  id = Column(
    Integer,
    primary_key = True
  )
  name = Column(
    String,
    nullable = False
  )
  deleted = Column(
    String(1)
  )
  category_id = Column(
    ForeignKey('category.id')
  )
  user_id = Column(
    ForeignKey('user.id')
  )
  longtext = Column(
    String()
  )
  image = Column(
    BLOB()
  )

  def add(self):
    """ Insert a item instance to database.
    """
    if Category.get_by_id(self.category_id).has_child() == True:
      return False, 'error', 'Selected Category ID is parent of others.'
    session.add(self)
    return True, 'success', 'Item is added.'
    
  def update(self):
    """ Update a item instance to database.
    """
    result = session.merge(self)
    return result
    
  def delete(self):
    """ Delete a item instance from database.
    """
    result = session.delete(self)
    return result
  
  @classmethod
  def delete_by_id(cls, item_id):
    """ Delete a item instance from database using item ID.
    """
    result = session.query(cls).filter_by(id = item_id).delete()
    print result
    session.commit()
    return result
  
  def commit(self):
    """ Commit the current transaction.
    """
    result = session.commit()
    return result
  
  @classmethod
  def count_by_category(cls, category_id):
    """ Return a counted number of items that belong to a category """
    return session.query(func.count(cls.id)).\
                              filter_by(category_id = category_id).first()[0]
  
  @classmethod
  def get_by_category(cls, category_id = None):
    """ Return a list of items that belong to a category """
    if category_id == None:
      return []
    #initiate list
    items = []
    #
    items += session.query(cls).filter_by(category_id = category_id).all()
    category = Category.get_by_id(category_id)
    
    if category != None and category.has_child():
      categories = Category.get_children(category.id)
      for c in categories:
        items += session.query(cls).filter_by(category_id = c.id).all()
    return items
  
  @classmethod
  def get_by_id(cls, id = None):
    """ Return an item instance using item ID """
    item = session.query(cls).filter_by(id = id).first()
    return item
  
  @property
  def serialize(self):
    """ Serialize item instance for making JSON format output """
    entry = {}
    entry['id'] = self.id
    entry['name'] = self.name
    entry['category_id'] = self.category_id
    entry['user_id'] = self.user_id
    entry['longtext'] = self.longtext.encode('utf8')
    return entry
    
  def __repr__(self):
    #return '' + str(self.id) + self.longtext.encode('utf-8')
    str_line = '{Table: ' + self.__class__.__name__ + '}'
    str_line += ' <'
    str_line += 'id = %s, name = %s, '
    str_line += 'catagory_id = %s, user_id = %s, '
    str_line += 'deleted = %s, longtext = %r , image = %r'
    str_line += '>'
    str_line = str_line % (self.id, self.name, 
                       self.category_id, self.user_id, 
                       self.deleted, self.longtext,
                       self.image)
    return str_line

## At end of file
engine = create_engine('sqlite:///catalog.db')#, convert_unicode = True
Base.metadata.create_all(engine)

#Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
