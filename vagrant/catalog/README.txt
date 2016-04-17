==== Before test web application, you have to do ... ====
1. Open your command prompt, and go to the directory that you could run vagrant box.
2. Run command 'vagrant up' to execute box, and then run command 'vagrant ssh' to login to box.
3. Run command 'cd /vagrant/catalog'.
4. Run command 'python init_db.py' to initialize database entries.
5. Run command 'python app.py' to execute the web server.

==== Before sign in, you could visit ... ====

== Main Page ==
1. Open a web browser (for example, Chrome) and type 'localhost:5000' into the address bar and press the 'Enter' key.
2. Now, you could see the main page of the web application.

== Catagories in Main Page ==
1. On the left side, there are many categories.
2. You could click a category link, to see the result.

== Items in Main Page ==
1. On the right side, there are items belongs to the selected category. If the root category is selected, it will shows all items.

== One Item in Main Page ==
1. Click an item link from the list of items, then it will shows that item's detail information includes image, long text and etc.

== Button 'Create Item' in Main Page ==
1. Click the button, page will be redirected to 'sign in' page.

==== Use t@g.com/pass to sign in for this test ... ====
t@g.com is User ID.
pass is Password.

==== After signed in, you could visit ... ====

== Items in Main Page ==
1. If the item belongs to the user that signed in, it will shows 2 buttons on the right side of each line. Those are 'edit' button, 'delete' button.

== One Item in Main Page ==
1. If the item belongs to the user that signed in, it will shows 2 buttons on the bottom of title. Those are 'edit' button, 'delete' button.

== Button 'Create Item' ==
1. You must NOT choose the root category or category that has sub-category.
2. Write the title and long text, choose a picture if you want, finally you could click the submit button to save it.

== Button 'Edit' ==
1. If you want change something in the item, you could click 'edit' button on the relavent item.
2. On the Edit page, change anything you want, then click 'submit' button to save it.

== Button 'Delete' ==
1. If you want delete an item, just click the 'delete' button to finish it.


==== About 3rd party Authentication ====

== Sign in with Google Account ==
1. You could find 'Sign in from with Google' button on the sign in page.
2. You could use your Google Account to sign in this web site and use your email address as ID.

==== About JSON format data usage ====

== Here we support JSON format api ==
1. One is /category/<int:cid>/item.json
If you go to this url(for example, http://localhost:5000/category/1/item.json), then you could get a list of items that belongs to the category 1.
2. The other one is /item/<int:item_id>.json
If you go to this url(for example, http://localhost:5000/item/1.json), then you could get an item information, that item's id is 1.