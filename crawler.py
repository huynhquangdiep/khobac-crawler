import json
import time
import os
import pandas as pd 
import unittest
from selenium.webdriver.common.by import By
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import constants
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        firefox_options = Options()
        # firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.maximize_window()

###################### common ###############################
    def extract_text(self, element):
        return element.text
    
    def clean_string(self, string):
        return string.replace('\n', ' ')
    
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

    def get_signature_infor(self):
        responses = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Người ký:')]")
        array = []
        for response in responses:
            array.append(response.text)

        return array
    
    def get_temp_docs(self, string):
        # Define the pattern for matching the desired substring
        pattern = r"(\d{6}_\d{7}_\d{7})"

        # Use re.search to find the pattern in the string
        match = re.search(pattern, string)

        # If there's a match, print the extracted substring
        if match:
            return match.group(1)
        
        return False
            
##################### End common ################################

######################### 07 #################################
    def process_model_07(self, code):
        try:
            invoice_id = self.get_content_by_key_search("Số:")
            parts = invoice_id.split()
            sub_invoice_id = parts[-1]
            organization = self.get_content_by_key_search("Đơn vị sử dụng Ngân sách:")
            organization_code = self.get_content_by_key_search("Mã đơn vị:")
            organization_received = self.get_content_by_key_search("Đơn vị nhận tiền:")
            signature_infor = self.get_signature_infor()
            elements = self.driver.find_elements("css selector", ".jrtableframe div")
            temp_payment_07 = self.get_temp_docs(self.get_content_by_key_search("(Kèm theo Giấy rút dự toán, Ủy nhiệm chi, Giấy đề nghị thanh toán tạm ứng số:"))
        
            i = 16
            data_response = []
            while i < len(elements) and i + 12 < len(elements):
                subdiv = elements[i + 8].find_elements(By.XPATH, './/div')
                money_text = subdiv[0].text.replace(".", "")
                money_value = int(money_text) if money_text.isdigit() else None  # Convert money to an integer if it's a digit
                
                content = self.clean_string(elements[i + 5].text + " " + elements[i].text)
                NDKT_code = elements[i+4].text if elements != [] else ""
                economic_code = elements[i+6].text if elements != [] else ""
                NSNN_code = elements[i+7].text if elements != [] else ""
                
                data = {
                    "id": invoice_id + content + NDKT_code + economic_code + NSNN_code,
                    "code_invoice": code,
                    "invoice_id": self.clean_string(invoice_id),
                    "sub_invoice_id": sub_invoice_id, 
                    "temp_payment_07": temp_payment_07,
                    "organization": organization,
                    "organization_code": organization_code,
                    "bill_code":elements[i].text,
                    "bill_date":elements[i + 1].text,
                    "NDKT_code":NDKT_code,
                    "economic_code":economic_code,
                    "NSNN_code":NSNN_code,
                    "content": content,
                    "money":money_value,
                    "organization_received": organization_received,
                    "bank_account": "",
                    "location": "",
                    "signer_1": signature_infor[0], 
                    "signer_2": signature_infor[1],
                    "signer_3": signature_infor[2],
                    "signer_4": signature_infor[3],
                }
                i += 12
                data_response = json.dumps(data, ensure_ascii=True)
                self.store_data(data_response)

            return True
        
        except Exception as e:
            print(f"An error occurred: {e}")

    def process_model(self, code, content_selector, money_selector, organization_search_key, location_search_key):
        invoice_id = self.get_content_by_key_search("Số:")
        parts = invoice_id.split()
        sub_invoice_id = parts[-1]
        signature_infor = self.get_signature_infor()
        invoice_id = self.get_content_by_key_search("Số:")
        content_arr = self.driver.find_elements(By.CSS_SELECTOR, content_selector)
        money = self.driver.find_elements(By.CSS_SELECTOR, money_selector)
        organization = self.get_content_by_key_search(organization_search_key)
        organization_received = self.get_content_by_key_search("Đơn vị nhận tiền:")
        bank_account = self.get_bank_accounts_16a1()[1]
        location = self.get_content_by_key_search(location_search_key)

        NDKT_code_arr = []
        chapter_code_arr = []
        economic_code_arr = []
        NSNN_code_arr = []

        if code == constants.MAU_SO_16a1 or code == constants.MAU_SO_16a2: 
            NDKT_code_arr = self.driver.find_elements(By.CSS_SELECTOR, ".jrcel[class*='cel_1_']")
            chapter_code_arr = self.driver.find_elements(By.CSS_SELECTOR, ".jrcel[class*='cel_2_']")
            economic_code_arr = self.driver.find_elements(By.CSS_SELECTOR, ".jrcel[class*='cel_3_']")
            NSNN_code_arr = self.driver.find_elements(By.CSS_SELECTOR, ".jrcel[class*='cel_4_']")

        elif code == constants.MAU_SO_16c:
            NSNN_code_arr = self.driver.find_elements(By.CSS_SELECTOR, ".jrcel[class*='cel_1_']")
            content_arr = content_arr[:-1]
            money = money[:-1]
         
        elif code == constants.MAU_SO_16c1:
            content_arr = content_arr[:-1]
            money = money[:-1]
 
        i = 1
        while i < len(content_arr):

            content = self.clean_string(content_arr[i].text)
            NDKT_code = NDKT_code_arr[i].text if NDKT_code_arr != [] else ""
            chapter_code = chapter_code_arr[i].text if chapter_code_arr != [] else ""
            economic_code = economic_code_arr[i].text if economic_code_arr != [] else ""
            NSNN_code = NSNN_code_arr[i].text if NSNN_code_arr != [] else ""

            data = {
                "id": invoice_id + content + NDKT_code + economic_code + NSNN_code,
                "code_invoice": code,
                "invoice_id": self.clean_string(invoice_id),
                "sub_invoice_id": sub_invoice_id, 
                "organization": organization,
                "organization_code": None,
                "bill_code":None,
                "bill_date":None,
                "NDKT_code": NDKT_code,
                "chapter_code": chapter_code,
                "economic_code": economic_code,
                "NSNN_code": NSNN_code,
                "content":content,
                "money":money[i].text.replace(".", ""),
                "organization_received": organization_received,
                "bank_account": bank_account,
                "location": location,
                "signer_1": signature_infor[0], 
                "signer_2": signature_infor[1],
                "signer_3": signature_infor[2],
                "signer_4": signature_infor[3],
            }
            # output.append(data)
            i = i + 1
            data_response = json.dumps(data, ensure_ascii=True)
            self.store_data(data_response)
        # return True

    def  store_data(self, data):
        url = constants.API_URL
        # Set the headers (assuming 'ContentType' is 'application/json')
        headers = {'Content-Type': 'application/json'}
        # Send the POST request
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx status codes)
            # Process the response content if needed
        except requests.exceptions.RequestException as e:
            print(f"Error making the request: {e}")

        # Check the response
        if response:
            print("*" * 20)
            print("Request was successful!")
            print("*" * 20)
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)  # Print the response content for debugging

######################### Main #################################
    def login(self):
        self.driver.get(constants.LOGIN_URL)
        time.sleep(5)
        self.wait_for_element(By.XPATH, '//input[@id="r1:0:pt1:sf1:it1::content"]')
        self.enter_text(By.XPATH, '//input[@id="r1:0:pt1:sf1:it1::content"]', constants.USER_NAME)
        self.enter_text(By.XPATH, '//input[@id="r1:0:pt1:sf1:it2::content"]', constants.PASSWORD)
        self.click_element(By.XPATH, '//button[@id="r1:0:pt1:sf1:cbLogin"]')
        self.driver.get(constants.URL_AFTER_LOGIN)
        self.click_element(By.XPATH, '//button[@id="pt1:r1:0:cb3"]')
        self.wait_for_element(By.XPATH, '//input[@id="pt1:r1:0:it12::content"]')
        self.enter_text(By.XPATH, '//input[@id="pt1:r1:0:it12::content"]', constants.YEAR)
        self.enter_text(By.XPATH, '//input[@id="pt1:r1:0:it10::content"]', constants.YEAR_MONTH)

        # Da thanh toan 
        self.click_element(By.XPATH, '//input[@id="pt1:r1:0:smc2::content"]') # Trạng thái:	
        self.click_element(By.XPATH, '//input[@id="pt1:r1:0:smc2::saId"]')   # Tat ca
        self.click_element(By.XPATH, '//input[@_adftrueval="Đã thanh toán"]') # Đã thanh toán 
        self.click_element(By.XPATH, '//input[@id="pt1:r1:0:smc2::content"]') # Thoat 
        self.click_element(By.XPATH, '//input[@id="pt1:r1:0:smc1::content"]') # Ds chứng từ
        self.click_element(By.XPATH, '//input[@id="pt1:r1:0:smc1::saId"]') # Tat ca
        self.click_element(By.XPATH, '//input[@_adftrueval="C2-02a/NS - Giấy rút dự toán Ngân sách Nhà nước"]')
        self.click_element(By.XPATH, '//input[@_adftrueval="C2-02b/NS - Giấy rút dự toán Ngân sách Nhà nước(Nộp thuế)"]')
        self.click_element(By.XPATH, '//input[@_adftrueval="C4-02a/KB - Ủy nhiệm chi"]')
        self.click_element(By.XPATH, '//input[@_adftrueval="C4-02c/KB - Ủy nhiệm chi"]')
        self.click_element(By.XPATH, '//input[@_adftrueval="M01 - Bảng kê chứng từ thanh toán/tạm ứng"]')

        time.sleep(5) #TODO = 100 seconds
    
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
        time.sleep(3)


    def get_list_href(self):
        links = self.driver.find_elements(By.XPATH, '//a[@class="xfh"]')
        hrefs = []
        i = 1
        while i < len(links) and i + 6 <= len(links): 
            hrefs.append(links[i])
            i = i + 6
        return hrefs

    def handle_error(self): 
        print("Reload page")
        self.driver.refresh()
        time.sleep(4)

    def remove_unnecessary_element(self):
        for class_name in ['AFBlockingGlassPane', 'AFModalGlassPane']:
            try:
                element = self.driver.find_element(By.XPATH, f'//div[@class="{class_name}"]')
                self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
            except NoSuchElementException:
                pass

    def handle_click_event(self, items):
        i = 0
        j = 0
        while i < len(items):
            try:
                items = self.get_list_href()# Remove blocking and modal glass panes if they exist

                # Remove blocking and modal glass panes if they exist
                self.remove_unnecessary_element()

                item_id = items[i].get_attribute("id")

                # Find the element you want to wait for
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, item_id))
                )

                items[i].click()
                time.sleep(2)
                self.handle_iframe(i, j)
                time.sleep(2)
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
        try: 
            self.driver.switch_to.frame(1)
            code_value = self.get_content_by_key_search("Mẫu số")
        except Exception as e:
            print(f"Loop: {e}")
            self.handle_error()

        if code_value in [constants.MAU_SO_04a, constants.MAU_SO_04b, constants.MAU_SO_05]:
            print("04 or 05")
            time.sleep(2)
            self.handle_close_modal()
            return self.driver.switch_to.parent_frame()
        
        elif code_value == constants.MAU_SO_16a1:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_soTien_"]', "Đơn vị rút dự toán:", "Tại KBNN (NH):")
        
        elif code_value == constants.MAU_SO_16a2:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_5_"]', "Đơn vị rút dự toán:", "Tại KBNN (NH):")

        elif code_value == constants.MAU_SO_16c:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_3_"]', "Đơn vị trả tiền:", "Tại Kho bạc Nhà nước (NH):")
        
        elif code_value == constants.MAU_SO_16c1:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_3_"]', "Đơn vị trả tiền:", "Tại Kho bạc Nhà nước (NH):")

        elif code_value == constants.MAU_SO_07:
            self.process_model_07(code_value)

        else: # TODO not save the code yet
            print("Invalid case")
            index = i + 1 
            result_array = [(index, j, code_value)]
            headers_to_check = ["ID", "Page", "Code"]
            self.export_file("errors/output.xlsx", headers_to_check, result_array)

        time.sleep(5)
        self.handle_close_modal()
        return self.driver.switch_to.parent_frame()
    
    def internal_testing(self): 
        # self.driver.get("file:///F:/01Project/03KhoBac/khobac-crawler/types/07.html")
        # self.driver.get("file:///F:/01Project/03KhoBac/khobac-crawler/types/16a1.html")
        # self.driver.get("file:///F:/01Project/03KhoBac/khobac-crawler/types/16a2.html")
        # self.driver.get("file:///F:/01Project/03KhoBac/khobac-crawler/types/16c.html")
        # self.driver.get("file:///F:/01Project/03KhoBac/khobac-crawler/types/16c1.html")

        self.driver.get("file:///D:/01Projects/03KhoBac/khobac-crawler/types/16a2.html")

        
        
        
    
        code_value = self.get_content_by_key_search("Mẫu số")
        print(code_value)

        if code_value == constants.MAU_SO_16a1:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_soTien_"]', "Đơn vị rút dự toán:", "Tại KBNN (NH):")
        
        elif code_value == constants.MAU_SO_16a2:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_5_"]', "Đơn vị rút dự toán:", "Tại KBNN (NH):")
        elif code_value == constants.MAU_SO_16c:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_3_"]', "Đơn vị trả tiền:", "Tại Kho bạc Nhà nước (NH):")
        
        elif code_value == constants.MAU_SO_16c1:
            self.process_model(code_value, '.jrcel[class*="cel_0_"]', '.jrcel[class*="cel_3_"]', "Đơn vị trả tiền:", "Tại Kho bạc Nhà nước (NH):")
        elif code_value == constants.MAU_SO_07:
            self.process_model_07(code_value)
        print('ok')

    def test_process_page(self):
        self.internal_testing()

        # self.login()
        # hrefs = self.get_list_href()
        # self.handle_click_event(hrefs)

######################### End #################################


if __name__ == "__main__":
    unittest.main()
