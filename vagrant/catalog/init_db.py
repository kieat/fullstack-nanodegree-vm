# coding=utf-8
from database_setup import Category, Item, User, Base, session

category_list = [
[1, 'Business Technology', 13],
[2, 'Certification', 13],
[3, 'Computer Science', 13],
[4, 'Databases & Big Data', 13],
[5, 'Digital Audio, Video & Photography', 13],
[6, 'Games & Strategy Guides', 13],
[7, 'Graphics & Design', 13],
[8, 'Hardware & DIY', 13],
[9, 'History & Culture', 13],
[10, 'Internet & Social Media', 13],
[11, 'Mobile Phones, Tablets & E-Readers', 13],
[12, 'Networking & Cloud Computing', 13],
[13, 'Computers & Technology', 0],
]

item_list = {
1: ['1:Book 1', '1:Book 2', '1:Book 3'],
2: ['2:Book 1', '2:Book 2', '2:Book 3'],
}

user_list = [
['k@g.com', 'Jackson', 'Michael', 'pass'],
['t@g.com', 'Timberlake', 'Justin', 'pass'],
]

def build_category():
  for c in category_list:
    new_category = Category(id = c[0], name = c[1], parent = c[2])
    new_category.add()
    
def build_item(category_id):
  if category_id in item_list:
    for i in item_list[category_id]:
      new_item = Item(name = i)
      new_item.category_id = category_id
      new_item.user_id = user_list[1][0]
      new_item.longtext = '서태지'.decode('utf8')
      new_item.add()
    
def build_user():
  for u in user_list:
    new_user = User(id = u[0])
    new_user.last_name = u[1]
    new_user.first_name = u[2]
    new_user.password = new_user.password_encode(u[3])
    new_user.add()

def delete_all_data(force = 0):
  if force == 0:
    to_delete = input('Delete all tables\'s entries before start?(1=Yes,0=No): ')
  else:
    to_delete = 1
  
  if to_delete == 1:
    for t in Base.metadata.sorted_tables:
      session.execute(t.delete())
  else:
    print '<Not delete anything>'

def printout_all_data():
  for subclass in Base.__subclasses__():
    for instance in session.query(subclass).all():
      print instance
if __name__ == '__main__':
  delete_all_data(1)
  
  build_user()
  
  build_category()
  
  for c in category_list:
    build_item(c[0])
  
  session.commit()
  printout_all_data()
  