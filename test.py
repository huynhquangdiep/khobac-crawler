import time
import os
import pandas as pd 
import unittest
import openpyxl
from selenium.webdriver.common.by import By
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import constants
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
import csv
from selenium.common.exceptions import NoSuchElementException

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        firefox_options = Options()
        # firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.maximize_window()

        # Define folder paths
        result_folder_path = os.path.join("results", constants.YEAR_MONTH_FOLDER)
        errors_folder_path = os.path.join("results", constants.YEAR_MONTH_FOLDER, "errors")  
        screenshot_folder_path = "errors/screenshots"  # Assuming you want it in the current working directory

        # Combine the current working directory with the screenshot folder
        screenshot_folder_path = os.path.join(os.getcwd(), screenshot_folder_path)

        # Create directories if they do not exist
        for folder_path in [result_folder_path, errors_folder_path, screenshot_folder_path]:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

###################### common ###############################
    def extract_text(self, element):
        return element.text
    
    def convert_to_string(self, string): 
        return "`" + string
    
    def trim_text(self, element):
        element = element.lstrip()
        element = element.rstrip()
        return element

    def extract_date(self, text):
        try:
            pattern = r"Ngày?\s+(\d{2})?\s+tháng?\s+(\d{2})?\s+năm?\s+(\d{4})(?:\s+|$)"
            match = re.search(pattern, text)
            if match:
                day, month, year = match.groups()
                return f"{day}/{month}/{year}"
            return ""
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def get_content_by_key_search(self, key_search):
        try:
            unit = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{key_search}')]")
            unit_value = self.extract_text(unit)
            unit_value = unit_value.replace(key_search, "")
            return self.trim_text(unit_value)
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def get_bank_accounts_16a1(self):
        try:
            bank_accounts = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Tài khoản: ')]")
            sender_acc, receiver_acc = [self.extract_text(b) for b in bank_accounts]
            sender_acc = sender_acc.replace("Tài khoản:", "").replace(".", "")
            sender_acc = self.trim_text(sender_acc) 
            sender_acc = str(sender_acc)

            receiver_acc = receiver_acc.replace("Tài khoản:", "").replace(".", "")
            receiver_acc = self.trim_text(receiver_acc)
            receiver_acc = str(receiver_acc)
            return sender_acc, receiver_acc

        except Exception as e:
            print(f"An error occurred: {e}")
    
    def get_date(self):
        try:
            dates = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Ngày')]")

            formatted_date = ""
            for date in dates:
                formatted_date = self.extract_date(date.text)
                if formatted_date:
                    break

            return formatted_date
        except Exception as e:
            print(f"An error occurred: {e}")

    def export_file(self, workbook_name, headers_to_check, result_array):
        if os.path.exists(workbook_name):
            existing_df = pd.read_excel(workbook_name)
            new_df = pd.DataFrame(result_array, columns=headers_to_check)
            result_df = pd.concat([existing_df, new_df], ignore_index=True)

            return result_df.to_excel(workbook_name, index=False)

        else:
            df = pd.DataFrame(result_array, columns=headers_to_check)
            return df.to_excel(workbook_name, index=False)

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
            
        return self.export_file(workbook_name, headers_to_check, result_array)

    def save_information_workbook_16a1_16c1(self, code, number, unit, receiver, sender_acc, receiver_acc, location, formatted, contents, money, workbook_name):
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
       
        return self.export_file(workbook_name, headers_to_check, result_array)

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
                    self.convert_to_string(code),
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
            
        return self.export_file(workbook_name, headers_to_check, result_array)
    
##################### End common ################################
    
    
    

####################### 16a1 ##############################
    def process_model_16a1(self, code):
        number = self.get_content_by_key_search("Số:")
        unit = self.get_content_by_key_search("Đơn vị rút dự toán:")
        receiver = self.get_content_by_key_search("Đơn vị nhận tiền:")
        sender_acc = self.convert_to_string(self.get_bank_accounts_16a1()[0])
        receiver_acc = self.convert_to_string(self.get_bank_accounts_16a1()[1])
        location = self.get_content_by_key_search("Tại KBNN (NH):")
        date = self.get_date()
        contents = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_0_"]')
        money = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_soTien_"]')
        workbook_name = "results/" + constants.YEAR_MONTH_FOLDER + "/16a1.xlsx"

        return self.save_information_workbook_16a1_16c1(code, number, unit, receiver, sender_acc, receiver_acc, location, date, contents, money, workbook_name)
    
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
        date = self.get_date()
        workbook_name = "results/" + constants.YEAR_MONTH_FOLDER +  "/16a2.xlsx"

        return self.save_information_workbook_16a2_16c(code, number, unit, sender_acc, receiver_acc, contents, total, tax, paid, receiver, location, date, workbook_name)
####################### End 16a2 ##############################

####################### Start 16c ##############################
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
        location = self.get_content_by_key_search("Tại Kho bạc Nhà nước (NH):")
        date = self.get_date()
        workbook_name = "results/" + constants.YEAR_MONTH_FOLDER +  "/16c.xlsx"

        return self.save_information_workbook_16a2_16c(code, number, unit, sender_acc, receiver_acc, contents, total, tax, paid, receiver, location, date, workbook_name)
####################### End 16c ##############################

####################### Start 16c1 ##############################
    def process_model_16c1(self, code):
        number = self.get_content_by_key_search("Số:")
        unit = self.get_content_by_key_search("Đơn vị trả tiền:")
        receiver = self.get_content_by_key_search("Đơn vị nhận tiền:")
        sender_acc = self.convert_to_string(self.get_bank_accounts_16a1()[0])
        receiver_acc = self.convert_to_string(self.get_bank_accounts_16a1()[1])
        contents = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_0_"]')
        money = self.driver.find_elements(By.CSS_SELECTOR, '.jrcel[class*="cel_3_"]')
        location = self.get_content_by_key_search("Tại Kho bạc Nhà nước (NH):")
        date = self.get_date()
        workbook_name = "results/" + constants.YEAR_MONTH_FOLDER +  "/16c1.xlsx"

        return  self.save_information_workbook_16a1_16c1(code, number, unit, receiver, sender_acc, receiver_acc, location, date, contents, money, workbook_name)
####################### End 16c1 ##############################

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
        workbook_name = "results/" + constants.YEAR_MONTH_FOLDER +   "/07.xlsx"

        return self.save_information_workbook_07(code, number, unit, code_unit, bill_code, bill_date, dos_code, dos_date, NDKT_code, contents, money, date, workbook_name)       
######################### 07 #################################

######################### Main #################################
    def login(self):
        self.driver.get(constants.LOGIN_URL)
        # time.sleep(5)
        self.wait_for_element(By.XPATH, '//input[@id="r1:0:pt1:sf1:it1::content"]')
        self.enter_text(By.XPATH, '//input[@id="r1:0:pt1:sf1:it1::content"]', constants.USER_NAME)
        self.enter_text(By.XPATH, '//input[@id="r1:0:pt1:sf1:it2::content"]', constants.PASSWORD)
        self.click_element(By.XPATH, '//button[@id="r1:0:pt1:sf1:cbLogin"]')

        self.driver.get(constants.URL_AFTER_LOGIN)

        self.click_element(By.XPATH, '//button[@id="pt1:r1:0:cb3"]')
        self.wait_for_element(By.XPATH, '//input[@id="pt1:r1:0:it12::content"]')
        self.enter_text(By.XPATH, '//input[@id="pt1:r1:0:it12::content"]', constants.YEAR)
        self.enter_text(By.XPATH, '//input[@id="pt1:r1:0:it10::content"]', constants.YEAR_MONTH)

        time.sleep(20) #TODO = 100 seconds
    
        self.click_element(By.XPATH, '//button[@id="pt1:r1:0:cb4"]')
        # time.sleep(10) #TODO = 100 seconds 

    def wait_for_element(self, by, locator):
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((by, locator)))

    def enter_text(self, by, locator, text):
        element = self.driver.find_element(by, locator)
        element.send_keys(text)

    def click_element(self, by, locator):
        element = self.driver.find_element(by, locator)
        element.click()
        time.sleep(10)


    def get_list_href(self):
        links = self.driver.find_elements(By.XPATH, '//a[@class="xfh"]')
        hrefs = []
        i = 1
        while i < len(links) and i + 6 <= len(links): 
            hrefs.append(links[i])
            i = i + 6
        return hrefs

    def handle_error(self): 
        self.driver.refresh()
        time.sleep(10) #TODO = 1000


    def handle_click_event(self, items):
        i = 0
        j = 0
        while i < len(items):
            try:
                items = self.get_list_href()# Remove blocking and modal glass panes if they exist

                for class_name in ['AFBlockingGlassPane', 'AFModalGlassPane']:
                    try:
                        element = self.driver.find_element(By.XPATH, f'//div[@class="{class_name}"]')
                        self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
                    except NoSuchElementException:
                        pass

                item_id = items[i].get_attribute("id")

                # Find the element you want to wait for
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, item_id))
                )

                items[i].click()
                time.sleep(5)
                self.handle_iframe(i, j)
                time.sleep(5)
                i += 1  # Increment i for the next iteration

                if (i)  == len(items):
                    next_button = self.driver.find_element(By.XPATH, '//a[@id="pt1:r1:0:cl1"]')

                    if 'p_AFDisabled' in next_button.get_attribute('class'):
                        break  # Exit the loop if the next button is disabled
                    else:
                        i = 0  # Reset i to 0 for the next iteration
                        j = j + 1
                        print("Move to next page", j)
                        next_button.click()
                        time.sleep(5)

            except Exception as e:
                print(f"Loop: {e}")
                self.handle_error()

    def handle_close_modal(self):
        close = self.driver.find_element(By.XPATH, '//div[@id="ctb1"]//a')
        return close.click()

    def handle_iframe(self, i, j):
        self.driver.switch_to.frame(1)
        try: 
            code_value = self.get_content_by_key_search("Mẫu số")
        except Exception as e:
            print(f"Loop: {e}")

        if code_value in [constants.MAU_SO_04a, constants.MAU_SO_04b, constants.MAU_SO_05]:
            print("04 or 05")
            time.sleep(5)
            self.handle_close_modal()
            return self.driver.switch_to.parent_frame()
        
        elif code_value == constants.MAU_SO_16a1:
            self.process_model_16a1(code_value)
        
        elif code_value == constants.MAU_SO_16a2:
            self.process_model_16a2(code_value)

        elif code_value == constants.MAU_SO_16c:
            self.process_model_16c(code_value)
        
        elif code_value == constants.MAU_SO_16c1:
            self.process_model_16c1(code_value)

        elif code_value == constants.MAU_SO_07:
            self.process_model_07(code_value)

        else:
            print("Invalid case")
            index = i + 1 
            result_array = [(index, j, code_value)]
            headers_to_check = ["ID", "Page", "Code"]
            self.export_file("errors/output.xlsx", headers_to_check, result_array)

        time.sleep(5)
        # self.take_screen_shot(i)
        self.handle_close_modal()
        return self.driver.switch_to.parent_frame()

    # def take_screen_shot(self, i):
    #     self.driver.save_screenshot('errors/screenshots/' + str(i) + ".png")
        
    def test_process_page(self):
        self.login()
        hrefs = self.get_list_href()
        self.handle_click_event(hrefs)

######################### End #################################


    # def tearDown(self):
        # self.driver.quit()


if __name__ == "__main__":
    unittest.main()
