
import subprocess
import time
import os
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------

CHROMEDRIVER_PATH = "C:\\chromedriver\\chromedriver.exe"  # o la ruta donde lo tengas
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
RUTA = r"C:\Users\kemie\OneDrive\Desktop\WebScrapingPy" # C:\Users\kemie\OneDrive\Documentos\AutoHotkey\TEST"
# Rutas de la carpeta de LOGS
LOG = r"C:\Users\kemie\OneDrive\Documentos\Afiliados\Logs"
# Rutas de Chrome
PROFILE_DIR= R"C:\Users\kemie\AppData\Local\Google\Chrome\User Data\Default" #"C:\Users\Juan Rivera\AppData\Local\Google\Chrome\User Data\Default"

PYTHON_EXE = r"C:\Users\kemie\AppData\Local\Programs\Python\Python313\python.exe"
os.makedirs(LOG, exist_ok=True)


LOG_GENERAL = os.path.join(LOG, "log_ejecucion.txt")

CHAT_NOTIFICACION = "3342470959"

scripts = [
    "Scraping Productivo Selectivo - Especiales.py",
    "Scraping Productivo - Page 2.py",
    "Scraping Productivo.py",
    # "Scraping Productivo Selectivo - Perfumeria.py",
    # "Scraping Productivo Selectivo - Moda Belleza.py",
    # "Scraping Productivo Selectivo - Muebles.py",
    # "Scraping Productivo Selectivo - Hogar.py",
    # "Scraping Productivo Selectivo - Tecnologia.py"
    # "Scraping Productivo Selectivo - Juguetes.py",
    # "Scraping Productivo Selectivo - Herramientas.py",
    # "Scraping Productivo Selectivo - Belleza y Cuidado Personal.py",
]

# ----------------------------------------------------------
# LOG
# ----------------------------------------------------------
def registrar_log(texto):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha}] {texto}\n"
    with open(LOG_GENERAL, "a", encoding="utf-8") as f:
        f.write(linea)
    print(linea.strip())


# ----------------------------------------------------------
# KILL CHROME
# ----------------------------------------------------------
def matar_chrome():
    os.system("taskkill /F /IM chrome.exe >NUL 2>NUL")
    os.system("taskkill /F /IM chromedriver.exe >NUL 2>NUL")
    time.sleep(3)  # PRIMO


# ----------------------------------------------------------
# WHATSAPP VIA SELENIUM
# ----------------------------------------------------------
def notificar_whatsapp(driver, mensaje):
    try:
        wait = WebDriverWait(driver, 23)

        driver.get("https://web.whatsapp.com")
        time.sleep(11)

        search = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]')))
        search.click()
        search.send_keys(Keys.CONTROL, 'a')
        search.send_keys(CHAT_NOTIFICACION)
        search.send_keys(Keys.ENTER)
        time.sleep(3)

        box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
        box.click()
        box.send_keys(mensaje)
        time.sleep(2)
        box.send_keys(Keys.ENTER)

        print("Notificación enviada por WhatsApp")

    except Exception as e:
        print(f"No se pudo enviar notificación: {e}")


# ----------------------------------------------------------
# INICIAR SELENIUM
# ----------------------------------------------------------
def iniciar_driver():
    print("Configurando WebDriver...")

    service = Service(CHROMEDRIVER_PATH)
    options = Options()

    options.add_argument(f'--user-data-dir={PROFILE_DIR}')
    options.binary_location = CHROME_PATH
    options.add_argument("--start-maximized")
    options.add_argument("--disable-info-bars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-default-apps")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--password-store=basic")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


# ----------------------------------------------------------
# EJECUTAR SCRIPT
# ----------------------------------------------------------
def ejecutar_script(nombre_script, driver):
    ruta_script = os.path.join(RUTA, nombre_script)

    registrar_log(f"== Iniciando {nombre_script} ==")

    try:
        subprocess.run([PYTHON_EXE, ruta_script], check=True)
        registrar_log(f"✔ Finalizó correctamente: {nombre_script}")
        notificar_whatsapp(driver, f"✔ Finalizó correctamente:\n{nombre_script}")

    except subprocess.CalledProcessError:
        registrar_log(f"❌ ERROR en {nombre_script}")
        notificar_whatsapp(driver, f"❌ ERROR al ejecutar:\n{nombre_script}")

    except Exception as e:
        registrar_log(f"⚠ ERROR inesperado en {nombre_script}: {e}")
        notificar_whatsapp(driver, f"⚠ ERROR inesperado:\n{nombre_script}")

    registrar_log(f"== Fin de {nombre_script} ==")


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
if __name__ == "__main__":

    registrar_log("🟦 Iniciando ejecución de TODOS los scripts")

    matar_chrome()

    driver = iniciar_driver()

    for s in scripts:

        matar_chrome()  # LIMPIEZA ANTES DE CADA SCRIPT
        time.sleep(3)

        try:
            ejecutar_script(s, driver)

        except Exception as e:
            registrar_log(f"⚠ Chrome colapsó en {s}, reiniciando navegador...")
            driver = iniciar_driver()
            time.sleep(5)

            try:
                ejecutar_script(s, driver)
            except:
                registrar_log(f"❌ Error definitivo en {s}, continuando...")
                continue

        time.sleep(2)  # PRIMO

    registrar_log("🟩 TODOS LOS SCRIPTS FINALIZADOS")
    notificar_whatsapp(driver, "🟩 TODOS LOS SCRIPTS FINALIZARON ✔")

    input("Presiona ENTER para cerrar...")