import datetime
import decimal
import tkinter as tk
import tkinter.font
import tkinter.messagebox
from tkinter import ttk

import Generate
import MySQL

MySQL.createDatabase()
MySQL.createTables()


class ScrollableFrame(ttk.Frame):
    """ Frames that are objects of ScrollableFrame are able to be scrolled.

    When placing objects in a scrollable frame, use frameName.scrollable_frame """

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        scrollbary = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbarx = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame.bind('<Configure>', self.set_scrollregion)

        scrollbary.pack(side="right", fill="y")
        scrollbarx.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.config(yscrollcommand=scrollbary.set)
        self.canvas.config(xscrollcommand=scrollbarx.set)

        self.canvas.bind('<Configure>', self.FrameWidth)

        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

    def FrameWidth(self, event):
        canvas_width = event.width + self.canvas_frame
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


# ***** Page Frames *****
root = tk.Tk()
root.title("OpenPay")
root.geometry("1280x720")
root.configure(background="gray")
homeFrame = ScrollableFrame(root)
employeesFrame = ScrollableFrame(root)
hiddenEmployeesFrame = ScrollableFrame(root)
addEditEmployeeFrame = ScrollableFrame(root)
paymentsFrame = ScrollableFrame(root)
hiddenPaymentsFrame = ScrollableFrame(root)
addEditPaymentFrame = ScrollableFrame(root)
quarterlyFrame = ScrollableFrame(root)
positionsFrame = ScrollableFrame(root)
hiddenPositionsFrame = ScrollableFrame(root)
addEditPositionFrame = ScrollableFrame(root)

# ***** Global Variables *****

selectedEmployee = tk.IntVar()
selectedPayment = tk.IntVar()
selectedPosition = tk.IntVar()
timeOfDay = tk.IntVar()


def openHome():
    """ Opens the home page after refreshing all tables """

    refreshEmployeeTables()
    refreshPaymentTables()
    refreshPositionTables()
    homeFrame.lift()


def openEmployees():
    """  Builds the employee tables and opens the employees page """

    refreshEmployeeTables()
    buildEmployeesTable(50)
    employeesFrame.lift()


def openNewEmployee():
    """ Opens New Employee Page """

    for widget in addEditEmployeeFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditEmployee(0)
    addEditEmployeeFrame.lift()


def openEditEmployee():
    """ Opens Edit employee Page """

    for widget in addEditEmployeeFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditEmployee(selectedEmployee.get())
    addEditEmployeeFrame.lift()


def openHiddenEmployees():
    """ Opens the hidden employees list """

    buildHiddenEmployeesTable(50)
    hiddenEmployeesFrame.lift()


def hideEmployee():
    """ If there is an employee selected, gives a warning box. If the user selects yes, hides the selected Employee. """

    if selectedEmployee.get() == 0:
        tkinter.messagebox.showinfo("Hide Employee", "You must select an employee first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to hide " + MySQL.getEmployeeFN_LN(selectedEmployee.get()) + "?"
        answer = tkinter.messagebox.askquestion("Hide Employee Confirmation", message)
        if answer == 'yes':
            MySQL.hideEmployee(selectedEmployee.get())
            refreshEmployeeTables()
        MySQL.closeConnection()


def revealEmployee():
    """ Reveals the selected employee if user responds "Yes" to warning. """

    if selectedEmployee.get() == 0:
        tkinter.messagebox.showinfo("Reveal Employee", "You must select an employee first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to reveal " + MySQL.getEmployeeFN_LN(selectedEmployee.get()) + "?"
        answer = tkinter.messagebox.askquestion("Reveal Employee Confirmation", message)
        if answer == 'yes':
            MySQL.revealEmployee(selectedEmployee.get())
            refreshEmployeeTables()
        MySQL.closeConnection()


def refreshEmployeeTables():
    """ Refreshes all employee tables.

    Call this function after making changes to any employee. """

    for widget in homeEmployeesPreview.winfo_children():
        widget.destroy()
    for widget in employeesTable.winfo_children():
        widget.destroy()
    for widget in hiddenEmployeesTable.winfo_children():
        widget.destroy()
    homeBuildEmployeesPreview(5)
    buildEmployeesTable(50)
    buildHiddenEmployeesTable(50)


def deleteEmployee():
    """
    If there is an employee selected, gives a warning popup. If the user selects yes, deletes the selected employee.
    """

    if selectedEmployee.get() == 0:
        tkinter.messagebox.showinfo("Delete Employee", "You must select an employee first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to delete " + MySQL.getEmployeeFN_LN(selectedEmployee.get()) + \
                  "? This will also delete every payment associated with " + \
                  MySQL.getEmployeeFN_LN(selectedEmployee.get()) + \
                  ". It is recommended that you hide employees rather than deleting them."
        answer = tkinter.messagebox.askquestion("Delete Employee Confirmation", message)
        if answer == 'yes':
            MySQL.deleteEmployee(selectedEmployee.get())
            refreshEmployeeTables()
        MySQL.closeConnection()


def openPayments():
    """ opens the Payments Page"""

    buildPaymentsTable(100)
    paymentsFrame.lift()
    return


def openHiddenPayments():
    """ Opens the list of Hidden Payments """

    buildHiddenPaymentsTable(100)
    hiddenPaymentsFrame.lift()
    return


def openEmployeePayments():
    """ Opens a table of payments for a the selected employee """

    buildEmployeePaymentsTable(100, selectedEmployee.get())
    paymentsFrame.lift()


def openSimilarPayments():
    """ Opens a table of payments for all payments with the same employeeID as the selected payment """

    MySQL.establishConnection()
    try:
        buildEmployeePaymentsTable(MySQL.getPaymentValue(selectedPayment.get(), "EmployeeID"))
    except:
        print(MySQL.getPaymentValue(selectedPayment.get(), "EmployeeID"))
        print("error")
        return
    paymentsFrame.lift()


def openNewPayment():
    """ Opens the new payment page """

    for widget in addEditPaymentFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditPayment(0)
    addEditPaymentFrame.lift()


def openEditPayment():
    """ Opens the edit payment page """

    for widget in addEditPaymentFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditPayment(selectedPayment.get())
    addEditPaymentFrame.lift()


def openPayEmployee():
    """ Opens a new payment for the selected employee """

    for widget in addEditPaymentFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditPayment(0, employeeID=selectedEmployee.get())
    addEditPaymentFrame.lift()


def openQuarterly():
    """ Opens the Quarterly Reports Page """

    buildQuarterlyTables()
    quarterlyFrame.lift()


def hidePayment():
    """ If there is a payment selected, gives a warning box. If the user selects yes, hides the selectedPayment. """

    if selectedPayment.get() == 0:
        tkinter.messagebox.showinfo("Hide Payment", "You must select a payment first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to hide the selected payment?"
        answer = tkinter.messagebox.askquestion("Hide Payment Confirmation", message)
        if answer == 'yes':
            MySQL.hidePayment(selectedPayment.get())
            refreshPaymentTables()
        MySQL.closeConnection()
    refreshPaymentTables()


def generatePaystub():
    """ Generates a paystub for the selected payment """

    Generate.generatePaystub(selectedPayment.get())
    return


def revealPayment():
    """ If there is a hidden payment selected, gives a warning box.

    If the user selects yes, reveals the selected payment. """

    if selectedPayment.get() == 0:
        tkinter.messagebox.showinfo("Reveal Payment", "You must select a payment first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to reveal the selected payment?"
        answer = tkinter.messagebox.askquestion("Reveal Payment Confirmation", message)
        if answer == 'yes':
            MySQL.revealPayment(selectedPayment.get())
            refreshPaymentTables()
        MySQL.closeConnection()


def deletePayment():
    """ If there is a payment selected, gives a warning popup. If the user selects yes, deletes the selected
    employee. """

    if selectedPayment.get() == 0:
        tkinter.messagebox.showinfo("Delete Payment", "You must select a payment first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to delete this Payment?"
        answer = tkinter.messagebox.askquestion("Delete Payment Confirmation", message)
        if answer == 'yes':
            MySQL.deletePayment(selectedPayment.get())
            refreshPaymentTables()
        MySQL.closeConnection()
    refreshPaymentTables()


def refreshPaymentTables():
    """ Refreshes the homePaymentPreview table. Call this function after making changes to the employees table. """

    for widget in homePaymentsPreview.winfo_children():
        widget.destroy()
    for widget in paymentsTable.winfo_children():
        widget.destroy()
    for widget in hiddenPaymentsTable.winfo_children():
        widget.destroy()
    homeBuildPaymentsPreview(5)
    buildPaymentsTable(50)
    buildHiddenPaymentsTable(50)


def openPositions():
    """ Opens the positions page """

    for widget in positionsTable.winfo_children():
        widget.destroy()
    buildPositionsTable(50)
    positionsFrame.lift()


def openNewPosition():
    """ Opens the New Position Page """

    for widget in addEditPositionFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditPosition(0)
    addEditPositionFrame.lift()


def openEditPosition():
    """ Opens the Edit Position Page """

    for widget in addEditPositionFrame.scrollable_frame.winfo_children():
        widget.destroy()
    buildAddEditPosition(selectedPosition.get())
    addEditPositionFrame.lift()


def hidePosition():
    """ If there is a position selected, gives a warning box. If the user selects yes, hides the selectedPosition. """

    if selectedPosition.get() == 0:
        tkinter.messagebox.showinfo("Hide Position", "You must select a position first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to hide " + MySQL.getPositionValue(selectedPosition.get(), "PositionName") + \
                  "?"
        answer = tkinter.messagebox.askquestion("Hide Position Confirmation", message)
        if answer == 'yes':
            MySQL.hidePosition(selectedPosition.get())
            refreshPositionTables()
        MySQL.closeConnection()


def openHiddenPositions():
    """ Opens the Hidden Positions Page """

    buildHiddenPositionsTable(50)
    hiddenPositionsFrame.lift()


def deletePosition():
    """ If there is a position selected, gives a warning popup. If the user selects yes, deletes the selected
    position. """

    if selectedPosition.get() == 0:
        tkinter.messagebox.showinfo("Delete Position", "You must select a position first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to delete " + MySQL.getPositionValue(selectedPosition.get(), "PositionName") + \
                  "?"
        answer = tkinter.messagebox.askquestion("Delete Position Confirmation", message)
        if answer == 'yes':
            MySQL.deletePosition(selectedPosition.get())
            refreshPositionTables()
        MySQL.closeConnection()


def revealPosition():
    """ If there is a position selected, gives a warning box. If the user selects yes, reveals the selectedPosition. """

    if selectedPosition.get() == 0:
        tkinter.messagebox.showinfo("Reveal Position", "You must select a position first.")
    else:
        MySQL.establishConnection()
        message = "Are you sure you want to reveal " + MySQL.getPositionValue(selectedPosition.get(), "PositionName") + \
                  "?"
        answer = tkinter.messagebox.askquestion("Reveal Position Confirmation", message)
        if answer == 'yes':
            MySQL.revealPosition(selectedPosition.get())
            refreshPositionTables()
        MySQL.closeConnection()


def refreshPositionTables():
    """ Refreshes the homePositionsPreview table. Call this function after making changes to the positions table. """

    for widget in homePositionsPreview.winfo_children():
        widget.destroy()
    for widget in positionsTable.winfo_children():
        widget.destroy()
    for widget in hiddenPositionsTable.winfo_children():
        widget.destroy()
    homeBuildPositionsPreview(5)
    buildPositionsTable(50)
    buildHiddenPositionsTable(50)


# ***** Toolbars *****

# *** Home Toolbar ***
homeToolbar = tk.Frame(homeFrame.scrollable_frame, bg="gray", pady=5)

viewEmployeesButt = tk.Button(homeToolbar, text="View Employees", command=openEmployees)
viewEmployeesButt.pack(side="left", padx=5, pady=5)
viewPaymentsButt = tk.Button(homeToolbar, text="View Payments", command=openPayments)
viewPaymentsButt.pack(side="left", padx=5, pady=5)
viewPositionsButt = tk.Button(homeToolbar, text="View Positions", command=openPositions)
viewPositionsButt.pack(side="left", padx=5, pady=5)

homeToolbar.pack(side="top", fill="x", expand="true")

# *** Employees Toolbar ***

employeesToolbar = tk.Frame(employeesFrame.scrollable_frame, bg="gray", pady=5)

newEmployeeButt = tk.Button(employeesToolbar, text="New Employee", command=openNewEmployee)
newEmployeeButt.pack(side="left", padx=5, pady=5)
editEmployeeButt = tk.Button(employeesToolbar, text="Edit Employee", command=openEditEmployee)
editEmployeeButt.pack(side="left", padx=5, pady=5)
payEmployeeButt = tk.Button(employeesToolbar, text="Pay Employee", command=openPayEmployee)
payEmployeeButt.pack(side="left", padx=5, pady=5)
viewEmployeePaymentsButt = tk.Button(employeesToolbar, text="View This Employee's Payments",
                                     command=openEmployeePayments)
viewEmployeePaymentsButt.pack(side="left", padx=5, pady=5)
hideEmployeeButt = tk.Button(employeesToolbar, text="Hide Employee", command=hideEmployee)
hideEmployeeButt.pack(side="left", padx=5, pady=5)
viewHiddenEmployeeButt = tk.Button(employeesToolbar, text="View Hidden Employees", command=openHiddenEmployees)
viewHiddenEmployeeButt.pack(side="left", padx=5, pady=5)
deleteEmployeeButt = tk.Button(employeesToolbar, text="Delete Employee", command=deleteEmployee, fg="red")
deleteEmployeeButt.pack(side="left", padx=5, pady=5)

employeesToolbar.pack(side="top", fill="x")

# *** Hidden Employees Toolbar ***

hiddenEmployeesToolbar = tk.Frame(hiddenEmployeesFrame.scrollable_frame, bg="gray", pady=5)

viewAllEmployeesButt = tk.Button(hiddenEmployeesToolbar, text="View All Employees", command=openEmployees)
viewAllEmployeesButt.pack(side="left", padx=5, pady=5)
revealEmployeeButt = tk.Button(hiddenEmployeesToolbar, text="Reveal Employee", command=revealEmployee)
revealEmployeeButt.pack(side="left", padx=5, pady=5)
deleteEmployeeButt = tk.Button(hiddenEmployeesToolbar, text="Delete Employee", command=deleteEmployee, fg="red")
deleteEmployeeButt.pack(side="left", padx=5, pady=5)

hiddenEmployeesToolbar.pack(side="top", fill="x")

# *** Payments Toolbar ***

paymentsToolbar = tk.Frame(paymentsFrame.scrollable_frame, bg="gray", pady=5)

newPaymentButt = tk.Button(paymentsToolbar, text="New Payment", command=openNewPayment)
newPaymentButt.pack(side="left", padx=5, pady=5)
editPaymentButt = tk.Button(paymentsToolbar, text="Edit Payment", command=openEditPayment)
editPaymentButt.pack(side="left", padx=5, pady=5)
generatePaystubButt = tk.Button(paymentsToolbar, text="Generate Paystub",
                                command=generatePaystub)
generatePaystubButt.pack(side="left", padx=5, pady=5)
viewEmployeePaymentsButt = tk.Button(paymentsToolbar, text="View This Employee's Payments",
                                     command=openSimilarPayments)
viewEmployeePaymentsButt.pack(side="left", padx=5, pady=5)
viewAllPaymentsButt = tk.Button(paymentsToolbar, text="View All Payments", command=openPayments)
viewAllPaymentsButt.pack(side="left", padx=5, pady=5)
hidePaymentButt = tk.Button(paymentsToolbar, text="Hide Payment", command=hidePayment)
hidePaymentButt.pack(side="left", padx=5, pady=5)
viewHiddenPaymentsButt = tk.Button(paymentsToolbar, text="View Hidden Payments", command=openHiddenPayments)
viewHiddenPaymentsButt.pack(side="left", padx=5, pady=5)
deletePaymentButt = tk.Button(paymentsToolbar, text="Delete Payment", command=deletePayment, fg="red")
deletePaymentButt.pack(side="left", padx=5, pady=5)
viewQuarterlyButt = tk.Button(paymentsToolbar, text="View Quarterly Info", command=openQuarterly)
viewQuarterlyButt.pack(side="left", padx=5, pady=5)

paymentsToolbar.pack(side="top", fill="x")

# *** Quarterly Payments Toolbar ***

quarterlyToolbar = tk.Frame(quarterlyFrame.scrollable_frame, bg="gray", pady=5)

viewAllPaymentsButt = tk.Button(quarterlyToolbar, text="View Payments", command=openPayments)
viewAllPaymentsButt.pack(side="left", padx=5, pady=5)

quarterlyToolbar.pack(side="top", fill="x")

# *** Hidden Payments Toolbar ***

hiddenPaymentsToolbar = tk.Frame(hiddenPaymentsFrame.scrollable_frame, bg="gray", pady=5)

viewAllPaymentsButt = tk.Button(hiddenPaymentsToolbar, text="View All Payments", command=openPayments)
viewAllPaymentsButt.pack(side="left", padx=5, pady=5)
revealPaymentButt = tk.Button(hiddenPaymentsToolbar, text="Reveal Payment", command=revealPayment)
revealPaymentButt.pack(side="left", padx=5, pady=5)
deletePaymentButt = tk.Button(hiddenPaymentsToolbar, text="Delete Payment", command=deletePayment, fg="red")
deletePaymentButt.pack(side="left", padx=5, pady=5)

hiddenPaymentsToolbar.pack(side="top", fill="x")

# *** Positions Toolbar ***
positionsToolbar = tk.Frame(positionsFrame.scrollable_frame, bg="gray", pady=5)

newPositionButt = tk.Button(positionsToolbar, text="New Position", command=openNewPosition)
newPositionButt.pack(side="left", padx=5, pady=5)
editPositionButt = tk.Button(positionsToolbar, text="Edit Position", command=openEditPosition)
editPositionButt.pack(side="left", padx=5, pady=5)
hidePositionButt = tk.Button(positionsToolbar, text="Hide Position", command=hidePosition)
hidePositionButt.pack(side="left", padx=5, pady=5)
viewHiddenPositionsButt = tk.Button(positionsToolbar, text="View Hidden Positions", command=openHiddenPositions)
viewHiddenPositionsButt.pack(side="left", padx=5, pady=5)
deletePositionButt = tk.Button(positionsToolbar, text="Delete Position", command=deletePosition, fg="red")
deletePositionButt.pack(side="left", padx=5, pady=5)

positionsToolbar.pack(side="top", fill="x")

# *** Hidden Positions Toolbar ***
hiddenPositionsToolbar = tk.Frame(hiddenPositionsFrame.scrollable_frame, bg="gray", pady=5)

viewAllPositionsButt = tk.Button(hiddenPositionsToolbar, text="View All Positions", command=openPositions)
viewAllPositionsButt.pack(side="left", padx=5, pady=5)
revealPositionButt = tk.Button(hiddenPositionsToolbar, text="Reveal Position", command=revealPosition)
revealPositionButt.pack(side="left", padx=5, pady=5)
deletePositionButt = tk.Button(hiddenPositionsToolbar, text="Delete Position", command=deletePosition, fg="red")
deletePositionButt.pack(side="left", padx=5, pady=5)

hiddenPositionsToolbar.pack(side="top", fill="x")

# ***** Tables *****

employeesTable = tk.Frame(employeesFrame.scrollable_frame)
hiddenEmployeesTable = tk.Frame(hiddenEmployeesFrame.scrollable_frame)

paymentsTable = tk.Frame(paymentsFrame.scrollable_frame)
hiddenPaymentsTable = tk.Frame(hiddenPaymentsFrame.scrollable_frame)
monthlyTotalTable = tk.Frame(quarterlyFrame.scrollable_frame)
quarterlyTotalTable = tk.Frame(quarterlyFrame.scrollable_frame)

positionsTable = tk.Frame(positionsFrame.scrollable_frame)
hiddenPositionsTable = tk.Frame(hiddenPositionsFrame.scrollable_frame)

#     **********

#      ****************

# ***** Main Menu *****

mainMenu = tk.Menu(root)
root.config(menu=mainMenu)

mainMenu.add_command(label="Home", command=openHome)

employeesMenu = tk.Menu(mainMenu)
mainMenu.add_cascade(label="Employees", menu=employeesMenu)
employeesMenu.add_command(label="View Employees", command=openEmployees)
employeesMenu.add_command(label="New Employee", command=openNewEmployee)
employeesMenu.add_command(label="View Hidden Employees", command=openHiddenEmployees)

paymentsMenu = tk.Menu(mainMenu)
mainMenu.add_cascade(label="Payments", menu=paymentsMenu)
paymentsMenu.add_command(label="View Payments", command=openPayments)
paymentsMenu.add_command(label="New Payment", command=openNewPayment)
paymentsMenu.add_command(label="View Hidden Payments", command=openHiddenPayments)

positionsMenu = tk.Menu(mainMenu)
mainMenu.add_cascade(label="Positions", menu=positionsMenu)
positionsMenu.add_command(label="View Positions", command=openPositions)
positionsMenu.add_command(label="New Position", command=openNewPosition)
positionsMenu.add_command(label="Open Hidden Positions", command=openHiddenPositions)


# ***** Pages *****

# *** Home Page ***


def homeBuildEmployeesPreview(rowCount):
    """ Creates a quick view of the employees table for the homepage, using the [rowCount] most recent employees """

    global selectedEmployee

    # sets the height and width of the table
    height = rowCount + 1
    width = 7

    # used to label the first row of the table
    headers = ["Select", "Name", "Salary", "Hourly Rate", "Housing Allowance", "HSA", "Primary Email Address"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(homeEmployeesPreview, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["employeeName", "EmployeeSalary", "EmployeeHourlyRate", "EmployeeHousingAllowance", "EmployeeHSA",
                   "EmployeePrimaryEmail"]
    mostRecentEmployeeID = MySQL.getMax("Employees", "EmployeeID")
    for i in range(1, height):  # Rows
        columnNamesIndex = 0
        # ensures there is still an employee to list and that it is not hidden
        if not (mostRecentEmployeeID == 0) and not \
                (MySQL.getEmployeeValue(mostRecentEmployeeID, "EmployeeIsHidden") == 1):
            homeEmployeeSelectButt = tk.Radiobutton(homeEmployeesPreview, value=mostRecentEmployeeID,
                                                    variable=selectedEmployee, relief="solid", anchor="center")
            homeEmployeeSelectButt.grid(row=i, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "employeeName":
                    value = MySQL.getEmployeeFN_LN(mostRecentEmployeeID)
                elif columnNames[columnNamesIndex] == "EmployeeGrossPay":
                    value = MySQL.getEmployeeValue(mostRecentEmployeeID, 'EmployeeSalary') + \
                            MySQL.getEmployeeValue(mostRecentEmployeeID, 'EmployeeHousingAllowance')
                else:
                    value = MySQL.getEmployeeValue(mostRecentEmployeeID, columnNames[columnNamesIndex])
                if isinstance(value, decimal.Decimal):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(homeEmployeesPreview, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(homeEmployeesPreview, text=' ', relief='solid', padx=5)
                b.grid(row=i, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentEmployeeID to get the next most recent employee
        mostRecentEmployeeID = MySQL.getNextHighest("Employees", "EmployeeID", mostRecentEmployeeID)
    MySQL.closeConnection()

    homeEmployeesPreview.pack(pady=(0, 20))


def homeBuildPaymentsPreview(rowCount):
    """ Creates a quick view of the Payments table, using the [rowCount] most recent payments """

    global selectedPayment

    # sets the height and width of the table
    height = rowCount + 1
    width = 13

    # used to label the first row of the table
    headers = ["Select", "Date", "Name", "Hours", "Gross Pay", "Housing", "HSA", "Social-Security", "Medicare",
               "Self-Employment", "Federal", "Net Pay", "FICA"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(homePaymentsPreview, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PaymentDate", "EmployeeName", "PaymentHours", "PaymentGrossPay", "PaymentHousing", "PaymentHSA",
                   "PaymentSSTax", "PaymentMedicareTax", "PaymentSETax", "PaymentFedWH", "PaymentNetPay", "FICA"]
    PaymentIDs = MySQL.getPaymentIDsByDate()
    rowIndex = 0
    for paymentID in PaymentIDs:
        mostRecentPaymentID = str(paymentID).split("(", 1)[1].split(",", 1)[0]
        columnNamesIndex = 0
        # ensures there is still a payment to list and that it is not hidden
        if not (mostRecentPaymentID == 0) and not (
                MySQL.getPaymentValue(mostRecentPaymentID, "PaymentIsHidden") == 1):
            homePaymentSelectButt = tk.Radiobutton(homePaymentsPreview, value=mostRecentPaymentID,
                                                   variable=selectedPayment, relief="solid", anchor="center")
            homePaymentSelectButt.grid(row=rowIndex, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "EmployeeName":
                    value = MySQL.getEmployeeFN_LN(MySQL.getPaymentValue(mostRecentPaymentID, "EmployeeID"))
                # FICA is SS + Medicare
                elif columnNames[columnNamesIndex] == "FICA":
                    value = (MySQL.getPaymentValue(mostRecentPaymentID, "PaymentSSTax") + \
                             MySQL.getPaymentValue(mostRecentPaymentID, "PaymentMedicareTax")) * 2
                # Format Dates to be readable for Americans
                elif columnNames[columnNamesIndex] == "PaymentDate":
                    value = MySQL.formatDate(MySQL.getPaymentValue(mostRecentPaymentID, "PaymentDate"))
                else:
                    value = MySQL.getPaymentValue(mostRecentPaymentID, columnNames[columnNamesIndex])
                # Add dollar signs to dollar amounts only
                if (isinstance(value, decimal.Decimal)) and not (columnNames[columnNamesIndex] == "PaymentHours"):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(homePaymentsPreview, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(homePaymentsPreview, text=' ', relief='solid', padx=5)
                b.grid(row=rowIndex, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentPaymentID to get the next most recent employee
        rowIndex += 1
        if rowIndex >= 5:
            break
    MySQL.closeConnection()

    homePaymentsPreview.pack(pady=(0, 20))


def homeBuildPositionsPreview(rowCount):
    """ Creates a quick view of the Positions table, using the [rowCount] most recent positions """

    global selectedPosition

    # sets the height and width of the table
    height = rowCount + 1
    width = 8

    # used to label the first row of the table
    headers = ["Select", "Name", "Salary", "Hourly Rate", "Housing Allowance", "HSA", "Self-Employment WH",
               "Federal WH"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(homePositionsPreview, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PositionName", "PositionSalary", "PositionHourlyRate", "PositionHousingAllowance", "PositionHSA",
                   "PositionSEWH", "PositionFedWH"]
    mostRecentPositionID = MySQL.getMax("Positions", "PositionID")

    for i in range(1, height):  # Rows
        # Tracks the index of columnNames to pull for each cell
        columnNamesIndex = 0

        # ensures there is still an employee to list and that it is not hidden
        if not (mostRecentPositionID == 0) and not (
                MySQL.getPositionValue(mostRecentPositionID, "PositionIsHidden") == 1):
            homePositionSelectButt = tk.Radiobutton(homePositionsPreview, value=mostRecentPositionID,
                                                    variable=selectedPosition, relief="solid", anchor="center")
            homePositionSelectButt.grid(row=i, column=0, sticky="ew")

            for j in range(1, width):  # Columns

                # Gets the value of each cell
                value = MySQL.getPositionValue(mostRecentPositionID, columnNames[columnNamesIndex])

                # If its a decimal value, it needs a dollar sign
                if isinstance(value, decimal.Decimal):
                    value = "$" + str(value)

                # ensures there is a value in the specified cell, then places it in the table
                if value is not None:
                    b = tk.Label(homePositionsPreview, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(homePositionsPreview, text=' ', relief='solid', padx=5)
                b.grid(row=i, column=j, sticky="nesw")

                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1

        # Updates the mostRecentPositionID to get the next most recent employee
        mostRecentPositionID = MySQL.getNextHighest("Positions", "PositionID", mostRecentPositionID)

    MySQL.closeConnection()

    homePositionsPreview.pack(pady=(0, 20))


homeEmployeesLabel = tk.Label(homeFrame.scrollable_frame, text="Recent Employees", pady=20, padx=20)
homeEmployeesPreview = tk.Frame(homeFrame.scrollable_frame)
homeViewEmployeesButt = tk.Button(homeFrame.scrollable_frame, text="View Employees", justify="center",
                                  command=openEmployees)

homePaymentsLabel = tk.Label(homeFrame.scrollable_frame, text="Recent Payments", pady=20, padx=20, underline=1)
homePaymentsPreview = tk.Frame(homeFrame.scrollable_frame)
homeViewPaymentsButt = tk.Button(homeFrame.scrollable_frame, text="View Payments", justify="center",
                                 command=openPayments)

homePositionsLabel = tk.Label(homeFrame.scrollable_frame, text="Recent Positions", pady=20, padx=20, underline=1)
homePositionsPreview = tk.Frame(homeFrame.scrollable_frame)
homeViewPositionsButt = tk.Button(homeFrame.scrollable_frame, text="View Positions", justify="center",
                                  command=openPositions)

f1 = tkinter.font.Font()
f1.configure(underline=True)
f1.configure(size=20)
f2 = tkinter.font.Font()
f2.configure(size=15)
homeEmployeesLabel.configure(font=f1)
homePaymentsLabel.configure(font=f1)
homePositionsLabel.configure(font=f1)


#    ******

# *** Employees Pages ***


def buildEmployeesTable(rowCount):
    """ Creates the employees table, using up to [rowCount] employees (usually 50) """

    global selectedEmployee

    # sets the height and width of the table
    height = rowCount + 1
    width = 13

    # used to label the first row of the table
    headers = ["Select", "Name", "Position", "Gross Pay", "Salary", "Hourly Rate", "Housing Allowance", "HSA",
               "Federal WH", "Self-Employment WH", "Pay Interval", "Primary Email Address", "Self-Employed"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(employeesTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["employeeName", "EmployeePosition", "EmployeeGrossPay", "EmployeeSalary", "EmployeeHourlyRate",
                   "EmployeeHousingAllowance", "EmployeeHSA", "EmployeeFedWH", "EmployeeSEWH", "EmployeePayInterval",
                   "EmployeePrimaryEmail", "EmployeeIsSE"]
    mostRecentEmployeeID = MySQL.getMax("Employees", "EmployeeID")
    for i in range(1, height):  # Rows
        columnNamesIndex = 0
        # ensures there is still an employee to list and that it is not hidden
        if not (mostRecentEmployeeID == 0) and not \
                (MySQL.getEmployeeValue(mostRecentEmployeeID, "EmployeeIsHidden") == 1):
            employeeSelectButt = tk.Radiobutton(employeesTable, value=mostRecentEmployeeID,
                                                variable=selectedEmployee, relief="solid", anchor="center")
            employeeSelectButt.grid(row=i, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "employeeName":
                    value = MySQL.getEmployeeFN_LN(mostRecentEmployeeID)
                elif columnNames[columnNamesIndex] == "EmployeeGrossPay":
                    value = MySQL.getEmployeeValue(mostRecentEmployeeID, 'EmployeeSalary') + \
                            MySQL.getEmployeeValue(mostRecentEmployeeID, 'EmployeeHousingAllowance')
                elif columnNames[columnNamesIndex] == "EmployeePosition":
                    if MySQL.getEmployeeValue(mostRecentEmployeeID, "PositionID") is not None:
                        value = MySQL.getPositionValue(MySQL.getEmployeeValue(mostRecentEmployeeID, "PositionID"),
                                                       "PositionName")
                    else:
                        value = ""
                elif columnNames[columnNamesIndex] == "EmployeeIsSE":
                    if MySQL.getEmployeeValue(mostRecentEmployeeID, columnNames[columnNamesIndex]) == 0:
                        value = "No"
                    else:
                        value = "Yes"
                else:
                    value = MySQL.getEmployeeValue(mostRecentEmployeeID, columnNames[columnNamesIndex])
                if isinstance(value, decimal.Decimal):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(employeesTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(employeesTable, text=' ', relief='solid', padx=5)
                b.grid(row=i, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentEmployeeID to get the next most recent employee
        mostRecentEmployeeID = MySQL.getNextHighest("Employees", "EmployeeID", mostRecentEmployeeID)
    MySQL.closeConnection()

    employeesTable.pack(pady=(0, 20))


def buildHiddenEmployeesTable(rowCount):
    """ Creates the Hidden Employees table, using up to [rowCount] employees (usually 50) """

    global selectedEmployee

    # sets the height and width of the table
    height = rowCount + 1
    width = 13

    # used to label the first row of the table
    headers = ["Select", "Name", "Position", "Gross Pay", "Salary" "Hourly Rate", "Housing Allowance", "HSA",
               "Federal WH",
               "Self-Employment WH", "Pay Interval", "Primary Email Address", "Self-Employed"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(hiddenEmployeesTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["employeeName", "EmployeePosition", "EmployeeGrossPay", "EmployeeSalary", "EmployeeHourlyRate",
                   "EmployeeHousingAllowance", "EmployeeHSA", "EmployeeFedWH", "EmployeeSEWH", "EmployeePayInterval",
                   "EmployeePrimaryEmail", "EmployeeIsSE"]
    mostRecentEmployeeID = MySQL.getMax("Employees", "EmployeeID")
    for i in range(1, height):  # Rows
        columnNamesIndex = 0
        # ensures there is still an employee to list and that it is not hidden
        if not (mostRecentEmployeeID == 0) and \
                (MySQL.getEmployeeValue(mostRecentEmployeeID, "EmployeeIsHidden") == 1):
            employeeSelectButt = tk.Radiobutton(hiddenEmployeesTable, value=mostRecentEmployeeID,
                                                variable=selectedEmployee, relief="solid", anchor="center")
            employeeSelectButt.grid(row=i, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "employeeName":
                    value = MySQL.getEmployeeFN_LN(mostRecentEmployeeID)
                elif columnNames[columnNamesIndex] == "EmployeePosition":
                    if MySQL.getEmployeeValue(mostRecentEmployeeID, "PositionID") is not None:
                        value = MySQL.getPositionValue(MySQL.getEmployeeValue(mostRecentEmployeeID, "PositionID"),
                                                       "PositionName")
                    else:
                        value = ""
                elif columnNames[columnNamesIndex] == "EmployeeGrossPay":
                    value = MySQL.getEmployeeValue(mostRecentEmployeeID, 'EmployeeSalary') + \
                            MySQL.getEmployeeValue(mostRecentEmployeeID, 'EmployeeHousingAllowance')
                elif columnNames[columnNamesIndex] == "EmployeeIsSE":
                    if MySQL.getEmployeeValue(mostRecentEmployeeID, columnNames[columnNamesIndex]) == 0:
                        value = "No"
                    else:
                        value = "Yes"
                else:
                    value = MySQL.getEmployeeValue(mostRecentEmployeeID, columnNames[columnNamesIndex])
                if isinstance(value, decimal.Decimal):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(hiddenEmployeesTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(hiddenEmployeesTable, text=' ', relief='solid', padx=5)
                b.grid(row=i, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentEmployeeID to get the next most recent employee
        mostRecentEmployeeID = MySQL.getNextHighest("Employees", "EmployeeID", mostRecentEmployeeID)
    MySQL.closeConnection()

    hiddenEmployeesTable.pack(pady=(0, 20))


def buildAddEditEmployee(employeeID):
    """ Builds the New Employee Page, which doubles as the Edit Employee Page if the employeeID == 0 """

    MySQL.establishConnection()

    def fillPositionInfo(self):
        # After a position is selected, autofills financial info from Postiions Table

        MySQL.establishConnection()

        Position = UserEmployeeValues[21].get()

        if Position == '':
            PositionID = 0
        else:
            PositionID = Position.split('(ID=', 1)[1].split(')')[0]

        PositionColumns = ['PositionSalary', 'PositionHourlyRate', 'PositionHousingAllowance', 'PositionHSA',
                           'PositionFedWH', 'PositionSEWH', 'PositionIsSE', 'PositionPayInterval']
        PositionIndex = 0

        for EmployeeIndex in range(22, 30):
            if PositionID == 0:
                if PositionColumns[PositionIndex] == 'PositionIsSE':
                    value = 0
                else:
                    value = ''
            else:
                value = MySQL.getPositionValue(PositionID, PositionColumns[PositionIndex])
            if value is not None:
                UserEmployeeValues[EmployeeIndex].set(value)
            PositionIndex += 1

    def printValues():
        for valueIndex in range(len(UserEmployeeValues)):
            valueIndexstr = str(valueIndex)
            print(EmployeeColumns[valueIndex] + ": " + UserEmployeeValues[
                valueIndex].get() + " (Index=" + valueIndexstr + ")")

    # PrintInfoButton = tk.Button(addEditEmployeeFrame.scrollable_frame, text="Print Values", command=printValues)
    # PrintInfoButton.grid(row=0, column=3)

    def submitEmployee():
        # Creates a new employee or edits the current employee

        # Converts all values to usable format and stores them in EmployeeValues[]
        EmployeeValues = []
        for i in range(5):
            if UserEmployeeValues[i].get() == '':
                EmployeeValues.append('NULL')
            else:
                EmployeeValues.append(UserEmployeeValues[i].get())
        for i in range(5, 7):
            if UserEmployeeValues[i].get() == '':
                EmployeeValues.append('NULL')
            else:
                EmployeeValues.append(UserEmployeeValues[i].get()[:1])
        if UserEmployeeValues[7].get() == 'MM-DD-YYYY':
            EmployeeValues.append('NULL')
        # Case 1: MM-DD-YYYY or MM/DD/YYYY
        elif (UserEmployeeValues[7].get()[2] == '-') and (UserEmployeeValues[7].get()[5] == '-') \
                or (UserEmployeeValues[7].get()[2] == '/') and (UserEmployeeValues[7].get()[5] == '/'):
            EmployeeValues.append(
                UserEmployeeValues[7].get()[6:10] + UserEmployeeValues[7].get()[:2] + UserEmployeeValues[7].get()[3:5])
        # Case 2: M-DD-YYYY or M/DD/YYYY
        elif (UserEmployeeValues[7].get()[1] == '-') and (UserEmployeeValues[7].get()[4] == '-') \
                or (UserEmployeeValues[7].get()[1] == '/') and (UserEmployeeValues[7].get()[4] == '/'):
            EmployeeValues.append(
                UserEmployeeValues[7].get()[5:9] + '0' + UserEmployeeValues[7].get()[0] + UserEmployeeValues[7].get()[
                                                                                          2:4])
        # Case 3: MM-D-YYYY or MM/D/YYYY
        elif (UserEmployeeValues[7].get()[2] == '-') and (UserEmployeeValues[7].get()[4] == '-') \
                or (UserEmployeeValues[7].get()[2] == '/') and (UserEmployeeValues[7].get()[4] == '/'):
            EmployeeValues.append(
                UserEmployeeValues[7].get()[5:9] + UserEmployeeValues[7].get()[:2] + '0' + UserEmployeeValues[7].get()[
                    3])
        # Case 4: M-D-YYYY or M/D/YYYY
        elif (UserEmployeeValues[7].get()[1] == '-') and (UserEmployeeValues[7].get()[3] == '-') \
                or (UserEmployeeValues[7].get()[1] == '/') and (UserEmployeeValues[7].get()[3] == '/'):
            EmployeeValues.append(
                UserEmployeeValues[7].get()[4:8] + '0' + UserEmployeeValues[7].get()[0] + '0' +
                UserEmployeeValues[7].get()[2])
        for i in range(8, 21):
            if UserEmployeeValues[i].get() == '':
                EmployeeValues.append('NULL')
            else:
                EmployeeValues.append(UserEmployeeValues[i].get())
        if UserEmployeeValues[21].get() == '':
            EmployeeValues.append('NULL')
        else:
            EmployeeValues.append(UserEmployeeValues[21].get().split('(ID=', 1)[1].split(')')[0])
        for i in range(22, 28):
            if UserEmployeeValues[i].get() == '':
                EmployeeValues.append(0)
            else:
                EmployeeValues.append(decimal.Decimal(UserEmployeeValues[i].get()))
        EmployeeValues.append(int(UserEmployeeValues[28].get()))
        if UserEmployeeValues[29].get() == '':
            EmployeeValues.append('NULL')
        else:
            EmployeeValues.append(UserEmployeeValues[29].get())

        # If employeeID == 0, create a new employee
        if employeeID == 0:
            """for i in range(len(EmployeeValues)):
                print(EmployeeColumns[i] + ': ' + str(EmployeeValues[i]))"""
            MySQL.addEmployee(EmployeePrefix=EmployeeValues[0], EmployeeFN=EmployeeValues[1],
                              EmployeeMN=EmployeeValues[2], EmployeeLN=EmployeeValues[3],
                              EmployeeSuffix=EmployeeValues[4], EmployeeGender=EmployeeValues[5],
                              EmployeeMaritalStatus=EmployeeValues[6], EmployeeBirthdate=EmployeeValues[7],
                              EmployeeStreetNum=EmployeeValues[8], EmployeeStreetName=EmployeeValues[9],
                              EmployeeCity=EmployeeValues[10], EmployeeState=EmployeeValues[11],
                              EmployeeZIP=EmployeeValues[12], EmployeeAptBuilding=EmployeeValues[13],
                              EmployeeAptRoom=EmployeeValues[14], EmployeePOBox=EmployeeValues[15],
                              EmployeePrimaryEmail=EmployeeValues[16], EmployeeSecondaryEmail=EmployeeValues[17],
                              EmployeeHomeNum=EmployeeValues[18], EmployeeCellNum=EmployeeValues[19],
                              EmployeeWorkNum=EmployeeValues[20], PositionID=EmployeeValues[21],
                              EmployeeSalary=EmployeeValues[22], EmployeeHourlyRate=EmployeeValues[23],
                              EmployeeHousingAllowance=EmployeeValues[24], EmployeeHSA=EmployeeValues[25],
                              EmployeeFedWH=EmployeeValues[26], EmployeeSEWH=EmployeeValues[27],
                              EmployeeIsSE=EmployeeValues[28], EmployeePayInterval=EmployeeValues[29])

        # If employeeID != 0, edit the existing employee
        else:
            for i in range(0, 7):
                if EmployeeValues[i] is not None:
                    EmployeeValues[i] = MySQL.addQuote(EmployeeValues[i])
            for i in range(8, 21):
                if EmployeeValues[i] is not None:
                    EmployeeValues[i] = MySQL.addQuote(EmployeeValues[i])
            if EmployeeValues[29] is not None:
                EmployeeValues[29] = MySQL.addQuote(EmployeeValues[29])
            for i in range(len(EmployeeColumns)):
                if EmployeeValues[i] is not None:
                    MySQL.editTable('Employees', employeeID, EmployeeColumns[i], str(EmployeeValues[i]))

        refreshEmployeeTables()
        openEmployees()

    # Used to track the order and name of each column in the table
    EmployeeColumns = ["EmployeePrefix", "EmployeeFN", "EmployeeMN", "EmployeeLN", "EmployeeSuffix", "EmployeeGender",
                       "EmployeeMaritalStatus", "EmployeeBirthdate", "EmployeeStreetNum", "EmployeeStreetName",
                       "EmployeeCity", "EmployeeState", "EmployeeZIP", "EmployeeAptBuilding",
                       "EmployeeAptRoom", "EmployeePOBox", "EmployeePrimaryEmail", "EmployeeSecondaryEmail",
                       "EmployeeHomeNum", "EmployeeCellNum", "EmployeeWorkNum", "PositionID", "EmployeeSalary",
                       "EmployeeHourlyRate", "EmployeeHousingAllowance", "EmployeeHSA", "EmployeeFedWH", "EmployeeSEWH",
                       "EmployeeIsSE", "EmployeePayInterval"]

    # Used to store the value of each column in the table. follows the order from above
    UserEmployeeValues = []

    # Used to store all of the labels
    Labels = []

    # Used to store the text for each label
    LabelText = ["Prefix", "First Name*", "Middle Name", "Last Name*", "Suffix", "Gender", "Marital Status", "Birthday",
                 "Street Number", "Street Name", "City", "State", "ZIP Code", "Apartment Building", "Apartment Room",
                 "PO Box", "Primary Email", "Secondary Email", "Home Number", "Cell Number", "Work Number", "Position",
                 "Salary", "Hourly Rate", "Housing Allowance", "HSA", "Federal Withholding", "Self-Employment Withholding",
                 "Self-Employed*", "Pay Interval"]

    # Used to store all of the entries
    Entries = []
    EntriesIndex = 0

    # Used to store all of the dropdown selections
    Dropdowns = []
    DropdownsIndex = 0

    # Used to store the desired size of each entry
    Sizes = [5, 15, 15, 15, 5, 13, 5, 20, 15, 3, 10, 15, 5, 5, 25, 25, 15, 15, 15, 15, 8, 8, 8, 8, 8, 8, 3, 9]
    SizeIndex = 0

    # Check if Creating new Employee or editing existing Employee
    if employeeID == 0:
        # Autofill values with blanks or data format
        for index in range(len(EmployeeColumns)):
            UserEmployeeValues.append(tk.StringVar())

            if EmployeeColumns[index] == 'EmployeeGender':
                UserEmployeeValues[index].set("      ")
            elif EmployeeColumns[index] == 'EmployeeMaritalStatus':
                UserEmployeeValues[index].set("      ")
            elif EmployeeColumns[index] == 'EmployeeBirthdate':
                UserEmployeeValues[index].set("MM-DD-YYYY")
            elif EmployeeColumns[index] == 'EmployeeIsSE':
                UserEmployeeValues[index].set(0)
            elif EmployeeColumns[index] == 'EmployeePayInterval':
                UserEmployeeValues[index].set("Monthly")
            else:
                UserEmployeeValues[index].set("")

    else:
        # Autofill values with existing data after converting it to more readable format for the user
        for index in range(len(EmployeeColumns)):
            UserEmployeeValues.append(tk.StringVar())
            if EmployeeColumns[index] == 'EmployeeGender':
                if MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) == 'M':
                    value = 'Male'
                elif MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) == 'F':
                    value = 'Female'
                elif MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) == 'O':
                    value = 'Other'
                else:
                    value = ''
            elif EmployeeColumns[index] == 'EmployeeMaritalStatus':
                if MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) == 'M':
                    value = 'Married'
                elif MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) == 'S':
                    value = 'Single'
                else:
                    value = ''
            elif EmployeeColumns[index] == 'EmployeeBirthdate':
                if MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) is not None:
                    value = str(MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]))[5:7] + '-' + \
                            str(MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]))[8:10] + '-' + \
                            str(MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]))[:4]
                else:
                    value = 'MM-DD-YYYY'
            elif EmployeeColumns[index] == 'PositionID':
                if MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]) is not None:
                    value = MySQL \
                                .getPositionValue(MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]),
                                                  'PositionName') + ' (ID=' \
                            + str(MySQL.getEmployeeValue(employeeID, EmployeeColumns[index])) + ')'
                else:
                    value = ''
            else:
                value = str(MySQL.getEmployeeValue(employeeID, EmployeeColumns[index]))
            if value != 'None':
                UserEmployeeValues[index].set(value)
            else:
                UserEmployeeValues[index].set("")

    PersonalInfoLabel = tk.Label(addEditEmployeeFrame.scrollable_frame, text="Personal Info", font=f1) \
        .grid(pady=15, row=0, column=0, columnspan=2, sticky="nsew")

    rowIndex = 1
    columnIndex = 0

    for EmployeeColumnsIndex in range(len(EmployeeColumns)):

        if EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeStreetNum':
            rowIndex += 2
            columnIndex = 0
        elif EmployeeColumns[EmployeeColumnsIndex] == 'PositionID':
            rowIndex += 2
            columnIndex = 0
            FinancialInfoLabel = tk.Label(addEditEmployeeFrame.scrollable_frame, text="Financial Info", font=f1) \
                .grid(pady=15, row=rowIndex, column=columnIndex, columnspan=2, sticky="nsew")
            rowIndex += 1

        Labels.append(tk.Label(addEditEmployeeFrame.scrollable_frame, text=LabelText[EmployeeColumnsIndex])
                      .grid(pady=(15, 5), padx=5, row=rowIndex, column=columnIndex))
        rowIndex += 1

        if EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeGender':
            Genders = ["Male", "Female", "Other"]
            Dropdowns.append(
                tk.OptionMenu(addEditEmployeeFrame.scrollable_frame, UserEmployeeValues[EmployeeColumnsIndex],
                              UserEmployeeValues[EmployeeColumnsIndex].get(), *Genders))
            Dropdowns[DropdownsIndex].grid(padx=30, row=rowIndex, column=columnIndex, sticky="ew")
            DropdownsIndex += 1
        elif EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeMaritalStatus':
            Dropdowns.append(
                tk.OptionMenu(addEditEmployeeFrame.scrollable_frame, UserEmployeeValues[EmployeeColumnsIndex],
                              UserEmployeeValues[EmployeeColumnsIndex].get(), 'Married', 'Single'))
            Dropdowns[DropdownsIndex].grid(padx=30, row=rowIndex, column=columnIndex, sticky="ew")
            DropdownsIndex += 1
        elif EmployeeColumns[EmployeeColumnsIndex] == 'PositionID':
            Positions = []
            mostRecentPositionID = MySQL.getMax('Positions', 'PositionID')
            while mostRecentPositionID != 0:
                positionName = MySQL.getPositionValue(mostRecentPositionID, 'PositionName')
                mostRecentPositionIDStr = str(mostRecentPositionID)
                Positions.append(positionName + ' (ID=' +
                                 mostRecentPositionIDStr + ')')
                mostRecentPositionID = MySQL.getNextHighest('Positions', 'PositionID', mostRecentPositionID)
            Dropdowns.append(
                tk.OptionMenu(addEditEmployeeFrame.scrollable_frame, UserEmployeeValues[EmployeeColumnsIndex],
                              UserEmployeeValues[EmployeeColumnsIndex].get(), *Positions, command=fillPositionInfo))
            Dropdowns[DropdownsIndex].grid(padx=5, row=rowIndex, column=columnIndex, sticky="ew")
            DropdownsIndex += 1
        elif EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeIsSE':
            SEButton = tk.Checkbutton(addEditEmployeeFrame.scrollable_frame,
                                      variable=UserEmployeeValues[EmployeeColumnsIndex], anchor="center")
            SEButton.grid(padx=5, row=rowIndex, column=columnIndex, sticky="ew")
        elif EmployeeColumns[EmployeeColumnsIndex] == 'EmployeePayInterval':
            PayrollIntervals = ['Monthly', 'SemiMonthly', 'BiWeekly', 'Weekly']
            Dropdowns.append(
                tk.OptionMenu(addEditEmployeeFrame.scrollable_frame, UserEmployeeValues[EmployeeColumnsIndex],
                              UserEmployeeValues[EmployeeColumnsIndex].get(), *PayrollIntervals))
            Dropdowns[DropdownsIndex].grid(padx=30, row=rowIndex, column=columnIndex, sticky="ew")
            DropdownsIndex += 1
        else:
            if (EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeSalary') \
                    or (EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeHourlyRate') \
                    or (EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeHousingAllowance') \
                    or (EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeHSA') \
                    or (EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeFedWH') \
                    or (EmployeeColumns[EmployeeColumnsIndex] == 'EmployeeSEWH'):
                container = tk.Frame(addEditEmployeeFrame.scrollable_frame)
                container.grid(padx=5, row=rowIndex, column=columnIndex)
                label = tk.Label(container, text="$").grid(row=0, column=0)
                Entries.append(tk.Entry(container, width=Sizes[SizeIndex],
                                        textvariable=UserEmployeeValues[EmployeeColumnsIndex]))
                Entries[EntriesIndex].grid(row=0, column=1)
            else:
                Entries.append(tk.Entry(addEditEmployeeFrame.scrollable_frame, width=Sizes[SizeIndex],
                                        textvariable=UserEmployeeValues[EmployeeColumnsIndex]))
                Entries[EntriesIndex].grid(padx=5, row=rowIndex, column=columnIndex)
            SizeIndex += 1
            EntriesIndex += 1

        rowIndex -= 1
        columnIndex += 1

        if columnIndex == 5:
            rowIndex += 2
            columnIndex = 0

    rowIndex += 2
    columnIndex = 0

    SubmitInfoButton = tk.Button(addEditEmployeeFrame.scrollable_frame, text="Submit Info", command=submitEmployee,
                                 font=f2)
    SubmitInfoButton.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)

    columnIndex += 1

    CancelButton = tk.Button(addEditEmployeeFrame.scrollable_frame, text="Cancel", command=openEmployees, font=f2)
    CancelButton.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)

    MySQL.closeConnection()


# *** Payments Pages ***


def buildPaymentsTable(rowCount):
    """ Creates the Payments table, using the [rowCount] most recent payments """

    global selectedPayment

    for widget in paymentsTable.winfo_children():
        widget.destroy()

    # sets the height and width of the table
    height = rowCount + 1
    width = 13

    # used to label the first row of the table
    headers = ["Select", "Date", "Name", "Hours", "Gross Pay", "Housing", "HSA", "Social-Security", "Medicare",
               "Self-Employment", "Federal", "Net Pay", "FICA"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(paymentsTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PaymentDate", "EmployeeName", "PaymentHours", "PaymentGrossPay", "PaymentHousing", "PaymentHSA",
                   "PaymentSSTax", "PaymentMedicareTax", "PaymentSETax", "PaymentFedWH", "PaymentNetPay", "FICA"]
    PaymentIDs = MySQL.getPaymentIDsByDate()
    rowIndex = 0
    for paymentID in PaymentIDs:  # Rows
        mostRecentPaymentID = str(paymentID).split("(", 1)[1].split(",", 1)[0]
        columnNamesIndex = 0
        # ensures there is still an employee to list and that it is not hidden
        if not (mostRecentPaymentID == 0) and not (
                MySQL.getPaymentValue(mostRecentPaymentID, "PaymentIsHidden") == 1):
            PaymentSelectButt = tk.Radiobutton(paymentsTable, value=mostRecentPaymentID,
                                               variable=selectedPayment, relief="solid", anchor="center")
            PaymentSelectButt.grid(row=rowIndex, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "EmployeeName":
                    value = MySQL.getEmployeeFN_LN(MySQL.getPaymentValue(mostRecentPaymentID, "EmployeeID"))
                # FICA is SS + Medicare
                elif columnNames[columnNamesIndex] == "FICA":
                    value = (MySQL.getPaymentValue(mostRecentPaymentID, "PaymentSSTax") + \
                             MySQL.getPaymentValue(mostRecentPaymentID, "PaymentMedicareTax")) * 2
                # Format Dates to be readable for Americans
                elif columnNames[columnNamesIndex] == "PaymentDate":
                    value = MySQL.formatDate(MySQL.getPaymentValue(mostRecentPaymentID, "PaymentDate"))
                else:
                    value = MySQL.getPaymentValue(mostRecentPaymentID, columnNames[columnNamesIndex])
                # Add dollar signs to dollar amounts only
                if (isinstance(value, decimal.Decimal)) and not (columnNames[columnNamesIndex] == "PaymentHours"):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(paymentsTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(paymentsTable, text=' ', relief='solid', padx=5)
                b.grid(row=rowIndex, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentPaymentID to get the next most recent employee
        # mostRecentPaymentID = MySQL.getNextHighest("Payments", "PaymentID", mostRecentPaymentID)
        rowIndex += 1
    MySQL.closeConnection()

    paymentsTable.pack(pady=(0, 20))


def buildHiddenPaymentsTable(rowCount):
    """ Creates the Hidden Payments table, using the [rowCount] most recent payments """

    global selectedPayment

    # sets the height and width of the table
    height = rowCount + 1
    width = 13

    # used to label the first row of the table
    headers = ["Select", "Date", "Name", "Hours", "Gross Pay", "Housing", "HSA", "Social-Security", "Medicare",
               "Self-Employment", "Federal", "Net Pay", "FICA"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(hiddenPaymentsTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PaymentDate", "EmployeeName", "PaymentHours", "PaymentGrossPay", "PaymentHousing", "PaymentHSA",
                   "PaymentSSTax", "PaymentMedicareTax", "PaymentSETax", "PaymentFedWH", "PaymentNetPay", "FICA"]
    PaymentIDs = MySQL.getPaymentIDsByDate()
    rowIndex = 0
    for paymentID in PaymentIDs:  # Rows
        mostRecentPaymentID = str(paymentID).split("(", 1)[1].split(",", 1)[0]
        columnNamesIndex = 0
        # ensures there is still a payment to list and that it is not hidden
        if not (mostRecentPaymentID == 0) and (MySQL.getPaymentValue(mostRecentPaymentID, "PaymentIsHidden") == 1):
            PaymentSelectButt = tk.Radiobutton(hiddenPaymentsTable, value=mostRecentPaymentID,
                                               variable=selectedPayment, relief="solid", anchor="center")
            PaymentSelectButt.grid(row=rowIndex, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "EmployeeName":
                    value = MySQL.getEmployeeFN_LN(MySQL.getPaymentValue(mostRecentPaymentID, "EmployeeID"))
                # FICA is SS + Medicare
                elif columnNames[columnNamesIndex] == "FICA":
                    value = (MySQL.getPaymentValue(mostRecentPaymentID, "PaymentSSTax") + \
                             MySQL.getPaymentValue(mostRecentPaymentID, "PaymentMedicareTax")) * 2
                # Format Dates to be readable for Americans
                elif columnNames[columnNamesIndex] == "PaymentDate":
                    value = MySQL.formatDate(MySQL.getPaymentValue(mostRecentPaymentID, "PaymentDate"))
                else:
                    value = MySQL.getPaymentValue(mostRecentPaymentID, columnNames[columnNamesIndex])
                # Add dollar signs to dollar amounts only
                if (isinstance(value, decimal.Decimal)) and not (columnNames[columnNamesIndex] == "PaymentHours"):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(hiddenPaymentsTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(hiddenPaymentsTable, text=' ', relief='solid', padx=5)
                b.grid(row=rowIndex, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentPaymentID to get the next most recent employee
        rowIndex += 1
    MySQL.closeConnection()

    hiddenPaymentsTable.pack(pady=(0, 20))


def buildEmployeePaymentsTable(employeeID):
    """ Creates the Payments table, using the [rowCount] most recent payments """

    global selectedPayment

    for widget in paymentsTable.winfo_children():
        widget.destroy()

    # sets the width of the table
    width = 13

    # used to label the first row of the table
    headers = ["Select", "Date", "Name", "Hours", "Gross Pay", "Housing", "HSA", "Social-Security", "Medicare",
               "Self-Employment", "Federal", "Net Pay", "FICA"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(paymentsTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PaymentDate", "EmployeeName", "PaymentHours", "PaymentGrossPay", "PaymentHousing", "PaymentHSA",
                   "PaymentSSTax", "PaymentMedicareTax", "PaymentSETax", "PaymentFedWH", "PaymentNetPay", "FICA"]
    PaymentIDs = MySQL.getEmployeePaymentIDsByDate(employeeID)
    rowIndex = 0
    for paymentID in PaymentIDs:  # Rows
        mostRecentPaymentID = str(paymentID).split("(", 1)[1].split(",", 1)[0]
        columnNamesIndex = 0
        # ensures there is still an employee to list and that it is not hidden
        if not (mostRecentPaymentID == 0) \
                and not (MySQL.getPaymentValue(mostRecentPaymentID, "PaymentIsHidden") == 1):
            PaymentSelectButt = tk.Radiobutton(paymentsTable, value=mostRecentPaymentID,
                                               variable=selectedPayment, relief="solid", anchor="center")
            PaymentSelectButt.grid(row=rowIndex, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                # If you need the employeeName, Concat the first name to the last name
                if columnNames[columnNamesIndex] == "EmployeeName":
                    value = MySQL.getEmployeeFN_LN(MySQL.getPaymentValue(mostRecentPaymentID, "EmployeeID"))
                # FICA is SS + Medicare
                elif columnNames[columnNamesIndex] == "FICA":
                    value = (MySQL.getPaymentValue(mostRecentPaymentID, "PaymentSSTax") + \
                             MySQL.getPaymentValue(mostRecentPaymentID, "PaymentMedicareTax")) * 2
                # Format Dates to be readable for Americans
                elif columnNames[columnNamesIndex] == "PaymentDate":
                    value = MySQL.formatDate(MySQL.getPaymentValue(mostRecentPaymentID, "PaymentDate"))
                else:
                    value = MySQL.getPaymentValue(mostRecentPaymentID, columnNames[columnNamesIndex])
                # Add dollar signs to dollar amounts only
                if (isinstance(value, decimal.Decimal)) and not (columnNames[columnNamesIndex] == "PaymentHours"):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(paymentsTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(paymentsTable, text=' ', relief='solid', padx=5)
                b.grid(row=rowIndex, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        rowIndex += 1
    MySQL.closeConnection()

    paymentsTable.pack(pady=(0, 20))


def buildAddEditPayment(paymentID, employeeID=0):
    """ Builds the New Payment Page, which doubles as the Edit Payment Page """

    # Used to track whether or not a payment has been submitted
    paymentSubmitted = False

    MySQL.establishConnection()

    global timeOfDay

    def printValues():
        for valueIndex in range(len(UserPaymentValues)):
            valueIndexstr = str(valueIndex)
            print(UserPaymentColumns[valueIndex] + ": " + UserPaymentValues[
                valueIndex].get() + " (Index=" + valueIndexstr + ")")

    def calculatePayroll():
        # After the user selects an employee, autofills all entries.

        MySQL.establishConnection()

        if UserPaymentValues[0].get() != '':
            EmployeeID = UserPaymentValues[0].get().split('(ID=', 1)[1].split(')')[0]
        else:
            return

        UserPaymentValues[1].set('Payroll')

        # Disable unneeded Entry Points
        Entries[5].config(state='normal')
        Entries[6].config(state='normal')
        Entries[7].config(state='disabled')

        # Get Employee Values from Employees Table
        EmployeeSalary = decimal.Decimal(MySQL.getEmployeeValue(EmployeeID, "EmployeeSalary"))
        EmployeeHourlyRate = decimal.Decimal(MySQL.getEmployeeValue(EmployeeID, "EmployeeHourlyRate"))
        EmployeePayInterval = MySQL.getEmployeeValue(EmployeeID, "EmployeePayInterval")
        EmployeePayIntervalStr = str(EmployeePayInterval)  # Must be string for if statements later
        EmployeeHousingAllowance = decimal.Decimal(MySQL.getEmployeeValue(EmployeeID, "EmployeeHousingAllowance"))
        EmployeeHSA = decimal.Decimal(MySQL.getEmployeeValue(EmployeeID, "EmployeeHSA"))
        EmployeeIsSE = MySQL.getEmployeeValue(EmployeeID, "EmployeeIsSE")
        EmployeeFedWH = decimal.Decimal(MySQL.getEmployeeValue(EmployeeID, "EmployeeFedWH"))
        EmployeeSEWH = decimal.Decimal(MySQL.getEmployeeValue(EmployeeID, "EmployeeSEWH"))

        if not UserPaymentValues[4].get() == '':
            PaymentHours = decimal.Decimal(UserPaymentValues[4].get())
        else:
            PaymentHours = 0

        # collection of if statements sets PaymentGrossPay, PaymentHousing, PaymentHSA, and PaymentFedWH
        PaymentGrossPay = 0
        if not (EmployeeHourlyRate == 0) and not (PaymentHours == 0):
            PaymentGrossPay += EmployeeHourlyRate * PaymentHours
        if EmployeePayIntervalStr == "BiWeekly":
            PaymentGrossPay += (EmployeeSalary / 26) + (EmployeeHousingAllowance / 26)
            PaymentHousing = EmployeeHousingAllowance / 26
            PaymentHSA = EmployeeHSA / 26
            PaymentFedWH = EmployeeFedWH / 26
            PaymentSEWH = EmployeeSEWH / 26
        elif (EmployeePayIntervalStr == 'Monthly') or (EmployeePayIntervalStr == 'None'):
            PaymentGrossPay += (EmployeeSalary / 12) + (EmployeeHousingAllowance / 12)
            PaymentHousing = EmployeeHousingAllowance / 12
            PaymentHSA = EmployeeHSA / 12
            PaymentFedWH = EmployeeFedWH / 12
            PaymentSEWH = EmployeeSEWH / 12
        elif EmployeePayIntervalStr == "SemiMonthly":
            PaymentGrossPay += (EmployeeSalary / 24) + (EmployeeHousingAllowance / 24)
            PaymentHousing = EmployeeHousingAllowance / 24
            PaymentHSA = EmployeeHSA / 24
            PaymentFedWH = EmployeeFedWH / 24
            PaymentSEWH = EmployeeSEWH / 24
        elif EmployeePayIntervalStr == "Weekly":
            PaymentGrossPay += (EmployeeSalary / 52) + (EmployeeHousingAllowance / 52)
            PaymentHousing = EmployeeHousingAllowance / 52
            PaymentHSA = EmployeeHSA / 52
            PaymentFedWH = EmployeeFedWH / 52
            PaymentSEWH = EmployeeSEWH / 52
        PaymentSalary = PaymentGrossPay - PaymentHousing

        # If statement determines PaymentSSTax, PaymentMedicareTax, and PaymentSETax
        if EmployeeIsSE == 0:
            PaymentSSTax = (PaymentGrossPay - PaymentHSA) * MySQL.SocialSecurityTaxRate
            PaymentMedicareTax = (PaymentGrossPay - PaymentHSA) * MySQL.MedicareTaxRate
            PaymentSEWH = 0
        else:
            PaymentSSTax = 0
            PaymentMedicareTax = 0

        PaymentNetPay = PaymentGrossPay - PaymentHSA - PaymentSSTax - PaymentMedicareTax - PaymentSEWH - PaymentFedWH

        UserPaymentValues[5].set(round(PaymentSalary, 2))
        UserPaymentValues[6].set(round(PaymentHousing, 2))
        UserPaymentValues[7].set(round(PaymentGrossPay, 2))
        UserPaymentValues[8].set(round(PaymentHSA, 2))
        UserPaymentValues[9].set(round(PaymentSSTax, 2))
        UserPaymentValues[10].set(round(PaymentMedicareTax, 2))
        UserPaymentValues[11].set(round(PaymentSEWH, 2))
        UserPaymentValues[12].set(round(PaymentFedWH, 2))
        UserPaymentValues[13].set(round(PaymentNetPay, 2))

        MySQL.closeConnection()

    def refreshTotals():
        # refreshes Gross Pay, Net Pay,

        if UserPaymentValues[1].get() == 'Payroll':
            if UserPaymentValues[5].get() != '':
                PaymentSalary = decimal.Decimal(UserPaymentValues[5].get())
            else:
                PaymentSalary = 0
            if UserPaymentValues[6].get() != '':
                PaymentHousing = decimal.Decimal(UserPaymentValues[6].get())
            else:
                PaymentHousing = 0
            PaymentGrossPay = PaymentSalary + PaymentHousing
        elif UserPaymentValues[7].get() != '':
            PaymentGrossPay = decimal.Decimal(UserPaymentValues[7].get())
        else:
            PaymentGrossPay = 0

        if UserPaymentValues[8].get() != '':
            PaymentHSA = decimal.Decimal(UserPaymentValues[8].get())
        else:
            PaymentHSA = 0
        if UserPaymentValues[9].get() != '':
            PaymentSSTax = decimal.Decimal(UserPaymentValues[9].get())
        else:
            PaymentSSTax = 0
        if UserPaymentValues[10].get() != '':
            PaymentMedicareTax = decimal.Decimal(UserPaymentValues[10].get())
        else:
            PaymentMedicareTax = 0
        if UserPaymentValues[11].get() != '':
            PaymentSEWH = decimal.Decimal(UserPaymentValues[11].get())
        else:
            PaymentSEWH = 0
        if UserPaymentValues[12].get() != '':
            PaymentFedWH = decimal.Decimal(UserPaymentValues[12].get())
        else:
            PaymentFedWH = 0

        PaymentNetPay = PaymentGrossPay - PaymentHSA - PaymentSSTax - PaymentMedicareTax - PaymentSEWH - PaymentFedWH

        UserPaymentValues[7].set(round(PaymentGrossPay, 2))
        UserPaymentValues[13].set(round(PaymentNetPay, 2))

    def refreshTaxes():
        # refreshes SSWH and MedWH

        MySQL.establishConnection()

        if UserPaymentValues[0].get() != '':
            EmployeeID = UserPaymentValues[0].get().split('(ID=', 1)[1].split(')')[0]
        else:
            return

        EmployeeIsSE = MySQL.getEmployeeValue(EmployeeID, "EmployeeIsSE")

        PaymentGrossPay = decimal.Decimal(UserPaymentValues[7].get())
        if UserPaymentValues[8].get() != '':
            PaymentHSA = decimal.Decimal(UserPaymentValues[8].get())
        else:
            PaymentHSA = 0

        if EmployeeIsSE == 0:
            PaymentSSTax = (PaymentGrossPay - PaymentHSA) * MySQL.SocialSecurityTaxRate
            PaymentMedicareTax = (PaymentGrossPay - PaymentHSA) * MySQL.MedicareTaxRate
        else:
            PaymentSSTax = 0
            PaymentMedicareTax = 0

        UserPaymentValues[9].set(round(PaymentSSTax, 2))
        UserPaymentValues[10].set(round(PaymentMedicareTax, 2))

        MySQL.closeConnection()

    calculatePayrollButton = tk.Button(addEditPaymentFrame.scrollable_frame, text="Calculate Payroll",
                                       command=calculatePayroll)
    calculatePayrollButton.grid(padx=15, row=0, column=3)
    refreshTotalsButton = tk.Button(addEditPaymentFrame.scrollable_frame, text="Refresh Totals",
                                    command=refreshTotals)
    refreshTotalsButton.grid(padx=15, row=0, column=4)
    refreshTaxesButton = tk.Button(addEditPaymentFrame.scrollable_frame, text="Refresh Taxes",
                                   command=refreshTaxes)
    refreshTaxesButton.grid(padx=15, row=0, column=5)

    """PrintInfoButton = tk.Button(addEditPaymentFrame.scrollable_frame, text="Print Values", command=printValues)
    PrintInfoButton.grid(padx=15, row=0, column=6)"""

    def submitPayment():
        # Creates a new payment or edits the current payment
        global paymentSubmitted
        # Converts all values to usable format and stores them in PaymentValues[]
        PaymentValues = []
        if UserPaymentValues[0].get() == '':
            tkinter.messagebox.showinfo("Submit Payment", "You must select an employee first.")
            paymentSubmitted = False
            return
        else:
            PaymentValues.append(UserPaymentValues[0].get().split('(ID=', 1)[1].split(')')[0])
        # Date -  Case 1: MM-DD-YYYY or MM/DD/YYYY
        if (UserPaymentValues[2].get()[2] == '-') and (UserPaymentValues[2].get()[5] == '-') \
                or (UserPaymentValues[2].get()[2] == '/') and (UserPaymentValues[2].get()[5] == '/'):
            PaymentValues.append(
                UserPaymentValues[2].get()[6:10] + UserPaymentValues[2].get()[:2] + UserPaymentValues[2].get()[3:5])
        # Case 2: M-DD-YYYY or M/DD/YYYY
        elif (UserPaymentValues[2].get()[1] == '-') and (UserPaymentValues[2].get()[4] == '-') \
                or (UserPaymentValues[2].get()[1] == '/') and (UserPaymentValues[2].get()[4] == '/'):
            PaymentValues.append(
                UserPaymentValues[2].get()[5:9] + '0' + UserPaymentValues[2].get()[0] + UserPaymentValues[2].get()[
                                                                                        2:4])
        # Case 3: MM-D-YYYY or MM/D/YYYY
        elif (UserPaymentValues[2].get()[2] == '-') and (UserPaymentValues[2].get()[4] == '-') \
                or (UserPaymentValues[2].get()[2] == '/') and (UserPaymentValues[2].get()[4] == '/'):
            PaymentValues.append(
                UserPaymentValues[2].get()[5:9] + UserPaymentValues[2].get()[:2] + '0' + UserPaymentValues[2].get()[3])
        # Case 4: M-D-YYYY or M/D/YYYY
        elif (UserPaymentValues[2].get()[1] == '-') and (UserPaymentValues[2].get()[3] == '-') \
                or (UserPaymentValues[2].get()[1] == '/') and (UserPaymentValues[2].get()[3] == '/'):
            PaymentValues.append(
                UserPaymentValues[2].get()[4:8] + '0' + UserPaymentValues[2].get()[0] + '0' +
                UserPaymentValues[2].get()[2])
        userTime = str(UserPaymentValues[3].get())
        if userTime[1] == ':':
            if timeOfDay.get() == 0:
                time = '0' + userTime[:4] + ':00'
            else:
                hour = int(userTime[0]) + 12
                time = str(hour) + userTime[1:4] + ':00'
        else:
            if timeOfDay.get() == 0:
                if int(userTime[:2]) == 12:
                    time = '00' + userTime[2:5] + ':00'
                else:
                    time = userTime[:5] + ':00'
            else:
                if int(userTime[:2]) == 12:
                    time = userTime[:5] + ':00'
                else:
                    hour = int(userTime[:2]) + 12
                    time = str(hour) + userTime[2:5] + ':00'
        PaymentValues.append(time)
        if UserPaymentValues[4].get() == '':
            PaymentValues.append(0)
        else:
            PaymentValues.append(UserPaymentValues[4].get())
        for i in range(6, 14):
            if UserPaymentValues[i].get() == '':
                PaymentValues.append(0)
            else:
                PaymentValues.append(UserPaymentValues[i].get())

        # If paymentID == 0, create a new payment
        if paymentID == 0:
            MySQL.addPayment(EmployeeID=PaymentValues[0], PaymentDate=PaymentValues[1],
                             PaymentTime=PaymentValues[2], PaymentHours=PaymentValues[3],
                             PaymentHousing=PaymentValues[4], PaymentGrossPay=PaymentValues[5],
                             PaymentHSA=PaymentValues[6], PaymentSSTax=PaymentValues[7],
                             PaymentMedicareTax=PaymentValues[8], PaymentSETax=PaymentValues[9],
                             PaymentFedWH=PaymentValues[10], PaymentNetPay=PaymentValues[11])

        # If paymentID != 0, edit the existing payment
        else:
            PaymentColumns = ["EmployeeID", "PaymentDate", "PaymentTime", "PaymentHours", "PaymentHousing",
                              "PaymentGrossPay", "PaymentHSA", "PaymentSSTax", "PaymentMedicareTax", "PaymentSETax",
                              "PaymentFedWH", "PaymentNetPay"]
            # for some reason, when updating a table's time value it requires quotes, whereas when adding a new entry it
            # does not require quotes.
            PaymentValues[2] = MySQL.addQuote(PaymentValues[2])
            for i in range(len(PaymentValues)):
                if PaymentValues[i] is not None:
                    MySQL.editTable('Payments', paymentID, PaymentColumns[i], str(PaymentValues[i]))
        paymentSubmitted = True

    def submitAndReload():
        global paymentSubmitted
        submitPayment()
        if paymentSubmitted == True:
            refreshPaymentTables()
            openPayments()

    def addAnother():
        submitPayment()
        buildAddEditPayment(0)

    # Used to track the order and name of each column in the table
    UserPaymentColumns = ["EmployeeID", "PaymentType", "PaymentDate", "PaymentTime", "PaymentHours", "PaymentSalary",
                          "PaymentHousing", "PaymentGrossPay", "PaymentHSA", "PaymentSSTax", "PaymentMedicareTax",
                          "PaymentSETax", "PaymentFedWH", "PaymentNetPay"]

    # Used to store the value of each column in the table. follows the order from above
    UserPaymentValues = []

    # Used to store all of the labels, same order as above
    Labels = []

    # Used to store text for each label
    LabelText = ["Employee", "Payment Type*", "Date*", "Time*", "Hours*", "Salary", "Housing Allowance", "Gross Pay*",
                 "HSA",
                 "Social-Security", "Medicare", "Self-Employment WH", "Federal WH", "Net Pay*"]

    # Used to store all entry mechanisms (entries and dropdowns)
    Entries = []

    # Used to store the desired size of each entry mechanism. For Dropdowns, it stores the padx value.
    Sizes = [0, 20, 10, 6, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8]

    # Check if Creating new payment or editing existing payment
    if paymentID == 0:
        # Create New Payment Label
        NewPaymentLabel = tk.Label(addEditPaymentFrame.scrollable_frame, text="New Payment", font=f1, borderwidth=2,
                                   relief="solid") \
            .grid(pady=30, row=0, column=0, columnspan=2, sticky="nsew")
        # Autofill values with default values
        for index in range(len(UserPaymentColumns)):
            UserPaymentValues.append(tk.StringVar())
            if UserPaymentColumns[index] == 'EmployeeID':
                if employeeID == 0:
                    value = ''
                else:
                    employeeName = MySQL.getEmployeeFN_LN(employeeID)
                    value = employeeName + ' (ID=' + str(employeeID) + ')'
            elif UserPaymentColumns[index] == 'PaymentType':
                value = ''
            elif UserPaymentColumns[index] == 'PaymentDate':
                value = str(datetime.datetime.now().today())[5:7] + '-' + \
                        str(datetime.datetime.now().today())[8:10] + '-' + \
                        str(datetime.datetime.now().today())[:4]
            elif UserPaymentColumns[index] == 'PaymentTime':
                currentTime = str(datetime.datetime.now().time())
                if (int(currentTime[:2]) < 12) and (int(currentTime[:2]) >= 1):
                    hour = int(currentTime[:2])
                    timeOfDay.set(0)
                elif int(currentTime[:2]) == 0:
                    hour = 12
                    timeOfDay.set(0)
                elif int(currentTime[:2]) == 12:
                    hour = 12
                    timeOfDay.set(1)
                else:
                    hour = int(currentTime[:2]) - 12
                    timeOfDay.set(1)
                if hour < 10:
                    hourStr = '0' + str(hour)
                else:
                    hourStr = str(hour)
                value = hourStr + currentTime[2:5]
            elif UserPaymentColumns[index] == 'PaymentHours':
                value = 0
            else:
                value = ""
            UserPaymentValues[index].set(value)
    else:
        # Create Edit Payment Label
        EditPaymentLabel = tk.Label(addEditPaymentFrame.scrollable_frame, text="Edit Payment", font=f1, borderwidth=2,
                                    relief="solid") \
            .grid(pady=30, row=0, column=0, columnspan=2, sticky="nsew")
        # Autofill values with data from Payments table
        for index in range(len(UserPaymentColumns)):
            UserPaymentValues.append(tk.StringVar())
            if UserPaymentColumns[index] == 'EmployeeID':
                value = str(MySQL.getEmployeeFN_LN(MySQL.getPaymentValue(paymentID, 'EmployeeID'))) + ' (ID=' \
                        + str(MySQL.getPaymentValue(paymentID, 'EmployeeID')) + ')'
            elif UserPaymentColumns[index] == 'PaymentType':
                value = ''
            elif UserPaymentColumns[index] == 'PaymentDate':
                value = str(MySQL.getPaymentValue(paymentID, UserPaymentColumns[index]))[5:7] + '-' + \
                        str(MySQL.getPaymentValue(paymentID, UserPaymentColumns[index]))[8:10] + '-' + \
                        str(MySQL.getPaymentValue(paymentID, UserPaymentColumns[index]))[:4]
            elif UserPaymentColumns[index] == 'PaymentTime':
                paymentTime = str(MySQL.getPaymentValue(paymentID, UserPaymentColumns[index]))
                if paymentTime[1] == ':':
                    paymentTime = '0' + paymentTime
                if (int(paymentTime[:2]) < 12) and (int(paymentTime[:2]) >= 1):
                    hour = int(paymentTime[:2])
                    timeOfDay.set(0)
                elif int(paymentTime[:2]) == 0:
                    hour = 12
                    timeOfDay.set(0)
                elif int(paymentTime[:2]) == 12:
                    hour = 12
                    timeOfDay.set(1)
                else:
                    hour = int(paymentTime[:2]) - 12
                    timeOfDay.set(1)
                if hour < 10:
                    hourStr = '0' + str(hour)
                else:
                    hourStr = str(hour)
                value = hourStr + paymentTime[2:5]
            elif UserPaymentColumns[index] == 'PaymentSalary':
                value = decimal.Decimal(MySQL.getPaymentValue(paymentID, 'PaymentGrossPay')) - \
                        decimal.Decimal(MySQL.getPaymentValue(paymentID, 'PaymentHousing'))
            else:
                value = str(MySQL.getPaymentValue(paymentID, UserPaymentColumns[index]))
            if value != 'None':
                UserPaymentValues[index].set(value)
            else:
                UserPaymentValues[index].set("")

    rowIndex = 1
    columnIndex = 0

    def selectPaymentType(self):
        if UserPaymentValues[1].get() == 'Payroll':
            Entries[5].config(state='normal')
            Entries[6].config(state='normal')
            Entries[7].config(state='disabled')
        elif UserPaymentValues[1].get() == 'Bonus':
            Entries[5].config(state='disabled')
            Entries[6].config(state='disabled')
            Entries[7].config(state='normal')
            UserPaymentValues[5].set('')
            UserPaymentValues[6].set('')

    # Create Payment Labels and Entries
    for PaymentColumnsIndex in range(len(UserPaymentColumns)):

        # Decide where to put new lines and big labels
        if UserPaymentColumns[PaymentColumnsIndex] == 'PaymentDate':
            rowIndex += 2
            columnIndex = 0
            PaymentInfoLabel = tk.Label(addEditPaymentFrame.scrollable_frame, text="Payment Info", font=f1) \
                .grid(pady=15, row=rowIndex, column=columnIndex, columnspan=2, sticky="nsew")
            rowIndex += 1
        elif UserPaymentColumns[PaymentColumnsIndex] == 'PaymentSalary':
            rowIndex += 2
            columnIndex = 0
            PaymentAmountLabel = tk.Label(addEditPaymentFrame.scrollable_frame, text="Payment Amount", font=f1) \
                .grid(pady=15, row=rowIndex, column=columnIndex, columnspan=2, sticky="nsew")
            rowIndex += 1
        elif UserPaymentColumns[PaymentColumnsIndex] == 'PaymentGrossPay':
            rowIndex += 2
            columnIndex = 0
        elif UserPaymentColumns[PaymentColumnsIndex] == 'PaymentHSA':
            rowIndex += 2
            columnIndex = 0
        elif UserPaymentColumns[PaymentColumnsIndex] == 'PaymentNetPay':
            rowIndex += 2
            columnIndex = 0

        # Append the Label with the text from LabelText[]
        Labels.append(tk.Label(addEditPaymentFrame.scrollable_frame, text=LabelText[PaymentColumnsIndex])
                      .grid(pady=(15, 5), padx=5, row=rowIndex, column=columnIndex))
        # Increment Row Index to place Entry
        rowIndex += 1

        # Decide where there are special cases for entry widgets (tk.OptionMenu instead of tk.Entry)
        if UserPaymentColumns[PaymentColumnsIndex] == 'EmployeeID':
            Employees = []
            mostRecentEmployeeID = MySQL.getMax('Employees', 'EmployeeID')
            while mostRecentEmployeeID != 0:
                employeeName = MySQL.getEmployeeFN_LN(mostRecentEmployeeID)
                mostRecentEmployeeIDStr = str(mostRecentEmployeeID)
                Employees.append(employeeName + ' (ID=' +
                                 mostRecentEmployeeIDStr + ')')
                mostRecentEmployeeID = MySQL.getNextHighest('Employees', 'EmployeeID', mostRecentEmployeeID)
            Entries.append(
                tk.OptionMenu(addEditPaymentFrame.scrollable_frame, UserPaymentValues[PaymentColumnsIndex],
                              UserPaymentValues[PaymentColumnsIndex].get(), *Employees))
            Entries[PaymentColumnsIndex].grid(padx=Sizes[PaymentColumnsIndex], row=rowIndex, column=columnIndex,
                                              sticky="ew")
        elif UserPaymentColumns[PaymentColumnsIndex] == 'PaymentType':
            PaymentTypes = ['Payroll', 'Bonus']
            Entries.append(
                tk.OptionMenu(addEditPaymentFrame.scrollable_frame, UserPaymentValues[PaymentColumnsIndex],
                              UserPaymentValues[PaymentColumnsIndex].get(), *PaymentTypes, command=selectPaymentType))
            Entries[PaymentColumnsIndex].grid(padx=Sizes[PaymentColumnsIndex], row=rowIndex, column=columnIndex,
                                              sticky="ew")
        elif UserPaymentColumns[PaymentColumnsIndex] == 'PaymentTime':
            container = tk.Frame(addEditPaymentFrame.scrollable_frame)
            container.grid(padx=5, row=rowIndex, column=columnIndex)
            AMRadio = tk.Radiobutton(container, value=0, variable=timeOfDay, text="AM", anchor="center")
            AMRadio.grid(padx=2, row=0, column=1)
            PMRadio = tk.Radiobutton(container, value=1, variable=timeOfDay, text="PM", anchor="center")
            PMRadio.grid(padx=2, row=1, column=1)
            Entries.append(tk.Entry(container, width=Sizes[PaymentColumnsIndex],
                                    textvariable=UserPaymentValues[PaymentColumnsIndex]))
            Entries[PaymentColumnsIndex].grid(row=0, column=0, rowspan=2)

        elif (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentSalary') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentHousing') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentGrossPay') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentHSA') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentSSTax') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentMedicareTax') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentSETax') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentFedWH') \
                or (UserPaymentColumns[PaymentColumnsIndex] == 'PaymentNetPay'):
            container = tk.Frame(addEditPaymentFrame.scrollable_frame)
            container.grid(padx=5, row=rowIndex, column=columnIndex)
            label = tk.Label(container, text="$").grid(row=0, column=0)
            Entries.append(tk.Entry(container, width=Sizes[PaymentColumnsIndex],
                                    textvariable=UserPaymentValues[PaymentColumnsIndex]))
            Entries[PaymentColumnsIndex].grid(row=0, column=1)
        else:
            Entries.append(tk.Entry(addEditPaymentFrame.scrollable_frame, width=Sizes[PaymentColumnsIndex],
                                    textvariable=UserPaymentValues[PaymentColumnsIndex]))
            Entries[PaymentColumnsIndex].grid(padx=5, row=rowIndex, column=columnIndex)

        # Go back a row for next label, and up a column for next label/entry
        rowIndex -= 1
        columnIndex += 1

    Entries[5].config(state='disabled')
    Entries[6].config(state='disabled')
    Entries[7].config(state='disabled')
    Entries[13].config(state='disabled')

    # Go up 2 rows and to column 0 for buttons
    rowIndex += 2
    columnIndex = 0

    # Submit Button
    SubmitInfoButton = tk.Button(addEditPaymentFrame.scrollable_frame, text="Submit Info", command=submitAndReload,
                                 font=f2)
    SubmitInfoButton.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)
    columnIndex += 1

    # Add another Button
    addAnotherButt = tk.Button(addEditPaymentFrame.scrollable_frame, text="Submit and Add Another", command=addAnother,
                               font=f2)
    addAnotherButt.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)
    columnIndex += 1

    # Cancel Button
    CancelButton = tk.Button(addEditPaymentFrame.scrollable_frame, text="Cancel", command=openPayments, font=f2)
    CancelButton.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)

    MySQL.closeConnection()


def buildQuarterlyTables():
    """ Builds MonthlyTotalTable and QuarterlyTotalTable and places them in QuarterlyFrame """

    global selectedPayment

    MySQL.establishConnection()

    for widget in monthlyTotalTable.winfo_children():
        widget.destroy()

    for widget in quarterlyTotalTable.winfo_children():
        widget.destroy()

    # ----- Monthly Totals Table -----

    # Creates the top row of headers
    Headers = ['941 Payments', 'SS WH', 'Medicare WH', 'Fed WH', 'SE WH', 'TOTAL']
    for i in range(len(Headers)):
        label = tk.Label(monthlyTotalTable, text=Headers[i], borderwidth=2, relief="solid", padx=15)
        label.grid(row=0, column=i, sticky="nesw")

    # Creates the left columns of Months
    Months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    for i in range(len(Months)):
        label = tk.Label(monthlyTotalTable, text=Months[i], borderwidth=2, relief="solid", padx=15)
        label.grid(row=(i + 1), column=0, sticky="nesw")

    # Used to determine what Column to pull value from
    PaymentColumns = ['PaymentSSTax', 'PaymentMedicareTax', 'PaymentFedWH', 'PaymentSETax']
    # Used to determine what month condition to pass to getMonthlyTotals
    MonthConditions = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    if selectedPayment.get() != 0:
        Year = str(MySQL.getPaymentValue(selectedPayment.get(), 'PaymentDate'))[:4]
    else:
        Year = str(datetime.datetime.now().today())[:4]

    # Calculates values and populates table
    for monthIndex in range(len(Months)):
        # Used to store all totals for each row
        Totals = []
        for columnIndex in range(len(PaymentColumns)):
            if (PaymentColumns[columnIndex] == 'PaymentSSTax') or (PaymentColumns[columnIndex] == 'PaymentMedicareTax'):
                Total = MySQL.getMonthlyTotal(MonthConditions[monthIndex], Year, PaymentColumns[columnIndex]) * 2
            else:
                Total = MySQL.getMonthlyTotal(MonthConditions[monthIndex], Year, PaymentColumns[columnIndex])
            Totals.append(Total)
            cell = tk.Label(monthlyTotalTable, text=str(Totals[columnIndex]), borderwidth=2, relief="solid", padx=15)
            cell.grid(row=(monthIndex + 1), column=(columnIndex + 1), sticky="nesw")
        value = Totals[0] + Totals[1] + Totals[2] + Totals[3]
        cell = tk.Label(monthlyTotalTable, text=str(value), borderwidth=2, relief="solid", padx=15)
        cell.grid(row=(monthIndex + 1), column=5, sticky="nesw")

    monthlyTotalTable.pack(pady=15)

    # ----- Quarterly Total Table -----

    # Creates the top row of headers
    Headers = ["941 Form Info", "Total SS", "Total Medicare", "Total Fed", "FICA Pay", "Total Pay"]
    for i in range(len(Headers)):
        label = tk.Label(quarterlyTotalTable, text=Headers[i], borderwidth=2, relief="solid", padx=15)
        label.grid(row=0, column=i, sticky="nesw")

    # Creates the Quarter Labels on the leftmost column
    Quarters = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']
    for i in range(len(Quarters)):
        label = tk.Label(quarterlyTotalTable, text=Quarters[i], borderwidth=2, relief="solid", padx=15)
        label.grid(row=(i + 1), column=0, sticky="nesw")

    # Total SS Column
    for i in range(1, 5):
        value = MySQL.getQuarterlyTotal(i, Year, 'PaymentSSTax') * 2
        label = tk.Label(quarterlyTotalTable, text=value, borderwidth=2, relief="solid", padx=15)
        label.grid(row=i, column=1, sticky="nesw")

    # Total Medicare Column
    for i in range(1, 5):
        value = MySQL.getQuarterlyTotal(i, Year, 'PaymentMedicareTax') * 2
        label = tk.Label(quarterlyTotalTable, text=value, borderwidth=2, relief="solid", padx=15)
        label.grid(row=i, column=2, sticky="nesw")

    # Total Federal Column
    for i in range(1, 5):
        federal = MySQL.getQuarterlyTotal(i, Year, 'PaymentFedWH')
        se = MySQL.getQuarterlyTotal(i, Year, 'PaymentSETax')
        value = federal + se
        label = tk.Label(quarterlyTotalTable, text=value, borderwidth=2, relief="solid", padx=15)
        label.grid(row=i, column=3, sticky="nesw")

    # Total Pay and FICA Pay Columns
    for i in range(1, 5):
        total = MySQL.getQuarterlyTotal(i, Year, 'PaymentGrossPay')
        label = tk.Label(quarterlyTotalTable, text=total, borderwidth=2, relief="solid", padx=15)
        label.grid(row=i, column=5, sticky="nesw")
        fica = total - MySQL.getSEGrossPay(i, Year)
        label = tk.Label(quarterlyTotalTable, text=fica, borderwidth=2, relief="solid", padx=15)
        label.grid(row=i, column=4, sticky="nesw")

    quarterlyTotalTable.pack(pady=15)

    MySQL.closeConnection()


# *** Positions Pages ***


def buildPositionsTable(rowCount):
    """ Creates the Positions table, using the [rowCount] most recent positions """

    global selectedPosition

    # sets the height and width of the table
    height = rowCount + 1
    width = 9

    # used to label the first row of the table
    headers = ["Select", "Name", "Salary", "Hourly Rate", "Housing Allowance", "HSA", "Self-Employment WH",
               "Federal WH",
               "Self-Employed"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(positionsTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PositionName", "PositionSalary", "PositionHourlyRate", "PositionHousingAllowance", "PositionHSA",
                   "PositionSEWH", "PositionFedWH", "PositionIsSE"]
    mostRecentPositionID = MySQL.getMax("Positions", "PositionID")
    for i in range(1, height):  # Rows
        columnNamesIndex = 0
        # ensures there is still a position to list and that it is not hidden
        if not (mostRecentPositionID == 0) and not (
                MySQL.getPositionValue(mostRecentPositionID, "PositionIsHidden") == 1):
            PositionSelectButt = tk.Radiobutton(positionsTable, value=mostRecentPositionID,
                                                variable=selectedPosition, relief="solid", anchor="center")
            PositionSelectButt.grid(row=i, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                if columnNames[columnNamesIndex] == 'PositionIsSE':
                    if MySQL.getPositionValue(mostRecentPositionID, columnNames[columnNamesIndex]) == 0:
                        value = 'No'
                    else:
                        value = 'Yes'
                else:
                    value = MySQL.getPositionValue(mostRecentPositionID, columnNames[columnNamesIndex])
                if isinstance(value, decimal.Decimal):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(positionsTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(positionsTable, text=' ', relief='solid', padx=5)
                b.grid(row=i, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentPositionID to get the next most recent employee
        mostRecentPositionID = MySQL.getNextHighest("Positions", "PositionID", mostRecentPositionID)
    MySQL.closeConnection()

    positionsTable.pack(pady=(0, 20))


def buildHiddenPositionsTable(rowCount):
    """ Creates the Hidden Positions table, using the [rowCount] most recent positions """

    global selectedPosition

    # sets the height and width of the table
    height = rowCount + 1
    width = 9

    # used to label the first row of the table
    headers = ["Select", "Name", "Salary", "Hourly Rate", "Housing Allowance", "HSA", "Self-Employment WH",
               "Federal WH",
               "Self-Employed"]

    MySQL.establishConnection()

    # Creates a label using each entry in the headers list
    for index in range(len(headers)):
        b = tk.Label(hiddenPositionsTable, text=headers[index], borderwidth=2, relief="solid", padx=5)
        b.grid(row=0, column=index, sticky="nesw")

    # Determines the columns from the table to pull for each grid
    columnNames = ["PositionName", "PositionSalary", "PositionHourlyRate", "PositionHousingAllowance", "PositionHSA",
                   "PositionSEWH", "PositionFedWH", "PositionIsSE"]
    mostRecentPositionID = MySQL.getMax("Positions", "PositionID")
    for i in range(1, height):  # Rows
        columnNamesIndex = 0
        # ensures there is still a position to list and that it is hidden
        if not (mostRecentPositionID == 0) and (
                MySQL.getPositionValue(mostRecentPositionID, "PositionIsHidden") == 1):
            PositionSelectButt = tk.Radiobutton(hiddenPositionsTable, value=mostRecentPositionID,
                                                variable=selectedPosition, relief="solid", anchor="center")
            PositionSelectButt.grid(row=i, column=0, sticky="ew")
            for j in range(1, width):  # Columns
                if columnNames[columnNamesIndex] == 'PositionIsSE':
                    if MySQL.getPositionValue(mostRecentPositionID, columnNames[columnNamesIndex]) == 0:
                        value = 'No'
                    else:
                        value = 'Yes'
                else:
                    value = MySQL.getPositionValue(mostRecentPositionID, columnNames[columnNamesIndex])
                if isinstance(value, decimal.Decimal):
                    value = "$" + str(value)
                # ensures there is a value in the specified cell
                if value is not None:
                    b = tk.Label(hiddenPositionsTable, text=value, relief="solid", padx=5)
                else:
                    b = tk.Label(hiddenPositionsTable, text=' ', relief='solid', padx=5)
                b.grid(row=i, column=j, sticky="nesw")
                # Increments columnNamesIndex to get the next column name
                columnNamesIndex += 1
        # Updates the mostRecentPositionID to get the next most recent employee
        mostRecentPositionID = MySQL.getNextHighest("Positions", "PositionID", mostRecentPositionID)
    MySQL.closeConnection()

    hiddenPositionsTable.pack(pady=(0, 20))


def buildAddEditPosition(positionID):
    """ Builds the AddEditPosition page, which allows the user to add or edit a position """

    MySQL.establishConnection()

    def printValues():
        for valueIndex in range(len(UserPositionValues)):
            valueIndexstr = str(valueIndex)
            print(PositionColumns[valueIndex] + ": " + UserPositionValues[
                valueIndex].get() + " (Index=" + valueIndexstr + ")")

    def submitPosition():
        # Creates a new position or edits the current position
        MySQL.establishConnection()

        # Converts all values to usable format and stores them in PositionValues[]
        PositionValues = []
        if UserPositionValues[0].get() == '':
            PositionValues.append('NULL')
        else:
            PositionValues.append(UserPositionValues[0].get())
        for i in range(1, 7):
            if UserPositionValues[i].get() == '':
                PositionValues.append('NULL')
            else:
                PositionValues.append(decimal.Decimal(UserPositionValues[i].get()))
        PositionValues.append(UserPositionValues[7].get())
        if UserPositionValues[8].get() == '':
            PositionValues.append('NULL')
        else:
            PositionValues.append(UserPositionValues[8].get())

        # If positionID == 0, create a new position
        if positionID == 0:
            MySQL.addPosition(PositionName=PositionValues[0], PositionSalary=PositionValues[1],
                              PositionHourlyRate=PositionValues[2], PositionHousingAllowance=PositionValues[3],
                              PositionHSA=PositionValues[4], PositionFedWH=PositionValues[5],
                              PositionSEWH=PositionValues[6],
                              PositionIsSE=PositionValues[7], PositionPayInterval=PositionValues[8])

        # If positionID != 0, edit the existing position
        else:
            PositionValues[0] = MySQL.addQuote(PositionValues[0])
            PositionValues[8] = MySQL.addQuote(PositionValues[8])
            for i in range(len(PositionColumns)):
                MySQL.editTable('Positions', positionID, PositionColumns[i], str(PositionValues[i]))

        MySQL.closeConnection()
        openPositions()

    # Used to store user entered values
    UserPositionValues = []

    # Used to store all of the labels for the form
    Labels = []

    # USed to reference as the names of all of the columns on the table
    PositionColumns = ["PositionName", "PositionSalary", "PositionHourlyRate", "PositionHousingAllowance",
                       "PositionHSA", "PositionFedWH", "PositionSEWH", "PositionIsSE", "PositionPayInterval"]

    # Used as text for all of the form labels
    LabelText = ["Title*", "Salary", "Hourly Rate", "Housing Allowance", "HSA", "Federal WH", "Self-Employment WH",
                 "Self Employed", "Pay Interval"]

    # Used to store all data entry points
    Entries = []

    # USed to store the sizes for all of the entries
    Sizes = [20, 10, 10, 10, 10, 10, 10, 10, 5]

    # Check if creating new position or editing existing position
    if positionID == 0:
        NewPositionLabel = tk.Label(addEditPositionFrame.scrollable_frame, text="New Position", font=f1, borderwidth=2,
                                    relief="solid") \
            .grid(pady=30, row=0, column=0, columnspan=2, sticky="nsew")
        # Autofill values with blanks or data format
        for i in range(len(PositionColumns)):
            UserPositionValues.append(tk.StringVar())
            if PositionColumns[i] == 'PositionIsSE':
                UserPositionValues[i].set(0)
            elif PositionColumns[i] == 'PositionPayInterval':
                UserPositionValues[i].set('                ')
            else:
                UserPositionValues[i].set('')
    else:
        EditPositionLabel = tk.Label(addEditPositionFrame.scrollable_frame, text="Edit Position", font=f1,
                                     borderwidth=2, relief="solid") \
            .grid(pady=30, row=0, column=0, columnspan=2, sticky="nsew")
        # Autofill values with existing data
        for i in range(len(PositionColumns)):
            UserPositionValues.append(tk.StringVar())
            value = MySQL.getPositionValue(positionID, PositionColumns[i])
            if value is not None:
                UserPositionValues[i].set(value)
            else:
                UserPositionValues[i].set('')

    """printValuesButt = tk.Button(addEditPositionFrame.scrollable_frame, text="Print Values", command=printValues)
    printValuesButt.grid(padx=5, row=0, column=3)"""

    rowIndex = 1
    columnIndex = 0

    for i in range(len(PositionColumns)):

        # Decide where to start a new row
        if (PositionColumns[i] == 'PositionSalary') \
                or (PositionColumns[i] == 'PositionHousingAllowance'):
            rowIndex += 2
            columnIndex = 0

        Labels.append(tk.Label(addEditPositionFrame.scrollable_frame, text=LabelText[i])
                      .grid(pady=(15, 5), padx=5, row=rowIndex, column=columnIndex))
        rowIndex += 1

        if (PositionColumns[i] == 'PositionSalary') \
                or (PositionColumns[i] == 'PositionHourlyRate') \
                or (PositionColumns[i] == 'PositionHousingAllowance') \
                or (PositionColumns[i] == 'PositionHSA') \
                or (PositionColumns[i] == 'PositionFedWH')\
                or (PositionColumns[i] == 'PositionSEWH'):
            container = tk.Frame(addEditPositionFrame.scrollable_frame)
            container.grid(padx=5, row=rowIndex, column=columnIndex)
            label = tk.Label(container, text="$")
            label.grid(row=0, column=0)
            entry = tk.Entry(container, width=Sizes[i], textvariable=UserPositionValues[i])
            entry.grid(row=0, column=1)
        elif PositionColumns[i] == 'PositionIsSE':
            entry = tk.Checkbutton(addEditPositionFrame.scrollable_frame, variable=UserPositionValues[i])
            entry.grid(row=rowIndex, column=columnIndex)
        elif PositionColumns[i] == 'PositionPayInterval':
            PayrollIntervals = ['Monthly', 'SemiMonthly', 'BiWeekly', 'Weekly']
            entry = tk.OptionMenu(addEditPositionFrame.scrollable_frame, UserPositionValues[i],
                                  UserPositionValues[i].get(), *PayrollIntervals)
            entry.grid(padx=Sizes[i], row=rowIndex, column=columnIndex, sticky="ew")
        else:
            entry = tk.Entry(addEditPositionFrame.scrollable_frame, width=Sizes[i], textvariable=UserPositionValues[i])
            entry.grid(padx=5, row=rowIndex, column=columnIndex)
        rowIndex -= 1
        columnIndex += 1

    rowIndex += 2
    columnIndex = 0

    SubmitInfoButton = tk.Button(addEditPositionFrame.scrollable_frame, text="Submit Info", command=submitPosition,
                                 font=f2)
    SubmitInfoButton.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)

    columnIndex += 1

    CancelButton = tk.Button(addEditPositionFrame.scrollable_frame, text="Cancel", command=openPositions, font=f2)
    CancelButton.grid(pady=50, padx=5, row=rowIndex, column=columnIndex)


# ***** On Start *****

# Build home page
homeEmployeesLabel.pack(fill="x")
homeBuildEmployeesPreview(5)
homeViewEmployeesButt.pack()
homePaymentsLabel.pack(fill="x")
homeBuildPaymentsPreview(5)
homeViewPaymentsButt.pack()
homePositionsLabel.pack(fill="x")
homeBuildPositionsPreview(5)
homeViewPositionsButt.pack()

# Place Frames in root
homeFrame.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
employeesFrame.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
hiddenEmployeesFrame.place(in_=root, x=0, relwidth=1, relheight=1)
addEditEmployeeFrame.place(in_=root, x=0, relwidth=1, relheight=1)
paymentsFrame.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
hiddenPaymentsFrame.place(in_=root, x=0, relwidth=1, relheight=1)
quarterlyFrame.place(in_=root, x=0, relwidth=1, relheight=1)
addEditPaymentFrame.place(in_=root, x=0, relwidth=1, relheight=1)
positionsFrame.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
hiddenPositionsFrame.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
addEditPositionFrame.place(in_=root, x=0, y=0, relwidth=1, relheight=1)

homeFrame.lift()
root.mainloop()

#       **********
