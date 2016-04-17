# coding=utf-8
from flask import Blueprint, render_template, request, \
                  redirect, url_for, json, flash, current_app
from database_setup import Item
from user import login_required, redirect_common, get_user_id_from_session
import os

blueprint = Blueprint('item', __name__)

@blueprint.route('/category/<int:cid>/item.json')
@blueprint.route('/item/<int:item_id>.json')
def item_json(cid = None, item_id = None):
  if item_id != None:
    item = Item.get_by_id(item_id)
    json_response = json.jsonify(Item=item.serialize)
  elif cid != None:
    items = Item.get_by_category(cid)
    json_response = json.jsonify(Items = [i.serialize for i in items])
  return json_response

@blueprint.route('/item/<int:item_id>')
def item_display(item_id = None):
  return render_template('item.html', title = 'Display item',\
                         item = Item.get_by_id(item_id),\
                         display = True
                        )

@blueprint.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
#@login_required()
def item_edit(item_id = None):
  item = Item.get_by_id(item_id)
  
  if request.method == 'POST':
    item.name = request.form['item-name']
    item.longtext = request.form["item-longtext"]
    file = request.files["item-image"]
    item.image = file.stream.getvalue()

    #file.save(os.path.join(current_app.root_path, file.filename))
    
    item.update()
    item.commit()
    return redirect(url_for('item.item_display', item_id = item_id))
  
  return render_template('item.html', title = 'Edit item',\
                         item = item,\
                         display = False
                        )
  
@blueprint.route('/item/<int:item_id>/delete')
@login_required()
def item_delete(item_id = None):
  Item.delete_by_id(item_id)
  return redirect_common(url_for('category.home'))

@blueprint.route('/category/<int:cid>/item/create', methods=['GET', 'POST'])
@login_required()
def item_create(cid = None):
  if request.method == 'POST':
    print 'To process item creation.'
    item = Item()
    item.category_id = request.form['item-category_id']
    item.name = request.form['item-name']
    item.longtext = request.form["item-longtext"]
    file = request.files["item-image"]
    item.image = file.stream.getvalue()
    item.user_id = get_user_id_from_session()
    result = item.add()
    if result[1] == 'error':
      flash(result[2], result[1])
    else:
      item.commit()
      return redirect(url_for('item.item_display', item_id = item.id))
  else:
    if cid == None:
      flash('Please select a category.', 'error')
      return redirect_common(url_for('category.home'))

  return render_template('item.html', title = 'Create item',\
                         item = Item(category_id = cid),\
                         display = False
                        )
  