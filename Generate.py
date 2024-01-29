import os
from docxtpl import DocxTemplate
import MySQL


def generatePaystub(paymentID):
    """ Generates a Paystub for PaymentID, opens it, and saves it to OpenPay\PayStubs\ """

    if paymentID == 0:
        return

    MySQL.establishConnection()

    EmployeeColumns = ["EmployeeFN", "EmployeeLN", "EmployeeStreetNum", "EmployeeStreetName", "EmployeeCity",
                       "EmployeeState", "EmployeeZIP"]
    EmployeeInfo = []
    for i in range(len(EmployeeColumns)):
        if MySQL.getEmployeeValue(MySQL.getPaymentValue(paymentID, 'EmployeeID'), EmployeeColumns[i]) is None:
            EmployeeInfo.append('')
        else:
            EmployeeInfo.append(
                MySQL.getEmployeeValue(MySQL.getPaymentValue(paymentID, 'EmployeeID'), EmployeeColumns[i]))
    if EmployeeInfo[4] != '':
        EmployeeInfo[4] = EmployeeInfo[4] + ','

    paymentDate = str(MySQL.getPaymentValue(paymentID, 'PaymentDate'))
    readableDate = paymentDate[5:7] + '-' + \
                   paymentDate[8:10] + '-' + \
                   paymentDate[:4]

    PaymentColumns = ["PaymentGrossPay", "PaymentHousing", "PaymentHSA", "PaymentSSTax", "PaymentMedicareTax",
                      "PaymentFedWH", "PaymentSETax", "PaymentNetPay"]
    CurrentPaymentInfo = []
    for i in range(len(PaymentColumns)):
        if MySQL.getPaymentValue(paymentID, PaymentColumns[i]) is None:
            CurrentPaymentInfo.append(0.00)
        else:
            CurrentPaymentInfo.append(MySQL.getPaymentValue(paymentID, PaymentColumns[i]))
    YearPaymentInfo = []
    for i in PaymentColumns:
        if MySQL.getYTD(paymentID, i) is None:
            YearPaymentInfo.append(0.00)
        else:
            YearPaymentInfo.append(MySQL.getYTD(paymentID, i))

    context = {
        'EmployeeFN': EmployeeInfo[0],
        'EmployeeLN': EmployeeInfo[1],
        'EmployeeStreetNum': EmployeeInfo[2],
        'EmployeeStreetName': EmployeeInfo[3],
        'EmployeeCity': EmployeeInfo[4],
        'EmployeeState': EmployeeInfo[5],
        'EmployeeZIP': EmployeeInfo[6],
        'PaymentDate': readableDate,
        'PaymentGrossPay': CurrentPaymentInfo[0],
        'YearGrossPay': YearPaymentInfo[0],
        'PaymentHousing': CurrentPaymentInfo[1],
        'YearHousing': YearPaymentInfo[1],
        'PaymentHSA': CurrentPaymentInfo[2],
        'YearHSA': YearPaymentInfo[2],
        'PaymentSSTax': CurrentPaymentInfo[3],
        'YearSSTax': YearPaymentInfo[3],
        'PaymentMedicareTax': CurrentPaymentInfo[4],
        'YearMedicareTax': YearPaymentInfo[4],
        'PaymentFedWH': CurrentPaymentInfo[5],
        'YearFedWH': YearPaymentInfo[5],
        'PaymentSETax': CurrentPaymentInfo[6],
        'YearSETax': YearPaymentInfo[6],
        'PaymentNetPay': CurrentPaymentInfo[7],
        'YearNetPay': YearPaymentInfo[7]
    }

    MySQL.closeConnection()

    doc = DocxTemplate("Paystub_Template.docx")
    doc.render(context)
    doc.save("PayStubs\generated_paystub" + str(paymentID) + ".docx")
    os.startfile("PayStubs\generated_paystub" + str(paymentID) + ".docx")

    return
