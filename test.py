import os
import pandas as pd 
import unittest
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.chrome.options import Options
import constants

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

###################### common ###############################
    def extract_text(self, element):
        return element.text
    
    def convert_to_string(self, string): 
        return "`" + string;
    
    def trim_text(self, element):
        element = element.lstrip()
        element = element.rstrip()
        return element

    def extract_date(self, text):
        pattern = r"Ngày?\s+(\d{2})?\s+tháng?\s+(\d{2})?\s+năm?\s+(\d{4})(?:\s+|$)"
        match = re.search(pattern, text)
        if match:
            day, month, year = match.groups()
            return f"{day}/{month}/{year}"
        return ""
    
    def get_content_by_key_search(self, key_search):
        try:
            unit = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{key_search}')]")
            unit_value = self.extract_text(unit)
            unit_value = unit_value.replace(key_search, "")
            return self.trim_text(unit_value)
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def get_bank_accounts_16a1(self):
        bank_accounts = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Tài khoản: ')]")
        sender_acc, receiver_acc = [self.extract_text(b) for b in bank_accounts]
        sender_acc = sender_acc.replace("Tài khoản:", "").replace(".", "")
        sender_acc = self.trim_text(sender_acc) 
        sender_acc = str(sender_acc)

        receiver_acc = receiver_acc.replace("Tài khoản:", "").replace(".", "")
        receiver_acc = self.trim_text(receiver_acc)
        receiver_acc = str(receiver_acc)
        return sender_acc, receiver_acc
    
    def get_receiver_16a1(self):
        receiver = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Đơn vị nhận tiền:')]")
        receiver_value = self.extract_text(receiver)
        receiver_value = receiver_value.replace("Đơn vị nhận tiền:", "")
        return self.trim_text(receiver_value)
    
    def get_date(self):
        dates = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Ngày')]")

        formatted_date = ""
        for date in dates:
            formatted_date = self.extract_date(date.text)
            if formatted_date:
                break

        return formatted_date
    
    def get_element_content_by_xpath(self, xpath):
        element = self.driver.find_element(By.XPATH, xpath)
        return element.text
    
    def save_information_workbook_16a2_16c(self, code, number, unit, sender_acc, receiver_acc, contents, total, tax, paid, receiver, location, formatted, workbook_name):
        headers_to_check =  [
                    "Mã",
                    "Số",
                    "Đơn vị",
                    "Tài Khoản gởi",
                    "Nội Dung",
                    "Tổng số tiền",
                    "Nộp thuế",
                    "Thanh toán cho ĐV hưởng",
                    "Đơn vị nhận tiền",
                    "Tài khoản nhận",
                    "Tại",
                    "Ngày",
                ]

        result_array = []
        for content, amount, tax_chil, paid_chil in zip(contents[1:], total[1:], tax[1:], paid[1:]):
            content_text = content.text
            money_text = amount.text.replace(".", "")
            tax_text = tax_chil.text.replace(".", "")
            paid_text = paid_chil.text.replace(".", "")
            result_array.append((
                    code,
                    number,
                    unit,
                    sender_acc,
                    content_text,
                    money_text,
                    tax_text,
                    paid_text,
                    receiver,
                    receiver_acc,
                    location,
                    formatted,
                )) 

        if os.path.exists(workbook_name):
            # print(f"The file '{workbook_name}' exists.")
            existing_df = pd.read_excel(workbook_name)
            new_df = pd.DataFrame(result_array, columns=headers_to_check)
            result_df = pd.concat([existing_df, new_df], ignore_index=True)
            result_df.to_excel(workbook_name, index=False)

        else:
            # print(f"The file '{workbook_name}' does not exist.")
            df = pd.DataFrame(result_array, columns=headers_to_check)
            df.to_excel(workbook_name, index=False)

    def save_information_workbook_16a1(self, code, number, unit, receiver, sender_acc, receiver_acc, location, formatted, contents, money, workbook_name):
        headers_to_check = [
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
        
        result_array = []
        for content, amount in zip(contents[1:], money[1:]):
            content_text = content.text
            money_text = float(amount.text.replace(".", ""))
            result_array.append((
                    code,
                    number,
                    unit,
                    sender_acc,
                    content_text,
                    money_text,
                    receiver,
                    receiver_acc,
                    location,
                    formatted,
                )) 
       

        if os.path.exists(workbook_name):
            # print(f"The file '{workbook_name}' exists.")
            existing_df = pd.read_excel(workbook_name)
            new_df = pd.DataFrame(result_array, columns=headers_to_check)
            result_df = pd.concat([existing_df, new_df], ignore_index=True)
            result_df.to_excel(workbook_name, index=False)

        else:
            # print(f"The file '{workbook_name}' does not exist.")
            df = pd.DataFrame(result_array, columns=headers_to_check)
            df.to_excel(workbook_name, index=False)

    def save_information_workbook_07(self, code, number, unit, code_unit, bill_code, bill_date, dos_code, dos_date, NDKT_code, contents, money, date, workbook_name): 
        headers_to_check = [
            "Mã",
            "Số",
            "Đơn vị sử dụng Ngân sách",
            "Mã đơn vị",
            "Số hóa đơn",
            "Ngày hóa đơn",
            "Số chứng từ",
            "Ngày chứng từ",
            "Mã NDKT",
            "Nội Dung",
            "Số Tiền",
            "Ngày"
        ]
        
        result_array = []
        

        for chil_bill_code, chil_bill_date, chil_dos_code, chil_dos_date, chil_NDKT_code, content, amount in zip(bill_code, bill_date, dos_code, dos_date, NDKT_code, contents, money):
            result_array.append((
                    code,
                    number,
                    unit,
                    code_unit,
                    chil_bill_code,
                    chil_bill_date,
                    chil_dos_code,
                    chil_dos_date,
                    chil_NDKT_code,
                    content,
                    amount,
                    date,
                ))  

        if os.path.exists(workbook_name):
            # print(f"The file '{workbook_name}' exists.")
            existing_df = pd.read_excel(workbook_name)
            new_df = pd.DataFrame(result_array, columns=headers_to_check)
            result_df = pd.concat([existing_df, new_df], ignore_index=True)
            result_df.to_excel(workbook_name, index=False)

        else:
            df = pd.DataFrame(result_array, columns=headers_to_check)
            df.to_excel(workbook_name, index=False)


##################### End common ################################

    def test_process_page(self):
        self.driver.get("file:///F:/02Source/02Training/KBST/khobac-crawler/types/kbst.html")
        self.driver.get("file:///F:/02Source/02Training/KBST/khobac-crawler/types/16a1.html")
        self.driver.get("file:///F:/02Source/02Training/KBST/khobac-crawler/types/16a2.html")
        # self.driver.get("file:///F:/02Source/02Training/KBST/khobac-crawler/types/16c.html")
        # self.driver.get("file:///F:/02Source/02Training/KBST/khobac-crawler/types/07.html")
        # self.driver.get("file:///F:/02Source/02Training/KBST/khobac-crawler/types/0701.html")

        code_value = self.get_content_by_key_search("Mẫu số")

        if code_value == constants.MAU_SO_16a1:
            return self.process_model_16a1(code_value)

        elif code_value == constants.MAU_SO_16a2:
            return self.process_model_16a2(code_value)

        elif code_value == constants.MAU_SO_16c:
            return self.process_model_16c(code_value)

        elif code_value == constants.MAU_SO_07:
            return self.process_model_07(code_value)

        else:
            return "Invalid case" 

####################### 16a1 ##############################
    def process_model_16a1(self, code):
        number = self.get_content_by_key_search("Số:")
        unit = self.get_content_by_key_search("Đơn vị rút dự toán:")
        receiver = self.get_content_by_key_search("Đơn vị nhận tiền:")
        sender_acc = self.convert_to_string(self.get_bank_accounts_16a1()[0])
        receiver_acc = self.convert_to_string(self.get_bank_accounts_16a1()[1])
        location = self.get_content_by_key_search("Tại KBNN (NH):")
        formatted = self.get_date()
        contents = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_0_"]')
        money = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_soTien_"]')
        workbook_name = "results/16a1.xlsx"

        return self.save_information_workbook_16a1(code, number, unit, receiver, sender_acc, receiver_acc, location, formatted, contents, money, workbook_name)
####################### 16a1 ##############################

    
####################### Function of 16a2 ######################
    def process_model_16a2(self, code):
        number = self.get_content_by_key_search("Số:")
        unit = self.get_content_by_key_search("Đơn vị rút dự toán:")
        receiver = self.get_content_by_key_search("Đơn vị nhận tiền:")
        sender_acc = self.convert_to_string(self.get_bank_accounts_16a1()[0])
        receiver_acc = self.convert_to_string(self.get_bank_accounts_16a1()[1])
        contents = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_0_"]')
        total = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_5_"]')
        tax = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_6_"]')
        paid = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_7_"]')
        location = self.get_content_by_key_search("Tại KBNN (NH):")
        formatted = self.get_date()

        workbook_name = "results/16a2.xlsx"

        return self.save_information_workbook_16a2_16c(code, number, unit, sender_acc, receiver_acc, contents, total, tax, paid, receiver, location, formatted, workbook_name)

####################### End 16a2 ##############################


####################### Start 16c ##############################
    def get_paying_unit_16c(self):
        unit = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Đơn vị trả tiền:')]")
        unit_value = self.extract_text(unit)
        unit_value = unit_value.replace("Đơn vị trả tiền:", "")
        return self.trim_text(unit_value)

    
    def get_address_of_treasury_16c(self):
        location = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Tại Kho bạc Nhà nước (NH):')]")
        location_value = self.extract_text(location)
        substring_to_remove = "Tại Kho bạc Nhà nước (NH):"
        location_value = location_value.replace(substring_to_remove, "")
        return self.trim_text(location_value)

    def process_model_16c(self, code):
        number = self.get_content_by_key_search("Số:")
        unit = self.get_content_by_key_search("Đơn vị trả tiền:")
        receiver = self.get_content_by_key_search("Đơn vị nhận tiền:")
        sender_acc = self.convert_to_string(self.get_bank_accounts_16a1()[0])
        receiver_acc = self.convert_to_string(self.get_bank_accounts_16a1()[1])
        contents = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_0_"]')
        total = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_3_"]')
        tax = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_4_"]')
        paid = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_5_"]')
        location = self.get_address_of_treasury_16c()
        date = self.get_date()
        workbook_name = "results/16c.xlsx"

        return self.save_information_workbook_16a2_16c(code, number, unit, sender_acc, receiver_acc, contents, total, tax, paid, receiver, location, date, workbook_name)
####################### End 16c ##############################

######################### 07 #################################
    def process_model_07(self, code):
        number = self.get_content_by_key_search("Số:")
        unit = self.get_content_by_key_search("Đơn vị sử dụng Ngân sách:")
        code_unit = self.convert_to_string(self.get_content_by_key_search("Mã đơn vị:"))
        date = self.get_date()

        # Find all div elements inside elements with class 'jrtableframe'
        elements = self.driver.find_elements("css selector", ".jrtableframe div")

        i = 16
        bill_code = []
        bill_date = []
        dos_code = []
        dos_date = []
        NDKT_code = []
        money = []
        contents = []

        while i < len(elements) and i + 12 < len(elements):
            bill_code.append(self.convert_to_string(elements[i].text))
            bill_date.append(elements[i+1].text)
            dos_code.append(self.convert_to_string(elements[i+2].text))
            dos_date.append(elements[i+3].text)
            NDKT_code.append(self.convert_to_string(elements[i+4].text))
            subdiv = elements[i+8].find_elements(By.XPATH, './/div')
            money_text = subdiv[0].text.replace(".", "")
            money.append(money_text)
            contents.append(elements[i+5].text)
            i += 12
        workbook_name = "results/07.xlsx"


        return self.save_information_workbook_07(code, number, unit, code_unit, bill_code, bill_date, dos_code, dos_date, NDKT_code, contents, money, date, workbook_name)       
######################### 07 #################################

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
