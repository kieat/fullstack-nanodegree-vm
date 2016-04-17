from flask import Blueprint, render_template, session
from database_setup import Category, Item

blueprint = Blueprint('category', __name__)

@blueprint.route('/')
@blueprint.route('/category/<int:cid>')
@blueprint.route('/category/<int:cid>/item/<int:item_id>')
def home(cid = None, item_id = None):

  #Check input: Category ID
  if cid == None:
    category_id = Category.get_root().id
  else:
    category_id = cid
  
  #Get one that is specified
  categories = [] + [Category.get_by_id(category_id)]
  
  #Get children
  if len(categories) == 1:
    children = Category.get_children(category_id, count_items = True)
    if len(children) == 0: #If no children, then get parent of it
      parent_id = categories[0].parent
      categories = [] + [Category.get_by_id(parent_id)]
      #get children of the parent
      children = Category.get_children(parent_id, count_items = True)
    
    if len(children) > 0:
      categories += children
  
    categories[0].parent_flag = True
  
  #Assign selected_flag
  for c in categories:
    if c.id == int(category_id):
      c.selected_flag = True
    else:
      c.selected_flag = False
  
  #Get item or items
  item = None
  items = []
  if item_id == None:
    items = Item.get_by_category(category_id)
  else:
    item = Item.get_by_id(item_id)
    if isinstance(item, Item) and item.category_id != category_id:
      item = None
  
  return render_template('home.html', title = 'Catalog Excercise',\
                         categories = categories,\
                         items = items,\
                         item = item
                        )
  