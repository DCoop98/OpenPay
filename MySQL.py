import decimal
import mysql.connector
import datetime

SocialSecurityTaxRate = decimal.Decimal(.062)
# Standard withholding percentage per check for social security taxes

MedicareTaxRate = decimal.Decimal(.0145)
# Standard withholding percentage per check for medicare taxes

SelfEmploymentTaxRate = decimal.Decimal(.15)


# standard withholding percentage per check for self employment taxes


def establishConnection():
    """ Establishes a connection to the local database and sets up db_cursor """

    global db_connection
    global db_cursor

    # Modify this if your MySQL Server Login Info is different.
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="OpenPay",
    )

    # creating database_cursor to perform SQL operation
    db_cursor = db_connection.cursor()

    # select Database OpenPay
    db_cursor.execute("USE OpenPay")


def closeConnection():
    """ Attempts to close the connection to the database """

    # try except block ensures that if there is not an active connection, the program will keep running.f
    try:
        db_cursor.close()
        db_connection.commit()
        db_connection.close()
    except:
        print("Connection already closed. ")


def tableExists(tableName):
    """ returns 1 if tableName exists, 0 if it does not """

    EmployeeStatement = "SHOW TABLES LIKE '" + tableName + "'"
    db_cursor.execute(EmployeeStatement)
    result = db_cursor.fetchone()
    if result:
        return 1
    else:
        return 0


def createDatabase():
    """ Create the database if it has not already been created """

    global db_connection
    global db_cursor

    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="OpenPay",
    )

    # creating database_cursor to perform SQL operation
    db_cursor = db_connection.cursor()
    db_cursor.execute("CREATE DATABASE IF NOT EXISTS OpenPay")
    closeConnection()


def createTables():
    """ Creates all tables if they have not already been created """

    establishConnection()

    if not tableExists('Positions'):
        db_cursor.execute("CREATE TABLE Positions("
                          "PositionID INT NOT NULL AUTO_INCREMENT, "
                          "PositionName VARCHAR(100) NOT NULL, "
                          "PositionSalary DECIMAL(15,2), "
                          "PositionHourlyRate DECIMAL(15,2), "
                          "PositionHousingAllowance DECIMAL(15,2), "
                          "PositionHSA DECIMAL(15,2), "
                          "PositionFedWH DECIMAL(15,2), "
                          "PositionSEWH DECIMAL(15,2), "
                          "PositionIsSE BOOLEAN, "
                          "PositionPayInterval VARCHAR(30), "
                          "PositionIsHidden BOOLEAN, "
                          "PRIMARY KEY ( PositionID )"
                          ")")
    else:
        print("Positions already exists.")

    if not tableExists('Employees'):
        db_cursor.execute("CREATE TABLE Employees("
                          "EmployeeID INT NOT NULL AUTO_INCREMENT, "
                          "EmployeePrefix VARCHAR(10), "
                          "EmployeeFN VARCHAR(30) NOT NULL, "
                          "EmployeeMN VARCHAR(30), "
                          "EmployeeLN VARCHAR(30) NOT NULL, "
                          "EmployeeSuffix VARCHAR(10), "
                          "PositionID INT, "
                          "EmployeeSalary DECIMAL(15,2) NOT NULL, "
                          "EmployeeHourlyRate DECIMAL(15,2) NOT NULL, "
                          "EmployeeHousingAllowance DECIMAL(15,2) NOT NULL, "
                          "EmployeeHSA DECIMAL(15,2) NOT NULL, "
                          "EmployeeFedWH DECIMAL(15,2) NOT NULL, "
                          "EmployeeSEWH DECIMAL(15,2) NOT NULL, "
                          "EmployeePayInterval VARCHAR(30), "
                          "EmployeeIsSE BOOLEAN NOT NULL, "
                          "EmployeeStreetNum INT, "
                          "EmployeeStreetName VARCHAR(50), "
                          "EmployeeCity VARCHAR(50), "
                          "EmployeeState VARCHAR(50), "
                          "EmployeeZIP VARCHAR(15), "
                          "EmployeeAptBuilding VARCHAR(30), "
                          "EmployeeAptRoom VARCHAR(30), "
                          "EmployeePOBox VARCHAR(30), "
                          "EmployeePrimaryEmail VARCHAR(150), "
                          "EmployeeSecondaryEmail VARCHAR(150), "
                          "EmployeeHomeNum VARCHAR(30), "
                          "EmployeeCellNum VARCHAR(30), "
                          "EmployeeWorkNum VARCHAR(30), "
                          "EmployeeGender CHAR(1), "
                          "EmployeeMaritalStatus CHAR(1), "
                          "EmployeeBirthdate DATE, "
                          "EmployeeIsHidden BOOLEAN, "
                          "PRIMARY KEY( EmployeeID ), "
                          "FOREIGN KEY ( PositionID ) REFERENCES Positions( PositionID )"
                          ")")
    else:
        print("Employees already exists.")

    if not tableExists('Payments'):
        db_cursor.execute("CREATE TABLE Payments("
                          "PaymentID INT NOT NULL AUTO_INCREMENT, "
                          "EmployeeID INT, "
                          "PaymentDate DATE NOT NULL, "
                          "PaymentTime TIME NOT NULL, "
                          "PaymentHours DECIMAL(15,2), "
                          "PaymentGrossPay DECIMAL(15,2) NOT NULL, "
                          "PaymentHousing DECIMAL(15,2) NOT NULL, "
                          "PaymentHSA DECIMAL(15,2) NOT NULL, "
                          "PaymentSSTax DECIMAL(15,2) NOT NULL, "
                          "PaymentMedicareTax DECIMAL(15,2) NOT NULL, "
                          "PaymentSETax DECIMAL(15,2) NOT NULL, "
                          "PaymentFedWH DECIMAL(15,2) NOT NULL, "
                          "PaymentNetPay DECIMAL(15,2) NOT NULL, "
                          "PaymentIsHidden BOOLEAN, "
                          "PRIMARY KEY ( PaymentID ), "
                          "FOREIGN KEY ( EmployeeID ) REFERENCES Employees( EmployeeID )"
                          ")")
    else:
        print("Payments already exists.")

    closeConnection()


def printDatabases():
    """ get list of all databases """

    establishConnection()
    db_cursor.execute("SHOW DATABASES")
    # print all databases
    for db in db_cursor:
        print(db)
    return
    closeConnection()


def addQuote(myString):
    """ adds single quotes around a string if the string does not equal null """

    if not myString == 'NULL':
        myString = "'" + str(myString) + "'"
    return myString


def getValue():
    """ Returns the 1st value in the last row retrieved from a database. useful for finding one specific value

    Must establish connection and select a row before calling """

    row = db_cursor.fetchone()
    return row[0]


def getEmployeeValue(EmployeeID, EmployeeColumn):
    """ returns the the value in the EmployeeColumn column of the Employees table from the row with EmployeeID
   Must establish connection before calling """

    EmployeeIDStr = str(EmployeeID)
    db_cursor.execute("SELECT " + EmployeeColumn + " FROM Employees WHERE EmployeeID = " + EmployeeIDStr)
    return getValue()


def getEmployeeFN_LN(EmployeeID):
    """ Returns "EmployeeFN EmployeeLN" for EmployeeID """

    EmployeeIDStr = str(EmployeeID)
    db_cursor.execute("SELECT EmployeeFN FROM Employees WHERE EmployeeID = " + EmployeeIDStr + ";")
    firstName = getValue()
    db_cursor.execute("SELECT EmployeeLN FROM Employees WHERE EmployeeID = " + EmployeeIDStr + ";")
    lastName = getValue()
    fullName = firstName + ' ' + lastName
    return fullName


def getMax(tableName, columnName):
    """ returns the max value of the specified column from the specified table. """

    db_cursor.execute("SELECT MAX(" + columnName + ") FROM " + tableName + ";")
    value = getValue()
    # If there are no employees, return 0
    if value is not None:
        return value
    else:
        return 0


def getNextHighest(tableName, columnName, previousMax):
    """ returns the next highest (after previousMax) value of columnName in tableName """

    if not previousMax == 0:
        previousMaxStr = str(previousMax)
        db_cursor.execute(
            "SELECT MAX(" + columnName + ") FROM " + tableName + " WHERE " + columnName + " < " + previousMaxStr)
        value = getValue()
        # If previousMax is last employee, return 0
        if value is not None:
            return value
        else:
            return 0
    else:
        return 0


def getPaymentIDsByDate():
    db_cursor.execute(
        "SELECT PaymentID From Payments ORDER BY PaymentDate DESC;"
    )
    rows = db_cursor.fetchall()
    if rows is not None:
        return rows
    else:
        return 0


def getEmployeePaymentIDsByDate(EmployeeID):
    db_cursor.execute(
        "SELECT PaymentID From Payments WHERE EmployeeID = " + str(EmployeeID) + " ORDER BY PaymentDate DESC;"
    )
    rows = db_cursor.fetchall()
    if rows is not None:
        return rows
    else:
        return 0


def addEmployee(EmployeePrefix='NULL', EmployeeFN='NULL', EmployeeMN='NULL', EmployeeLN='NULL', EmployeeSuffix='NULL',
                PositionID=0, EmployeeSalary=0.0, EmployeeHourlyRate=0.0, EmployeePayInterval='NULL', EmployeeIsSE=0.0,
                EmployeeStreetNum='NULL',
                EmployeeStreetName='NULL', EmployeeCity='NULL', EmployeeState='NULL', EmployeeZIP='NULL',
                EmployeeAptBuilding='NULL', EmployeeAptRoom='NULL', EmployeePOBox='NULL', EmployeePrimaryEmail='NULL',
                EmployeeSecondaryEmail='NULL', EmployeeHomeNum='NULL', EmployeeCellNum='NULL', EmployeeWorkNum='NULL',
                EmployeeGender='NULL', EmployeeMaritalStatus='NULL', EmployeeBirthdate='NULL',
                EmployeeHousingAllowance=0.0, EmployeeHSA=0.0, EmployeeFedWH=0.0, EmployeeSEWH=0.0):
    """ Creates a new row on the employees table """

    establishConnection()

    # The statements below convert ints into strings for use in database execution
    if PositionID == 0:
        PositionIDStr = 'NULL'
    else:
        PositionIDStr = str(PositionID)
    EmployeeSalaryStr = str(EmployeeSalary)
    EmployeeHourlyRateStr = str(EmployeeHourlyRate)
    EmployeeIsSEStr = str(EmployeeIsSE)
    EmployeeHousingAllowanceStr = str(EmployeeHousingAllowance)
    EmployeeHSAStr = str(EmployeeHSA)
    EmployeeFedWHStr = str(EmployeeFedWH)
    EmployeeSEWHStr = str(EmployeeSEWH)

    # The statements below add quotes to every value for use in database execution
    EmployeePrefix = addQuote(EmployeePrefix)
    EmployeeFN = addQuote(EmployeeFN)
    EmployeeMN = addQuote(EmployeeMN)
    EmployeeLN = addQuote(EmployeeLN)
    EmployeeSuffix = addQuote(EmployeeSuffix)
    EmployeePayInterval = addQuote(EmployeePayInterval)
    EmployeeStreetNum = addQuote(EmployeeStreetNum)
    EmployeeStreetName = addQuote(EmployeeStreetName)
    EmployeeCity = addQuote(EmployeeCity)
    EmployeeState = addQuote(EmployeeState)
    EmployeeZIP = addQuote(EmployeeZIP)
    EmployeeAptBuilding = addQuote(EmployeeAptBuilding)
    EmployeeAptRoom = addQuote(EmployeeAptRoom)
    EmployeePOBox = addQuote(EmployeePOBox)
    EmployeePrimaryEmail = addQuote(EmployeePrimaryEmail)
    EmployeeSecondaryEmail = addQuote(EmployeeSecondaryEmail)
    EmployeeGender = addQuote(EmployeeGender)
    EmployeeMaritalStatus = addQuote(EmployeeMaritalStatus)
    EmployeeBirthdate = addQuote(EmployeeBirthdate)
    EmployeeHomeNum = addQuote(EmployeeHomeNum)
    EmployeeCellNum = addQuote(EmployeeCellNum)
    EmployeeWorkNum = addQuote(EmployeeWorkNum)

    # MySQL command to create row on Employees Table
    db_cursor.execute("INSERT INTO Employees (EmployeePrefix, EmployeeFN, EmployeeMN, EmployeeLN, EmployeeSuffix, "
                      "PositionID, "
                      "EmployeeSalary, EmployeeHourlyRate, EmployeePayInterval, EmployeeIsSE, EmployeeStreetNum, "
                      "EmployeeStreetName, EmployeeCity, EmployeeState, EmployeeZIP, EmployeeAptBuilding, "
                      "EmployeeAptRoom, EmployeePOBox, EmployeePrimaryEmail, EmployeeSecondaryEmail, EmployeeHomeNum, "
                      "EmployeeCellNum, EmployeeWorkNum, EmployeeGender, EmployeeMaritalStatus, EmployeeBirthdate, "
                      "EmployeeHousingAllowance, EmployeeHSA, EmployeeFedWH, EmployeeSEWH)"
                      "VALUES (" + EmployeePrefix + ", " + EmployeeFN + ", " + EmployeeMN + ", " + EmployeeLN + ", " +
                      EmployeeSuffix + ", " + PositionIDStr + ", " + EmployeeSalaryStr + ", " + EmployeeHourlyRateStr + ", " +
                      EmployeePayInterval + ", " + EmployeeIsSEStr + ", " + EmployeeStreetNum + ", " +
                      EmployeeStreetName + ", " + EmployeeCity + ", " + EmployeeState + ", " + EmployeeZIP + ", " +
                      EmployeeAptBuilding + ", " + EmployeeAptRoom + ", " + EmployeePOBox + ", " + EmployeePrimaryEmail
                      + ", " + EmployeeSecondaryEmail + ", " + EmployeeHomeNum + ", " + EmployeeCellNum + ", " +
                      EmployeeWorkNum + ", " + EmployeeGender + ", " + EmployeeMaritalStatus + ", " + EmployeeBirthdate
                      + ", " + EmployeeHousingAllowanceStr + ", " + EmployeeHSAStr + ", " + EmployeeFedWHStr + ", " +
                      EmployeeSEWHStr + ");")

    closeConnection()


def deleteEmployee(EmployeeID):
    """ deletes the employee with  the specified employee id from the employees table, along with all of their payments
    from the payments table """

    establishConnection()
    EmployeeIDStr = str(EmployeeID)
    db_cursor.execute("DELETE FROM Payments WHERE EmployeeID = '" + EmployeeIDStr + "';")
    db_cursor.execute("DELETE FROM Employees WHERE EmployeeID = '" + EmployeeIDStr + "';")
    closeConnection()


def hideEmployee(EmployeeID):
    # Hides the employee with the specified EmployeeID

    establishConnection()

    EmployeeIDStr = str(EmployeeID)

    db_cursor.execute("UPDATE Employees SET EmployeeIsHidden = 1 WHERE EmployeeID = " + EmployeeIDStr + ";")

    closeConnection()


def revealEmployee(EmployeeID):
    """ Unhides an employee with the specified employeeID """

    establishConnection()

    EmployeeIDStr = str(EmployeeID)

    db_cursor.execute("UPDATE Employees SET EmployeeIsHidden = 0 WHERE EmployeeID = " + EmployeeIDStr + ";")

    closeConnection()


def addPayment(EmployeeID, PaymentDate='NULL', PaymentTime='NULL',
               PaymentHours=decimal.Decimal(0), PaymentGrossPay=decimal.Decimal(0),
               PaymentHousing=decimal.Decimal(0), PaymentHSA=decimal.Decimal(0), PaymentSSTax=decimal.Decimal(0),
               PaymentMedicareTax=decimal.Decimal(0), PaymentSETax=decimal.Decimal(0),
               PaymentFedWH=decimal.Decimal(0), PaymentNetPay=decimal.Decimal(0)):
    """ Adds a new payment to the payments table for the specified employee with other variables if specified """

    establishConnection()

    # converts all variable types to strings
    EmployeeIDStr = str(EmployeeID)
    PaymentDateStr = str(PaymentDate)
    PaymentTimeStr = str(PaymentTime)
    PaymentHoursStr = str(PaymentHours)
    PaymentGrossPayStr = str(PaymentGrossPay)
    PaymentHousingStr = str(PaymentHousing)
    PaymentHSAStr = str(PaymentHSA)
    PaymentSSTaxStr = str(PaymentSSTax)
    PaymentMedicareTaxStr = str(PaymentMedicareTax)
    PaymentSETaxStr = str(PaymentSETax)
    PaymentFedWHStr = str(PaymentFedWH)
    PaymentNetPayStr = str(PaymentNetPay)

    # Add Quotes for MySQL Statement
    PaymentDateStr = addQuote(PaymentDateStr)
    PaymentTimeStr = addQuote(PaymentTimeStr)

    # MySQL Code inserts actual row on Payments Table
    db_cursor.execute("INSERT INTO PAYMENTS (EmployeeID, PaymentDate, PaymentTime, PaymentHours, PaymentGrossPay, "
                      "PaymentHousing, PaymentHSA, PaymentSSTax, PaymentMedicareTax, PaymentSETax, PaymentFedWH, "
                      "PaymentNetPay)"
                      "VALUE (" + EmployeeIDStr + ", " + PaymentDateStr + ", " + PaymentTimeStr + ", " + PaymentHoursStr +
                      ", " + PaymentGrossPayStr + ", " + PaymentHousingStr + ", " + PaymentHSAStr + ", " +
                      PaymentSSTaxStr + ", " + PaymentMedicareTaxStr + ", " + PaymentSETaxStr + ", " + PaymentFedWHStr +
                      ", " + PaymentNetPayStr + ")")

    closeConnection()


def deletePayment(PaymentID):
    """ deletes the payment with the specified paymentID from the payments table """

    establishConnection()
    PaymentIDStr = str(PaymentID)
    db_cursor.execute("DELETE FROM Payments WHERE PaymentID = '" + PaymentIDStr + "';")
    closeConnection()


def hidePayment(PaymentID):
    """ Hides the payment with the specified paymentID """

    establishConnection()

    PaymentIDStr = str(PaymentID)

    db_cursor.execute("UPDATE Payments SET PaymentIsHidden = 1 WHERE PaymentID = " + PaymentIDStr + ";")

    closeConnection()


def revealPayment(PaymentID):
    """ Unhides the payment with the specified id """

    establishConnection()

    PaymentIDStr = str(PaymentID)

    db_cursor.execute("UPDATE Payments SET PaymentIsHidden = 0 WHERE PaymentID = " + PaymentIDStr + ";")

    closeConnection()


def getPaymentValue(PaymentID, PaymentColumn):
    """ returns the value in the PaymentColumn column of the Payments table from the row with PaymentID

    Must establish connection before calling """

    PaymentIDStr = str(PaymentID)
    db_cursor.execute("SELECT " + PaymentColumn + " FROM Payments WHERE PaymentID = " + PaymentIDStr)
    return getValue()


def getMonthlyTotal(Month, Year, PaymentColumn):
    """ Returns The Totals of PaymentColumn Within a given Month. Pass Month as a string and PaymentColumn as a string.
    """

    establishConnection()

    db_cursor.execute("SELECT SUM(" + PaymentColumn + ") "
                                                      "FROM  payments " +
                      "WHERE PaymentDate LIKE '" + Year + '-' + Month + "-%'")

    row = db_cursor.fetchone()

    closeConnection()

    if row[0] is not None:
        return row[0]
    else:
        return 0


def getQuarterlyTotal(Quarter, Year, PaymentColumn):
    """ Returns the total amount in payment column for quarter 1, 2, 3, or 4 of Year"""

    if Quarter == 1:
        conditional = "WHERE PaymentDate LIKE '" + Year + "-01-%' " \
                                                          "OR PaymentDate LIKE '" + Year + "-02-%' " \
                                                                                           "OR PaymentDate LIKE '" + Year + "-03-%'"
    elif Quarter == 2:
        conditional = "WHERE PaymentDate LIKE '" + Year + "-04-%' " \
                                                          "OR PaymentDate LIKE '" + Year + "-05-%' " \
                                                                                           "OR PaymentDate LIKE '" + Year + "-06-%'"
    elif Quarter == 3:
        conditional = "WHERE PaymentDate LIKE '" + Year + "-07-%' " \
                                                          "OR PaymentDate LIKE '" + Year + "-08-%' " \
                                                                                           "OR PaymentDate LIKE '" + Year + "-09-%'"
    elif Quarter == 4:
        conditional = "WHERE PaymentDate LIKE '" + Year + "-10-%' " \
                                                          "OR PaymentDate LIKE '" + Year + "-11-%' " \
                                                                                           "OR PaymentDate LIKE '" + Year + "-12-%'"
    else:
        return

    establishConnection()

    db_cursor.execute("SELECT SUM(" + PaymentColumn + ") \
    FROM Payments " \
                      + conditional)

    row = db_cursor.fetchone()

    closeConnection()

    if row[0] is not None:
        return row[0]
    else:
        return 0


def getSEGrossPay(Quarter, Year):
    """ returns the total amount in PaymentGrossPay for Self-employed employees only for Year.

    Used for calculating fica pay """

    if Quarter == 1:
        conditional = "WHERE p.EmployeeID = e.EmployeeID\
         AND (p.PaymentDate LIKE '" + Year + "-01-%' " \
                                             "OR p.PaymentDate LIKE '" + Year + "-02-%' " \
                                                                                "OR p.PaymentDate LIKE '" + Year + "-03-%') \
         AND e.EmployeeIsSE = 1"
    elif Quarter == 2:
        conditional = "WHERE p.EmployeeID = e.EmployeeID\
                 AND (p.PaymentDate LIKE '" + Year + "-04-%' " \
                                                     "OR p.PaymentDate LIKE '" + Year + "-05-%' " \
                                                                                        "OR p.PaymentDate LIKE '" + Year + "-06-%') \
                 AND e.EmployeeIsSE = 1"
    elif Quarter == 3:
        conditional = "WHERE p.EmployeeID = e.EmployeeID\
                 AND (p.PaymentDate LIKE '" + Year + "-07-%' " \
                                                     "OR p.PaymentDate LIKE '" + Year + "-08-%' " \
                                                                                        "OR p.PaymentDate LIKE '" + Year + "-09-%') \
                 AND e.EmployeeIsSE = 1"
    elif Quarter == 4:
        conditional = "WHERE p.EmployeeID = e.EmployeeID\
                         AND (p.PaymentDate LIKE '" + Year + "-10-%' " \
                                                             "OR p.PaymentDate LIKE '" + Year + "-11-%' " \
                                                                                                "OR p.PaymentDate LIKE '" + Year + "-12-%') \
                         AND e.EmployeeIsSE = 1"
    else:
        return

    establishConnection()

    db_cursor.execute("SELECT SUM(PaymentGrossPay) \
    FROM Payments p, Employees e " + conditional)

    row = db_cursor.fetchone()

    closeConnection()

    if row[0] is not None:
        return row[0]
    else:
        return 0


def getYTD(paymentID, paymentColumn):
    """ returns the YTD value of PaymentColumn for the employee receiving Payment ID """

    establishConnection()

    endDate = str(getPaymentValue(paymentID, 'PaymentDate'))
    employeeID = getPaymentValue(paymentID, 'EmployeeID')
    startDate = endDate[:4] + '-01-01'

    db_cursor.execute("SELECT SUM(" + paymentColumn + ") "
                                                      "FROM Payments p, Employees e "
                                                      "WHERE p.EmployeeID = e.EmployeeID "
                                                      "AND p.EmployeeID = " + str(employeeID) + " "
                                                                                                "AND p.PaymentDate <= '" + endDate + "' "
                                                                                                                                     "AND p.PaymentDate >= '" + startDate + "'")

    row = db_cursor.fetchone()

    closeConnection()

    if row[0] is not None:
        return row[0]
    else:
        return 0


def makeString(decValue):
    """ Returns 'NULL' as String if decValue is .1, else returns decValue as String """

    if decValue == .1:
        return 'NULL'
    else:
        return str(decValue)


def addPosition(PositionName, PositionSalary='NULL', PositionHourlyRate='NULL', PositionHousingAllowance='NULL',
                PositionHSA='NULL', PositionSEWH='NULL', PositionFedWH='NULL', PositionPayInterval='NULL',
                PositionIsSE='NULL'):
    """ Creates a new entry on the Positions table """

    establishConnection()

    # Converts all values into NULL Strings if default, else makes them into Strings equal to user value
    PositionSalaryStr = makeString(PositionSalary)
    PositionHourlyRateStr = makeString(PositionHourlyRate)
    PositionHousingAllowanceStr = makeString(PositionHousingAllowance)
    PositionHSAStr = makeString(PositionHSA)
    PositionSEWHStr = makeString(PositionSEWH)
    PositionFedWHStr = makeString(PositionFedWH)
    PositionIsSEStr = makeString(PositionIsSE)

    PositionName = addQuote(PositionName)
    PositionPayInterval = addQuote(PositionPayInterval)

    db_cursor.execute("INSERT INTO Positions(PositionName, PositionSalary, PositionHourlyRate, "
                      "PositionHousingAllowance, PositionHSA, PositionSEWH, PositionFedWH, PositionPayInterval, "
                      "PositionIsSE)"
                      "VALUES(" + PositionName + ", " + PositionSalaryStr + ", " + PositionHourlyRateStr + ", " +
                      PositionHousingAllowanceStr + ", " + PositionHSAStr + ", " + PositionSEWHStr + ", " +
                      PositionFedWHStr + ", " + PositionPayInterval + ", " + PositionIsSEStr + ");")

    closeConnection()


def deletePosition(PositionID):
    """ Deletes the specified positionID after updating all employees' PositionID with that position to 'NULL' """

    establishConnection()

    PositionIDStr = str(PositionID)

    db_cursor.execute("UPDATE Employees SET PositionID = NULL WHERE PositionID = " + PositionIDStr
                      + ";")
    db_cursor.execute("DELETE FROM Positions WHERE PositionID = " + PositionIDStr + ";")

    closeConnection()


def hidePosition(PositionID):
    """ Hides the position with the specified positionID """

    establishConnection()

    PositionIDStr = str(PositionID)

    db_cursor.execute("UPDATE Positions SET PositionIsHidden = 1 WHERE PositionID = " + PositionIDStr + ";")

    closeConnection()


def revealPosition(PositionID):
    """ Unhides the position specified by the PositionID """

    establishConnection()

    PositionIDStr = str(PositionID)

    db_cursor.execute("UPDATE Positions SET PositionIsHidden = 0 WHERE PositionID = " + PositionIDStr + ";")

    closeConnection()


def getPositionValue(PositionID, PositionColumn):
    """ returns the value in the PaymentColumn column of the Payments table from the row with PaymentID

    Must establish connection before calling """

    PositionIDStr = str(PositionID)
    db_cursor.execute("SELECT " + PositionColumn + " FROM Positions WHERE PositionID = " + PositionIDStr)
    return getValue()


def editTable(TableName, ID, ColumnName, ColumnValue):
    """ Modifies ColumnName of TableName to equal ColumnValue on the Corresponding ID

    For TableName:
        Pass "Employees", "Positions", or "Payments" as String
    For ID:
        Pass Corresponding ID as Int
    For ColumnName:
        Pass as String
    For ColumnValue:
        If number, pass as string (ex. ColumnValue = "3")
        If string, pass as string with extra set of '' (ex. ColumnValue = "'Accountant'")
    """

    establishConnection()

    IDName = 'NULL'

    # Sets IDName based on what table is being accessed
    if TableName == "Employees":
        IDName = "EmployeeID"
    elif TableName == "Payments":
        IDName = "PaymentID"
    elif TableName == "Positions":
        IDName = "PositionID"

    # Converts ID to a string
    IDStr = str(ID)

    # Updates Database
    if not IDName == 'NULL':
        db_cursor.execute("UPDATE " + TableName + " SET " + ColumnName + " = " + ColumnValue + " WHERE " + IDName +
                          " = " + IDStr + ";")

    closeConnection()


def formatDate(date):
    """ Formats [date] to be readable for dumb Americans """

    dateStr = str(date)
    db_cursor.execute("SELECT DATE_FORMAT('" + dateStr + "', '%m/%d/%Y');")
    return getValue()

