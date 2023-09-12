####################### Functions of 16a1 #############################
import openpyxl
from selenium.webdriver.common.by import By


def get_receiver_16a1(self):
    receiver = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Đơn vị nhận tiền:')]")
    receiver_value = self.extract_text(receiver)
    receiver_value = receiver_value.replace("Đơn vị nhận tiền:", "")
    return self.trim_text(receiver_value)

def get_bank_accounts_16a1(self):
    bank_accounts = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Tài khoản: ')]")
    sender_acc, receiver_acc = [self.extract_text(b) for b in bank_accounts]
    sender_acc = sender_acc.replace("Tài khoản:", "").replace(".", "")
    sender_acc = self.trim_text(sender_acc)
    receiver_acc = receiver_acc.replace("Tài khoản:", "").replace(".", "")
    receiver_acc = self.trim_text(receiver_acc)
    return sender_acc, receiver_acc

def get_location_16a1(self):
    location = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Tại KBNN (NH):')]")
    location_value = self.extract_text(location)
    substring_to_remove = "Tại KBNN (NH):"
    location_value = location_value.replace(substring_to_remove, "")
    return self.trim_text(location_value)

def get_date_16a1(self):
    dates = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Ngày')]")

    formatted_date = ""
    for date in dates:
        formatted_date = self.extract_date(date.text)
        if formatted_date:
            break

    return formatted_date

def write_to_excel(self, code_value, number_value, unit_value, receiver_value, sender_acc, receiver_acc, location_value, formatted_date, contents, money):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    header_row = [
        "Mã",
        "Số",
        "Đơn vị",
        "Tài Khoản 1",
        "Nội Dung",
        "Số Tiền",
        "Đơn vị nhận tiền",
        "Tài khoản nhận",
        "Tại",
        "Ngày",
    ]
    sheet.append(header_row)

    for content, amount in zip(contents[1:], money[1:]):
        content_text = content.text
        money_text = int(amount.text.replace(".", ""))
        sheet.append(
            [
                code_value,
                number_value,
                unit_value,
                sender_acc,
                content_text,
                money_text,
                receiver_value,
                receiver_acc,
                location_value,
                formatted_date,
            ]
        )

    workbook.save("16a1.xlsx")

def process_model_16a1(self, code_value):

    number_value = self.get_number()
    unit_value = self.get_unit_16a1()
    receiver_value = self.get_receiver_16a1()
    sender_acc = self.get_bank_accounts_16a1()[0]
    receiver_acc = self.get_bank_accounts_16a1()[1]
    location_value = self.get_location_16a1()
    formatted_date = self.get_date_16a1()
    contents = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_0_"]')
    money = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_soTien_"]')
    self.write_to_excel(code_value, number_value, unit_value, receiver_value, sender_acc, receiver_acc, location_value, formatted_date, contents, money)
        
####################### End 16a1 ##############################