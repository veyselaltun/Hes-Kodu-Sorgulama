from selenium import webdriver
from playsound import playsound
import time
import pymysql
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# veri tabanına ekleme
browser = webdriver.Chrome()
def girisyap():
    tc = input("Tc Kimlik Numaranız: ") 
    sifre = input("E-Devlet Şifreniz ")
    browser.get("https://giris.turkiye.gov.tr/Giris/")

    tckimlik = browser.find_element_by_name("tridField")
    sifre = browser.find_element_by_name("egpField")
    tckimlik.send_keys(tc)
    sifre.send_keys(sifre)
    giris_yap = browser.find_element_by_xpath(
        "/html/body/div[1]/main/section[2]/form/div[2]/input[4]")
    giris_yap.click()
    time.sleep(2)

girisyap()

aa = 1

connection = pymysql.connect(
    host="localhost", user="root", passwd="", database="yenigelenhes")
cursor = connection.cursor()
#aa Muhabbetini sorgulamayalım :D
while (aa < 2):

    try:
        if cursor.execute("SELECT webhes FROM sonhes WHERE status = 0 ORDER BY id DESC"):
            sonhes = cursor.fetchone()
            print(sonhes)
            assert isinstance(sonhes, object)
            if sonhes:
                browser.get(
                    "https://www.turkiye.gov.tr/saglik-bakanligi-hes-kodu-sorgulama")
                hes_kodu = browser.find_element_by_name("hes_kodu")
                hes_kodu.send_keys(sonhes)
                sorgula = browser.find_element_by_xpath(
                    "//*[@id='contentStart']/div[3]/form/div/input[1]")
                browser.execute_script("arguments[0].click();", sorgula)
                ciktiyi_bekle = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "compact")))
                hessonuc = browser.find_element_by_xpath(
                    "//*[@id='contentStart']/div/dl/dd[3]").text
                sql = "UPDATE sonhes SET status = %s, risk = %s WHERE webhes = %s"  
                val = (1, hessonuc, sonhes)
                cursor.execute(sql, val)
                connection.commit()
                if hessonuc == "Riskli":
                    print("Riskli")
                else:
                    print(" Hes Kodu Kontrol Edildi, Veri Tabanına Eklendi.")
        else:

            connection.commit()

    except Exception as e:
        errortxt = open("errortxt.txt", "w")
        errortxt.write(str(e))
        errortxt.close()
        hatayiac = open("errortxt.txt")
        a = hatayiac.readline()
        b = hatayiac.readline()
        c= "Message:"
        if b:
            print("Çıkış yapılmış, Tekrar giriş yapılıyor...")
            girisyap()
        elif c:
            sql = "UPDATE sonhes SET status = %s, risk = %s WHERE webhes = %s"
            val = (1, "Gecersiz", sonhes)
            cursor.execute(sql, val)
            print("Geçersiz Hes kodu girildi.")
            connection.commit()
            playsound('3.mp3')
            
        else:
            print("Teknik Aksaklık Mevcut")