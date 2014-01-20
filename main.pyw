from Tkinter import *
import tkMessageBox
import csv
import shutil, time
import os, os.path

inventory = {}
product_list = []
current_product = None
current_flavor = None
quantity_available = None



class MainWindow(Frame):

    def __init__(self, master):
        #base product box; Shows the 'base' name i.e. Ensure, Glucerna, etc.
        self.productBox = Listbox(master)
        self.productBox.grid(row=1, column=1, rowspan=7, columnspan=2, sticky=N+S+E+W, padx=4)
        self.productBox.bind('<<ListboxSelect>>',self.get_flavors)

        #attribute product box; Shows the 'attribute' name such as flavor or calorie density
        self.attributeBox = Listbox(master)
        self.attributeBox.grid(row=1, rowspan=2, column=4, columnspan=2, sticky=N+E+W+S)
        self.attributeBox.bind('<<ListboxSelect>>',self.get_quantity)

        #label to display 'x in stock' where x is the selected item
        self.stockLabel = Label(text="None")
        self.stockLabel.grid(row=3, column=4, columnspan=2, sticky=N+E+W+S)

        #spinbox to designate how many items to add/remove from selected product
        self.modifyQuantitySpin = Spinbox(master, wrap=True, values=[x for x in range(1000)])
        self.modifyQuantitySpin.grid(row=4, column=4, sticky=N+S+E+W, columnspan=2)

        #add and subtract stock buttons
        self.addButton = Button(text="+", command=self.add_quantity).grid(row=5, column=4, sticky=N+E+W+S)
        self.subtractButton = Button(text="-", command=self.subtract_quantity).grid(row=5, column=5, sticky=N+E+W+S)

        #button to add an item to the list that opens a new window
        self.additemButton = Button(text="Add Product", command=self.openAddWindow).grid(row=6, column=4, columnspan=2, sticky=N+S+E+W)

        #delete button to remove the selected item from the list
        self.deleteButton = Button(text="Delete", command=self.remove_product).grid(row=7, column=4, sticky=N+S+W+E)

        #save button to write the current data to a csv file
        self.saveButton = Button(text="Save", command=self.savedata).grid(row=7, column=5, sticky=N+W+S+E)

        #padding to fill the outside rows/columns while keeping inside gaps tight
        self.padding1 = Label(text="  ").grid(row=0,column=0)
        #self.padding3 = Label(text="MANAGE THAT INVENTORY").grid(row=0, column=1, columnspan=6, sticky=N+S+E+W)
        self.padding2 = Label(text="  ").grid(row=8,column=7)
        #self.padding42 = Label(text="shit yeah.").grid(row=8, column=1, columnspan=6, sticky=N+S+E+W)




    def savedata(self):
        #save data to a csv file
        self.refresh_productBox()
        products = []
        quantities = []
        flavors = []
        for key in inventory:
            if type(inventory[key]) == dict:
                for possible_flavor in inventory[key]:
                    products.append(key)
                    flavors.append(possible_flavor)
                    quantities.append(inventory[key][possible_flavor])
            else:
                products.append(key)
                flavors.append("")
                quantities.append(inventory[key])
        shutil.copy("inv.csv",time.strftime("backup\BAK_%m%d_%H%M%S.csv"))       
        with open('inv.csv', 'w+') as inventory_write:
            writer = csv.writer(inventory_write, dialect='excel')
            count = 0
            for item in products:
               writer.writerow(([item]+[flavors[count]]+[quantities[count]]))
               count += 1

                

    def refresh_productBox(self):
        #fills the product box with the products from the dictionary after it's sorted
        base_productList = []
        self.attributeBox.delete(0,END)
        self.productBox.delete(0,END)
        for product in inventory:
            base_productList.append(product)
            
        base_productList.sort()
        
        for item in base_productList:
            self.productBox.insert(END,item)
            if inventory[item] == 0 or inventory[item] == '0':
                self.productBox.itemconfig(END,fg='red')
            




    def get_flavors(self,stuff):
        """
        get the flavors and put them in the attributebox, otherwise indicate there are none and get the quantity
        of the selected product instead
        """
        global current_product
        current_product = str(self.productBox.get(self.productBox.curselection()))
        self.stockLabel.config(text=str(current_product) + " selected")
        self.attributeBox.delete(0,END)
        for product in inventory:
            if current_product == product:
                if type(inventory[product]) == dict:
                    for flavor in inventory[product]:
                        self.attributeBox.insert(END,flavor)
                        if int(inventory[product][flavor]) == 0:
                            self.attributeBox.itemconfig(END,fg='red')
                else:
                    self.attributeBox.insert(END,"No options available.")
                    self.get_quantity()





    def get_quantity(self,stuff=1):
        """
        Compare the selected product to the dictionary of products, if its there then
        change the globals (quantity/product) to the corresponding values and display the quantity. If a
        TclError occurs because the current select is actually a flavor, then search for the right flavor
        within a product's dictionary.
        """
        global current_product, quantity_available, current_flavor

        try:
            for item in inventory:
                if str(self.productBox.get(self.productBox.curselection())) == item:
                    quantity_available, current_product = inventory[item], item
                    self.refresh_quantity()
                    current_flavor = None

        except TclError:
            for flavor in inventory[current_product]:
                if str(self.attributeBox.get(self.attributeBox.curselection())) == flavor:
                    quantity_available = inventory[current_product][flavor]
                    current_flavor = flavor
                    self.refresh_quantity()





    def refresh_quantity(self):
        #refresh the label that holds the quantity with the latest, for changes and new selections
        self.stockLabel.config(text=str(quantity_available)+ " available")
            




    def remove_product(self):
        #method to remove products from the productlist
        try:
            #try to set the current selection to a variable, if it fails that means nothing is selected in this listbox
            product_to_delete = self.productBox.get(self.productBox.curselection())
            #make the user aware that they will delete the product and all of it's flavors, confirm dialogue.
            if tkMessageBox.askokcancel("Remove All","This will remove the base product and all it's flavors. Proceed?"):
                inventory.pop(product_to_delete)
                self.productBox.delete(ANCHOR)
                self.attributeBox.delete(0,END)
        except TclError:
            """
            catch the error if nothing in the ProductBox is selected, then check the attributeBox for selection and
            delete that instead if there is one.
            """
            inventory[current_product].pop(self.attributeBox.get(self.attributeBox.curselection()))
            self.attributeBox.delete(ANCHOR)





    def add_quantity(self):
        """
        gets the number from the spinbox and adds it to the current quantity of the selected product/flavor,
        catches the error if a flavor isn't selected
        """
        global quantity_available
        try:
            spinbox_num = int(self.modifyQuantitySpin.get())
            if current_flavor:
                temp_item = int(inventory[current_product][current_flavor])
                quantity_available = inventory[current_product][current_flavor] = temp_item + spinbox_num
            else:
                quantity_available = inventory[current_product] = int(inventory[current_product]) + spinbox_num
            self.resetSpinbox()
            self.refresh_quantity()
        except TypeError:
            tkMessageBox.showerror("Woops!", "You need to pick a flavor!")
    



        
    def subtract_quantity(self):
        """
        gets the number from the spinbox and subtracts it from the current quantity of the selected product/flavor,
        catches the error if a flavor isn't selected and doesn't allow you to subtract below 0.
        """
        global quantity_available
        try:
            spinbox_num = int(self.modifyQuantitySpin.get())
            if current_flavor:
                temp_item = int(inventory[current_product][current_flavor])
                if self.check_negative_stock(temp_item, spinbox_num):
                    quantity_available = inventory[current_product][current_flavor] = temp_item - spinbox_num
            else:
                temp_item = int(inventory[current_product])
                if self.check_negative_stock(temp_item, spinbox_num):
                    quantity_available = inventory[current_product] = temp_item - spinbox_num
            self.resetSpinbox()
            self.refresh_quantity()
        except TypeError:
            tkMessageBox.showerror("Woops!", "You need to pick a flavor!")






    def resetSpinbox(self):
        #reset the quantity spinbox to 0
        self.modifyQuantitySpin.delete(0,"end")
        self.modifyQuantitySpin.insert(0,0)



    def check_negative_stock(self, current, change):
        #check the subtraction function to make sure we don't get negative stock, return false if its negative
        if (current - change) < 0:
            tkMessageBox.showerror("Woops!", "We don't have that many!")
            return False
        elif (current - change) >= 0:
            return True


    def callback(self):
        #protocol for dealing with a quit. Check if there's more than 20 backups, delete the oldest, then close.
        self.savedata()
        if tkMessageBox.askokcancel("Quit", "Really quit?"):
            while len(os.listdir("backup")) >20:
                files = [os.path.join("backup/", fname) for fname in os.listdir("backup")]
                oldest = min(files, key=os.path.getmtime)
                os.remove(oldest)
            root.destroy()


    def openAddWindow(self):
        #opens a small popup window when the 'add product' button is clicked.
        self.addItemFrame = Toplevel()
        self.addItem = AddItemWindow(self.addItemFrame)
        self.addItemFrame.title("Add a Product")



        
class AddItemWindow(Frame):
    #New window for adding new items to the inventory
    def __init__(self, master):
        
        self.productLabel = Label(master, text="Product:").grid(row=2, column=1, sticky=E)
        self.productEntry = Entry(master)
        self.productEntry.grid(row=2, column=2, sticky=W, columnspan=2)

        self.flavorLabel = Label(master, text="Flavor:").grid(row=3, column=1, sticky=E)
        self.flavorEntry = Entry(master)
        self.flavorEntry.grid(row=3, column=2, columnspan=2, sticky=W)

        self.quantityLabel = Label(master, text="Quantity:").grid(row=4, column=1,sticky=E)
        self.quantitySpin = Spinbox(master, width=18, wrap=True, values=[x for x in range(1000)])
        self.quantitySpin.grid(row=4, column=2, sticky=W, columnspan=2)        
    
        self.addButton = Button(master, text="Add", command=self.product_addition)
        self.addButton.grid(row=6, column=2, sticky=N+S+W+E)
        self.cancelButton = Button(master, text="Cancel", command=master.destroy)
        self.cancelButton.grid(row=6, column=3, sticky=N+S+W+E)

        self.padding1 = Label(master, text=" ").grid(row=0, column=0)
        self.padding2 = Label(master, text=" ").grid(row=7, column=4)



    def product_addition(self):
        """
        Function that handles the gathering of new flavor, product, and quantity to add. It checks to make
        sure proper datatypes are entered and determines if this can be added to the dictionary.
        """
        global new_product, new_flavor, new_quantity
        try:
            new_product = str(self.productEntry.get())
            new_flavor = str(self.flavorEntry.get())
            new_quantity = int(self.quantitySpin.get())
            if new_product.isalnum():
            
                if new_product in inventory and not new_flavor: #If existing product specified and no flavor given...
                    tkMessageBox.showerror("Oops", "Looks like this product exists. Please modify quantity in the main window")


                elif (new_product not in inventory) and new_flavor: #if the product specified does not exist and a flavor was given...
                    inventory[new_product] = {new_flavor: new_quantity}
                    self.productEntry.delete(0,END), self.flavorEntry.delete(0,END), self.quantitySpin.delete(0,END)
                    
    
                elif (new_product in inventory) and type(inventory[new_product]) != dict: #if the product exists but without flavors...
                    tkMessageBox.showerror("Oops!", "That product doesn't support flavors.\
     To add support, please delete the base item and then add it back in with a flavor.")
                    
                elif new_product in inventory and (new_flavor in inventory[new_product]): #If existing product AND flavor
                    tkMessageBox.showerror("Oops", "Looks like this flavor exists. Please modify quantity in the main window")
                    
                elif new_product in inventory and new_flavor: #if the product exists and user gave a new flavor...
                    inventory[new_product][new_flavor] = new_quantity
                    self.productEntry.delete(0,END), self.flavorEntry.delete(0,END), self.quantitySpin.delete(0,END)
                        
                elif not new_flavor and new_product not in inventory: #if no flavor given, and its a new product...
                    inventory[new_product] = new_quantity
                    self.productEntry.delete(0,END), self.flavorEntry.delete(0,END), self.quantitySpin.delete(0,END)

                MainWindow.refresh_productBox(inventory_Buddy)

        except ValueError:
            tkMessageBox.showerror("Oops!", "Please check your quantity, it should be a number!")

            
             



                                    
if __name__ == "__main__":
    #start this shit up
    root = Tk()
    root.title("Inventory Buddy v0.1b")
    inventory_Buddy = MainWindow(root)


    with open('inv.csv', 'r+') as inventory_file:
    #Open up the inventory csv file and read that shit
    #{Product1:Quantity1, Product2:{FlavorA:QuantityA}}
        reader = csv.reader(inventory_file)

        for row in reader:
            #product name in the first column, flavor (if applicable) in the second
            base_product = str(row[0])
            flavor = str(row[1])

            if base_product:
                #if there's a flavor and the product isn't already in the dictionary, add the product, then the flavor
                if flavor and not (base_product in inventory):
                    inventory[base_product] = {flavor:row[2]}
                #if there's a flavor and the product IS in the dictionary, add this flavor to the product's dictionary
                elif flavor and inventory[base_product]:
                    inventory[base_product][flavor] = row[2]
                #if there's no flavor, just add the product to the dictionary
                else: inventory[base_product] = row[2]
        #fill them listboxes
        inventory_Buddy.refresh_productBox()
        
    root.protocol("WM_DELETE_WINDOW", inventory_Buddy.callback)   
    root.mainloop()






