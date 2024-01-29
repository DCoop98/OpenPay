Installation Instructions

1. Download and Install Python: https://www.python.org/downloads/

2. Ensure that python is working correctly by typing "py --version" in a command prompt. 
If this does not work, you may have to add the python directory and the python/scripts directory to the system variable PATH. 
Python's Directory will typically be C:\Users\USERNAME\PythonVERSION or C:\Users\USERNAME\AppData\Local\Programs\Python\PythonVERSION

3.Install MySQL Community Server: https://dev.mysql.com/downloads/windows/installer/8.0.html
Use all default options, but setup OpenPay as the root password.

If you already have MySQL setup for another use, you can change the password for root if this will not interfere with other processes.
Alternatively, you may setup a new user with access to the database or use a more secure password than OpenPay.
If you do this, change the login info on the establishConnection() function in MySQL.py .


4.Use pip to install required packages.
To do this, open a command prompt and type the following commands:

pip install datetime
pip install mysql-connector-python
pip install docx
pip install docxtpl

If mysql-connector-python installation fails and says you need Microsoft Visual C++ 14.0,
go to https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2017 and download the Visual Studio Community Installer.
During installation, ONLY check Desktop development with C++ and Python Development. Then, run pip install mysql-connector-python again.

5. Open OpenPay.pyw to run the program. You can create a shortcut to your desktop for future ease of use.


Design Documentation (for code maintenance)

OpenPay uses three files:

MySQL.py
Generate.py
OpenPay.py

MySQL.py contains all functions used to interact with the database.
Generate.py contains the functions used to generate pay stubs and can be used for future template report generation as well.
OpenPay.py is the main python function that is run on start. It creates the GUI and calls functions from MySQL.py and Generate.py as the user interacts with the program.

All functions have docstrings as outlined by python's official documentation that describe its usage.

Paystub_Template.docx is the template used to generate pay stubs. The user can move variables as desired to rearrange the appearance of pay stubs.
All pay stubs are stored in OpenPay\PayStubs\ by default, but the user will most likely save them to a new location as well.

ALTER TABLE `openpay`.`employees`
ADD COLUMN `EmployeeSEWH` DECIMAL(15,2) NOT NULL AFTER `EmployeeFedWH`;