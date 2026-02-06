import time, random 
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import pyperclip, csv, os, locale, string, hashlib
from datetime import datetime 

# Configuración inicial
WHATSAPP ='https://web.whatsapp.com'  # URL de WhatsApp Web
MERCADOLIBRE_URL = "https://www.mercadolibre.com.mx"
MERCADOLIBRE_DEALS_URL = "https://www.mercadolibre.com.mx/ofertas?page=2"
MERCADOLIBRE_AFFILIATE_URL = "https://www.mercadolibre.com.mx/afiliados/linkbuilder"
# MERCADOLIBRE_DEALS_URL = "https://www.mercadolibre.com.mx/ofertas?page=2"


  
# Ids de productos
PRODUCT_IDS = (
  [f":R2{j}j7:" for j in range(0, 10)] # R21j7 al R210j7
  +
  [f":R2{j}j7:" for j in string.ascii_lowercase[:22]]# R2aj7 al R2vj7 (a=0 ... v=21)
  +
  [f":R3{j}j7:" for j in range(0, 5)]
  +
  [f":R3{j}j7:" for j in string.ascii_lowercase[:15]]    # R2aj7 al R2vj7 (a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7, i=8, j=9, k=10, ... v=21)  
)
# CHROMEDRIVER_PATH = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\ChromeDriver\chromedriver.exe'
CHROMEDRIVER_PATH = r"C:\ChromeDriver\chromedriver.exe"  # o la ruta donde lo tengas
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" # Ruta a Google Chromes
# CHROMEDRIVER_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\ChromeDriver\chromedriver.exe"
PRODUCT_SELECTOR_TEMPLATE = 'div[id="{product_id}"] a'  # Plantilla para seleccionar productos por ID

# Rutas de la carpeta de LOG 
ruta_carpeta = r"C:\Users\kemie\OneDrive\Documentos\Afiliados\Logs"
# Rutas de Chrome
PROFILE_DIR= R"C:\Users\kemie\AppData\Local\Google\Chrome\User Data\Default" #"C:\Users\Juan Rivera\AppData\Local\Google\Chrome\User Data\Default"
PROFILE= "Erick" #profile_dir = "Profile 1"  # Cambia según el nombre del perfil (puede ser "Default", "Profile 2", etc.)
CHAT = "Lord Gangas I" # "Notas Erick" # "Lord Gangas I"  # Nombre del chat de WhatsApp


# Selectores CSS
TITLE_SELECTOR = 'h1.ui-pdp-title'
PRICE_ORIGINAL_SELECTOR = 's.andes-money-amount--previous .andes-money-amount__fraction'
PRICE_DISCOUNTED_SELECTOR = 'meta[itemprop="price"]'
PRICE_CONTENT = "content"
DISCOUNT_PERCENTAGE_SELECTOR = "span.andes-money-amount__discount"


USER = 'kemiedo@gmail.com'
PASSWORD = '************'


def extract_number(text):
    if not text:
        return None
    cleaned_text = re.sub(r'[$,]', '', str(text)).strip()
    match = re.search(r'(\d+)', cleaned_text)
    return int(match.group(1)) if match else None

def extract_percentage(text):
    if not text:
        return None
    match = re.search(r'(\d+)\s*%', str(text))
    return int(match.group(1)) if match else None


###################################################
#llamado de accion
from vLlamados import llamados_verde, llamados_naranja, llamados_rojo, llamados_fuego #Trae a los llamados de acción desde el archivo llamados.py
#Id de boton para generar links de afiliado, cambia bastante, así se cambia solo en este file.
from vID_boton_link import idlink #Trae la variable donde se almacena el ID del Boton que genera los links de afiliado id_boton_link.py


def obtener_llamado_accion(discount_percentage):
    try:
        discount_percentage = float(discount_percentage)
    except:
        discount_percentage = 0
    if discount_percentage >= 60:
        return random.sample(llamados_fuego,1)[0]  # Selecciona un llamado de acción al azar
    elif discount_percentage >= 41:
        return random.sample(llamados_rojo,1)[0]  # Selecciona un llamado de acción al azar
    elif discount_percentage >= 21:
        return random.sample(llamados_naranja,1)[0]  # Selecciona un llamado de acción al azar
    else:
        return random.sample(llamados_verde,1)[0]  # Selecciona un llamado de acción al azar
###################################################
 
 # Crear log
 ###################################################
nombre_log = "Registro.log"
ruta_log = os.path.join(ruta_carpeta, nombre_log)
contador_mensajes = 0

def registrar_envio(product_info, contador): 
    resumen = f"{product_info['ID']} → {product_info['Titulo'][:15]}  → 🔥 Ahora: ${product_info['Precio Descuento']} – {product_info['% Descuento']}% OFF"
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_log = f"[{hora_actual}] ✅ Mensaje #{contador} enviado: '{resumen}'\n"
    
    # Guardar en archivo log
    with open(ruta_log, "a", encoding="utf-8") as log_file:
        log_file.write(mensaje_log)
    print(mensaje_log.strip())  # también lo muestra en consola
###################################################

# Configuración de Selenium
print("Configurando WebDriver...")
options = Options()
# options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Ruta a Brave
options.binary_location = CHROME_PATH # Ruta a Google Chrome
options.add_argument(f"--user-data-dir={PROFILE_DIR}") # Ruta de datos de Google Chrome
options.add_argument(f"--profile-directory={PROFILE}") # options.add_argument("profile-directory=Default")  # O el nombre del perfil que usas Erick
options.add_argument("--start-maximized")
options.add_argument("--disable-info-bars")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-features=PushMessaging,NotificationTriggers")
options.add_argument("--disable-component-update")
options.add_argument("--disable-default-apps")
options.add_argument("--password-store=basic")
# options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
#options.add_argument("--disable-gpu")  # Recomendado en algunos sistemas
#options.add_argument("--window-size=1920,1080")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
# pestana_ofertas = driver.window_handles[0]
# pestana_whatsapp = driver.window_handles[1]
try:

    wait = WebDriverWait(driver, 10)  # Tiempo de espera explícita
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print(f"Navegando a: {MERCADOLIBRE_DEALS_URL}")
    driver.get(MERCADOLIBRE_DEALS_URL)  # o la página que necesites
    wait = WebDriverWait(driver, 3)  # Tiempo de espera explícita
    print("WebDriver iniciado correctamente.")

except Exception as e:
    print(f"Error al iniciar WebDriver: {e}")
    print("Verifica la ruta a chromedriver y/o Brave.")
    exit()

# Proceso principal
scraped_data = []  # Lista para almacenar los datos extraídos

try:
    # 1. Ir a la página de whatsapp
    time.sleep(random.uniform(0.5,1))   # Esperar que cargue la página
    # Abrir WhatsApp Web en una nueva pestaña y esperar a que esté disponible
    driver.execute_script("window.open('https://web.whatsapp.com');")
    wait.until(lambda d: len(d.window_handles) > 1)  # Esperar hasta que haya más de una pestaña
    time.sleep(random.uniform(101, 201))  # Esperar que cargue la página de WhatsApp Web
    driver.switch_to.window(driver.window_handles[0])   # Cambiar a la pestaña de Ofertas
    time.sleep(random.uniform(1, 2))   # Esperar que cargue la página
    # time.sleep(random.uniform(300, 500.5))   # Esperar que cargue la página

    # Manejar el overlay de consentimiento de cookies
    try:
        cookie_banner = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cookie-consent-banner-opt-out_container')))
        accept_button = cookie_banner.find_element(By.CSS_SELECTOR, '.cookie-consent-banner-opt-out_accept_all')
        accept_button.click()
        print("Cookies aceptadas.")
    except TimeoutException:
        print("No se encontró el banner de cookies.")

    # Iterar sobre los IDs de productos
    
    for product_id in PRODUCT_IDS:
         # Recorrer los productos y asignar un número + ID único
                         
        try:
            print(f"\nProcesando producto con ID: {product_id}")

            # Construir el selector CSS para el producto actual
            product_selector = PRODUCT_SELECTOR_TEMPLATE.format(product_id=product_id)
            
            # Encontrar y hacer clic en el producto
            try:
                product_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, product_selector)))
                product_url = product_link.get_attribute('href')  # Guardar la URL del producto            
                # product_link.click()
                
                # Abrir en una nueva pestaña con JavaScript
                driver.execute_script("window.open(arguments[0]);", product_url)                
                # Cambiar a la nueva pestaña (última)
                driver.switch_to.window(driver.window_handles[-1])
                
                time.sleep(random.uniform(1, 2))  # Esperar que cargue la página del producto
            except TimeoutException:
                print(f"Producto con ID {product_id} no encontrado. Continuando...")
                continue
            

            time.sleep(random.uniform(0.5, 1))  # Esperar que cargue la página del producto
            product_url = driver.current_url
            print(product_url)
            print(f"URL copiada OK")             
            # Extraer datos del producto
            product_info = {
                "ID": product_id,
                "Icon": "N/A", 
                "Titulo": "N/A",
                "Precio Original": "N/A",
                "Precio Descuento": "N/A",
                "% Descuento": "N/A",
                "Indicador": "N/A",
                "URL Original": product_url,
                "URL Afiliado": "Error al generar"
            }
            
            try:
                # Título
                titulo_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, TITLE_SELECTOR)))
                product_info["Titulo"] = titulo_element.text.strip()
                titulo = titulo_element.text.strip()
                try:
                    titulo_lower = titulo.lower()
                    icon_titulo = "🏷️"  # ícono por defecto
                    if any(p in titulo_lower for p in ["tv", "televisión", "monitor", "smart tv"]):
                        icon_titulo = "📺"
                    elif any(p in titulo_lower for p in ["bocina", "sonido", "barra de sonido", "parlante", "speaker"]):
                        icon_titulo = "🔊"
                    elif any(p in titulo_lower for p in ["audífono", "headset", "auricular", "earbuds"]):
                        icon_titulo = "🎧"
                    elif any(p in titulo_lower for p in ["laptop", "notebook", "portátil", "computadora", "pc"]):
                        icon_titulo = "💻"
                    elif any(p in titulo_lower for p in ["celular","samsung galaxy s25","samsung galaxy s24","samsung galaxy s","samsung galaxy a", "smartphone", "iphone", "android", "poco", "realme", "oneplus", "oppo"]):
                        icon_titulo = "📱"
                    elif any(p in titulo_lower for p in ["reloj", "smartwatch", "pulsera inteligente"]):
                        icon_titulo = "⌚"
                    elif any(p in titulo_lower for p in ["cámara", "webcam", "fotografía", "dron"]):
                        icon_titulo = "📷"
                    elif any(p in titulo_lower for p in ["impresora", "scanner", "multifuncional"]):
                        icon_titulo = "🖨️"
                    elif any(p in titulo_lower for p in ["consola", "xbox", "playstation", "nintendo"]):
                        icon_titulo = "🎮"
                    elif any(p in titulo_lower for p in ["horno", "microondas", "estufa", "cocina", "quemador", "freidora"]):
                        icon_titulo = "🔥"
                    elif any(p in titulo_lower for p in [ "refri", "refrigerador", "lavadora", "electrodoméstico"]):
                        icon_titulo = "🧊"
                    elif any(p in titulo_lower for p in ["protector solar", "fps"]):
                        icon_titulo = "☀️⛱️"
                    elif any(p in titulo_lower for p in ["ventilador", "ventiladores", "aire acondicionado", "enfriador de aire", "humidificador", "a/c"]):
                        icon_titulo = "💨🥶❄️"
                    elif any(p in titulo_lower for p in ["colchón", "silla", "escritorio", "sofá", "mueble"]):
                        icon_titulo = "🛋️"
                    elif any(p in titulo_lower for p in ["maquillaje", "cosmético", "labial", "rubor", "rímel", "delineador", "esmalte", "brocha", "belleza"]):
                         icon_titulo = "💄"
                    elif any(p in titulo_lower for p in ["baño", "toalla", "cortina", "jabón", "regadera", "tapete", "portacepillo"]):
                        icon_titulo = "🛁"
                    elif any(p in titulo_lower for p in ["tenis", "zapato","zapatos", "botas", "sandalia","sandalias", "calzado", "pantufla"]):
                        icon_titulo = "👟"
                    elif any(p in titulo_lower for p in ["vitamina", "suplemento", "colágeno", "proteína", "multivitamínico","creatina", "omega", "nutrición", "energizante"]):
                        icon_titulo = "💪"
                    elif any(p in titulo_lower for p in ["herramienta", "taladro", "atornillador", "desarmador", "destornillador", "martillo", "llave inglesa", "pinza", "esmeriladora", "sierra", "caladora", "multiherramienta", "compresor", "caja de herramientas", "torno", "broca", "remachadora", "cautín", "nivel", "escuadra", "cepillo eléctrico", "cortadora", "sierra circular", "sierra de calar", "sierra de cinta", "sierra"]):
                        icon_titulo = "🛠️"
                    elif any(p in titulo_lower for p in ["perfume", "colonia", "fragancia", "loción", "body mist", "eau de parfum", "eau de toilette", "spray corporal", "desodorante", "set de perfume" ]):
                        icon_titulo = "🧴"
                    elif any(p in titulo_lower for p in ["sábana", "juego de sábanas", "edredón", "cobertor", "cobija", "colcha", "almohada", "funda", "ropa de cama", "cojín", "cubrecolchón", "colchón"]):
                        icon_titulo = "🛏️"
                    elif any(p in titulo_lower for p in ["auto", "automóvil", "coche", "carro", "vehículo", "camioneta", "sedán", "suv", "pickup", "motocicleta"]):
                        icon_titulo = "🚗"
                    elif any(p in titulo_lower for p in ["refacción", "sensor", "bujía", "amortiguador", "balata", "pastilla de freno", "clutch", "embrague", "radiador", "alternador", "inyector", "bobina", "banda", "correa", "válvula", "termostato", "pieza de motor", "soporte de motor", "soporte de transmisión",  "filtro de aire", "filtro de aceite", "filtro de combustible", "filtro de aire acondicionado"]):
                        icon_titulo = "🔧"
                                    
                    product_info["Icon"] = icon_titulo.strip()
                    print(f"Ícono asignado: {icon_titulo}")
                except Exception as e:
                    icon_titulo = "❓"
                    print(f"Error al asignar ícono al título: {e}")
                
                # Precio original (puede no existir)
                try:
                    precio_orig_element = driver.find_element(By.CSS_SELECTOR, PRICE_ORIGINAL_SELECTOR)
                    product_info["Precio Original"] = extract_number(precio_orig_element.text)
                except NoSuchElementException:
                    product_info["Precio Original"] = "N/A"

                # Precio con descuento
                #__________________________________________________________
                try:
                    precio_element = driver.find_element(By.CSS_SELECTOR, PRICE_DISCOUNTED_SELECTOR)
                    precio_descuento = float(precio_element.get_attribute(PRICE_CONTENT))
                    print(f"Precio descuento {precio_descuento}")
                    time.sleep(random.uniform(1, 2.5))
                    product_info["Precio Descuento"] = (
                        f"{int(precio_descuento):,}" if precio_descuento == int(precio_descuento)
                           else f"{precio_descuento:,.2f}")
                    # product_info["Precio Descuento"] = "{:,.2f}".format(precio_descuento)
                except Exception as e:
                    precio_descuento = 0
                    product_info["Precio descuento"] = "N/A"
                    print(f"Error al obtener el precio desde el meta tag: {e}")
                #__________________________________________________________
                # Obtner el porcentaje de descuento
                try:
                    porcentaje_element = driver.find_element(By.CSS_SELECTOR, DISCOUNT_PERCENTAGE_SELECTOR)
                    discount_text = porcentaje_element.text.strip()  # Ejemplo: "68% OFF"

                    # Extrae el número del texto
                    match = re.search(r"(\d+)", discount_text)
                    discount_percentage = int(match.group(1)) if match else 0

                    product_info["% Descuento"] = extract_percentage(porcentaje_element.text)
                    # print(f"Porcentaje de descuento obtenido: {discount_percentage}%")

                except Exception as e:
                    discount_percentage = 0
                    print(f"Error al extraer porcentaje de descuento: {e}") 


                try:
                    # Suponiendo que discount_percentage ya es un número entero
                    discount_percentage = int(discount_percentage)

                    if 1 <= discount_percentage <= 20:
                        indicador = "🟢"
                    elif 21 <= discount_percentage <= 40:
                        indicador = "🟠🟠"
                    elif 41 <= discount_percentage <= 60:
                        indicador = "🔴🔴🔴"
                    elif discount_percentage > 60:
                        indicador = "🔥🔥🔥🔥"
                    else:
                        indicador = "⚪"
                    product_info["Indicador"] = indicador.strip()
                    # Mostrar el porcentaje de descuento y el indicador
                except Exception as e:
                    print(f"Error al procesar el semáforo de descuento: {e}")
                    indicador = "❓"
            except Exception as e:
                print(f"Error al extraer datos del producto {product_id}: {e}")

            # Navegar a la página de afiliados
            print("Generando link afiliado...")
            # Abrir una nueva pestaña para la página de afiliados
            # driver.switch_to.window(driver.window_handles[0])   # Cambiar a la nueva pestaña de WhatsApp
            driver.get(MERCADOLIBRE_AFFILIATE_URL)
            time.sleep(random.uniform(1,2.5))  # Esperar que cargue la página de afiliados

            try:
                # Navegar a la página de afiliados
                
                # 1. Espera y encuentra el input
                time.sleep(random.uniform(1, 2))
                input_url = driver.find_element(By.ID, "url-0")

                # 2. Enviamos la URL original
                input_url.clear()
                input_url.send_keys(product_info["URL Original"])

                # 3. Espera y da clic en el botón
                time.sleep(random.uniform(1.5, 2))
                boton = driver.find_element(By.ID, f"{idlink}") #R19lcu R19kcu ":R19kcu:" # ":R19kcq:" R2j9u
                boton.click()

                # 4. Espera a que el valor se copie al portapapeles
                time.sleep(random.uniform(1, 2))  # Asegúrate que la acción de copiar haya ocurrido

                # 5. Obtener valor del portapapeles
                product_info["URL Afiliado"] = pyperclip.paste()
                
                # Esperar que se genere el link afiliado
                time.sleep(random.uniform(1, 2.5))  # Ajusta según sea necesario
                link_afiliado = pyperclip.paste()  # Leer del portapapeles
                driver.close()  # Cerrar la pestaña de afiliados

            except Exception as e:
                print(f"Error al generar link afiliado: {e}")
            
            # Enviar a Whatsapp
            #####################################################
            try:
                # Abrir WhatsApp Web en una nueva pestaña
                # time.sleep(random.uniform(100, 205))  # Tiempo de espera para abrir sesion de WhtasApp
                time.sleep(random.uniform(.5,1))  # Ajusta según sea necesario  
                print(f"Abriendo WhatsApp Web en una nueva pestaña...")
                driver.switch_to.window(driver.window_handles[1])   # Cambiar a la nueva pestaña de WhatsApp
                time.sleep(random.uniform(5, 7.5))  # Esperar que cargue WhatsApp Web
                # Buscar el chat de "Lord Gangas I"
                print(f"Buscando el chat '{CHAT}' en WhatsApp Web...")
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]')))
                search_box.click()
                search_box.send_keys(Keys.CONTROL, 'a')  # Nombre del chat
                search_box.send_keys(CHAT)  # Nombre del chat
                search_box.send_keys(Keys.ENTER)  # Presionar Enter para abrir el chat
                search_box.click()
                time.sleep(random.uniform(0.5, 1))  # Esperar que se abra el chat
                # Enviar el mensaje con los datos del producto
                # Convertimos los valores a string y en minúsculas para asegurar la comparación
                precio_original = str(product_info.get('Precio Original', '')).strip().lower()
                precio_descuento = str(product_info.get('Precio Descuento', '')).strip().lower()
                llamados_accion = obtener_llamado_accion(product_info['% Descuento'])
                print(f"Porcentaje de Descuento: {discount_percentage}% → Indicador: {indicador}")
                print(llamados_accion)

                # Condición para mensaje corto
                if precio_original in ["none", "n/a", "na", "", "0", "0.0"] or precio_descuento in ["none", "n/a", "na", "na", "", "0", "0.0"]:
                    message = (
                    f"_*{llamados_accion}*_\n \n" 
                    f"_*{product_info['Icon']} {product_info['Titulo']}*_\n"
                    f"*✨ Oportunidad única por solo: ${product_info['Precio Descuento']}*\n"
                    f"*🔥Aprovecha esta oferta antes de que se agote🔥* \n"
                    f"*{random.choice(['🛒', '🔗'])} Compra aquí 👇🏼*\n{product_info['URL Afiliado']} \n"
                )
                else:
                    message = (
                    f"_*{llamados_accion}*_\n \n" 
                    f"_*{product_info['Icon']} {product_info['Titulo']}*_\n"
                    f"*💸 Antes:* ~${product_info['Precio Original']}~\n"
                    f"*🔥 Ahora: ${product_info['Precio Descuento']}*\n"
                    f"*🎯 Descuento: {product_info['Indicador']} {product_info['% Descuento']}% OFF*\n"
                    f"*{random.choice(['🛒', '🔗'])} Compra aquí 👇🏼*  \n{product_info['URL Afiliado']} \n"
                    )
                
                # message_box = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p')
                message_box = driver.find_element(By.XPATH,'//div[@role="textbox" and @aria-placeholder="Escribe un mensaje"]')
                message_box.click()
                
                print(f"Enviando mensaje al chat '{CHAT}'...")
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                time.sleep(random.uniform(1, 3))  # Esperar un momento antes de pegar
                pyperclip.copy(message)
                time.sleep(random.uniform(1, 3))  # Esperar un momento antes de pegar
                message_box.send_keys(Keys.CONTROL, 'v')
                # message_box.send_keys(message)

                time.sleep(random.uniform(11, 21))  # Esperar que se abra el chat
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                message_box.send_keys(Keys.DELETE)         # Suprimir el texto seleccionado
                # message_box.send_keys(Keys.CONTROL, 'x')  # Cortar el mensaje 
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                message_box.send_keys("Lupita y John")  # Enviar un texto para evitar el error de "No se puede enviar un mensaje vacío"
                time.sleep(random.uniform(11, 21))  # Esperar un momento antes de copiar
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                
                time.sleep(random.uniform(1.5, 2))  # Esperar un momento 
                pyperclip.copy(message)
                time.sleep(random.uniform(1.5, 2))  # Esperar un momento 
                message_box.send_keys(Keys.CONTROL, 'v') # Ctrl + v (pegar)

                time.sleep(random.uniform(11, 21))  # Esperar que se abra el chat
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                #message_box.send_keys(Keys.CONTROL, 'x')  # Cortar el mensaje 
                message_box.send_keys(Keys.DELETE)         # Suprimir el texto seleccionado
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                message_box.send_keys("Gigi y Evan")  # Enviar un texto para evitar el error de "No se puede enviar un mensaje vacío"
                time.sleep(random.uniform(11, 21))  # Esperar un momento antes de copiar
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                pyperclip.copy(message)
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                message_box.send_keys(Keys.CONTROL, 'v') # Ctrl + v (pegar)
                
                time.sleep(random.uniform(11, 21))  # Esperar un momento antes de enviar el mensaje
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                message_box.send_keys("Aby bb")  # Enviar un texto para evitar el error de "No se puede enviar un mensaje vacío"
                time.sleep(random.uniform(11, 21))  # Esperar un momento antes de copiar
                message_box.send_keys(Keys.CONTROL, 'a') # Ctrl + A (seleccionar todo)
                # Ctrl + v (pegar)
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                pyperclip.copy(message)
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento 
                message_box.send_keys(Keys.CONTROL, 'v')
                time.sleep(random.uniform(91, 141))  # Esperar un momento antes de enviar el mensaje
                
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'img.x1c4vz4f.x2lah0s.xdl72j9.x1vke2v8')))
                print("✅ Miniatura cargada.")
                time.sleep(random.uniform(127, 201))  # tiempo de espera entre mensajes
                # Esperar que se cargue la imagen web                
                message_box.send_keys(Keys.ENTER)  # Enviar el mensaje
                time.sleep(random.uniform(11, 21))  # Esperar un momento antes de enviar el mensaje                
                contador_mensajes += 1 # si llega a esta línea, manda el mensaje al contador de mensajes
                registrar_envio(product_info, contador_mensajes) # Registra el mensaje en el log
                time.sleep(random.uniform(0.5, 1))  # Esperar un momento antes de continuar
                # Cambbiar a la pestaña de Ofertas
                driver.switch_to.window(driver.window_handles[0])   # Cambiar a la nueva pestaña de Ofertas
                print(f"Mensaje enviado al chat 'Lord Gangas I'.")
                # contador_mensajes += 1
                # registrar_envio(product_info, contador_mensajes)
            except Exception as e:
                print(f"Error al enviar mensaje por WhatsApp: {e}")
            #####################################################
               
            finally:
                
                time.sleep(random.uniform(1, 2))  # Esperar un momento antes de continuar
                driver.switch_to.window(driver.window_handles[0])  # Volver a la pestaña principal

            # Guardar los datos del producto
            scraped_data.append(product_info)
            print(f"Datos del producto {product_id} guardados.")

        except ElementClickInterceptedException:
            print(f"Error procesando el producto con ID {product_id}: Elemento interceptado. Intentando nuevamente...")
        
            try:
                # Intentar cerrar cualquier overlay que pueda estar bloqueando
                close_button = driver.find_element(By.CSS_SELECTOR, '.cookie-consent-banner-opt-out_close')
                close_button.click()
                print("Overlay cerrado. Reintentando clic.")
                continue
            except NoSuchElementException:
                print("No se encontró ningún overlay para cerrar.")

        except Exception as e:
            print(f"Error procesando el producto con ID {product_id}: {e}")
            continue
        
finally:
    # Cerrar el navegador
    print("Cerrando WebDriver...")
    # driver.quit()
    driver.close()            
    time.sleep(random.uniform(1, 2))  # Esperar que cargue la página de afiliados    
    # driver.close()
    print("WebDriver cerrado.")
    
    
    # Guarda el archivo txt
    # ✅ Configura el locale correctamente
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Mexico.1252')  # Windows
    except:
        locale.setlocale(locale.LC_TIME, 'es_MX.UTF-8')  # Linux/macOS

    # 📁 Ruta de guardado
    os.makedirs(ruta_carpeta, exist_ok=True)

    # 🕒 Fecha y nombre del archivo
    fecha_actual = datetime.now()
    dia_semana = fecha_actual.strftime('%A').capitalize()  # "Sábado"
    fecha_numerica = fecha_actual.strftime('%y%m%d%H%M')   # "2505172249"
    nombre_archivo = f"Ofertas de ML {dia_semana} {fecha_numerica}.txt"

    # 📝 Ruta completa
    ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
    print(f"Ruta final del archivo: {ruta_completa}")

    # Guardar txt
    
    # Guardar datos con formato de presentación
    with open(ruta_completa, "w", encoding="utf-8") as file:
        for item in scraped_data:
            file.write("--------------------------------------------------\n")
            file.write(f" \n")
            file.write(f"_*{item['Icon']} {item['Titulo']}*_\n")
            file.write(f"*💸 Antes:* ~${item['Precio Original']}~\n")
            file.write(f"*🔥 Ahora: ${item['Precio Descuento']}*\n")
            file.write(f"*🎯 Descuento: {item['Indicador']} {item['% Descuento']}% OFF*\n")
            file.write(f"*{random.choice(["🛒", "🔗"])} Compra aquí 👇🏼*  \n{item['URL Afiliado']}\n")
            # 🔗 
            file.write("--------------------------------------------------\n\n")
    print(f"Archivo guardado en: {ruta_completa}")

# Mostrar los datos recopilados
print("\n- DATOS RECOPILADOS -")
for item in scraped_data:
    print(f"*Título: {item['Icon']} {item['Titulo']}*")
    print(f"Precio Original: ~${item['Precio Original']}~")
    print(f"*Precio con Descuento: ${item['Precio Descuento']}*")
    print(f"*Descuento: {item['Indicador']} {item['% Descuento']}% OFF*")
    print(f"URL Original: {item['URL Original']}")
    print(f"URL Afiliado: {item['URL Afiliado']}")
    print("-" * 50)