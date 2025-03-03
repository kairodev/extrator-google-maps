import pandas as pd
import time
import requests
import socket
import ssl
import os
import sys
import random
import warnings
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

warnings.filterwarnings("ignore")

def enviar_email(destinatario, remetente, senha, assunto, corpo):
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()  # Ativa a segurança
            servidor.login(remetente, senha)
            servidor.send_message(msg)
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

def verificar_site(url, verificar_completo=False):
    if not url or url == "Não obtido":
        return {
            "velocidade_carregamento": "Não obtido",
            "tem_ssl": "Não obtido",
            "dominio": "Não obtido",
            "site_proprio": "Não obtido",
            "whatsapp": "Não obtido",
            "instagram": "Não obtido",
            "tecnologias": "Não obtido"
        }

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    parsed_url = urlparse(url)
    dominio = parsed_url.netloc or parsed_url.path.split('/')[0]
    
    site_proprio = not any(x in url.lower() for x in ['instagram.com', 'facebook.com', 'api.whatsapp.com', 'wa.me', 'linkedin.com', 'twitter.com', 'youtube.com'])

    if not verificar_completo:
        return {
            "velocidade_carregamento": "Não obtido",
            "tem_ssl": "Não obtido",
            "dominio": dominio,
            "site_proprio": "Sim" if site_proprio else "Não",
            "whatsapp": "Não obtido",
            "instagram": "Não obtido",
            "tecnologias": "Não obtido"
        }

    try:
        start_time = time.time()
        response = requests.get(url, timeout=5, verify=False)
        velocidade_carregamento = round(time.time() - start_time, 2)
    except (requests.RequestException, socket.gaierror):
        return {
            "velocidade_carregamento": "Erro",
            "tem_ssl": "Não obtido",
            "dominio": dominio,
            "site_proprio": "Sim" if site_proprio else "Não",
            "whatsapp": "Não obtido",
            "instagram": "Não obtido",
            "tecnologias": "Não obtido"
        }

    tem_ssl = url.startswith('https://') and response.status_code == 200
    if tem_ssl:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((dominio, 443)) as sock:
                with ctx.wrap_socket(sock, server_hostname=dominio):
                    tem_ssl = True
        except (ssl.SSLError, socket.error):
            tem_ssl = False

    whatsapp = "Não obtido"
    instagram = "Não obtido"
    tecnologias = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'api.whatsapp.com' in href or 'wa.me' in href:
                whatsapp = href
                break
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'instagram.com' in href:
                instagram = href
                break
        html_content = response.text.lower()
        if 'wp-content' in html_content or 'wordpress' in html_content:
            tecnologias.append("WordPress")
        if 'bootstrap' in html_content:
            tecnologias.append("Bootstrap")
        if 'react' in html_content or 'react-dom' in html_content:
            tecnologias.append("ReactJS")
        if not tecnologias:
            tecnologias.append("Não obtido")

    return {
        "velocidade_carregamento": velocidade_carregamento,
        "tem_ssl": "Sim" if tem_ssl else "Não",
        "dominio": dominio,
        "site_proprio": "Sim" if site_proprio else "Não",
        "whatsapp": whatsapp,
        "instagram": instagram,
        "tecnologias": "; ".join(tecnologias)
    }

def scroll_to_load_results(driver, max_results):
    scroll_pane = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'm6QErb')]//div[@role='feed']"))
    )
    
    businesses = []
    previous_count = 0
    
    while len(businesses) < max_results:
        try:
            businesses = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
            current_count = len(businesses)
            
            if current_count >= max_results:
                break
            
            if current_count == previous_count:
                break
            
            last_element = businesses[-1]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_element)
            
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, 'hfpxzc')) > current_count
            )
            
            previous_count = current_count
            time.sleep(0.5)
            
        except TimeoutException:
            break
        except IndexError:
            break
        except Exception as e:
            print(f"Erro durante a rolagem: {str(e)}")
            break
    
    return min(len(businesses), max_results)

def extrair_elemento(driver, xpath, descricao, nome_esperado, i, total):
    try:
        elemento = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        texto = elemento.text.strip()
        return texto if texto else "Não obtido"  
    except (TimeoutException, NoSuchElementException):
        return "Não obtido"

def extrair_reputacao(driver, nome_esperado, i, total):
    try:
        rating_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'F7nice')]"))
        )
        rating_text = rating_element.text.strip()
        
        parts = rating_text.split()
        if len(parts) >= 2:
            nota = parts[0].replace(',', '.')  
            num_avaliacoes = parts[1].replace('(', '').replace(')', '')  
            return f"{num_avaliacoes} ({nota})"
        return "Não obtido"
    except (TimeoutException, NoSuchElementException, Exception) as e:
        print(f"Reputação não encontrada para {nome_esperado}: {str(e)}")
        return "Não obtido"

def processar_aba(driver, window_handle, nome_esperado, link, strict_filter, i, total, verificar_sites):
    try:
        driver.switch_to.window(window_handle)
        driver.get(link)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'DUwDvf')]"))
        )

        name = extrair_elemento(driver, "//h1[contains(@class, 'DUwDvf')]", "Nome", nome_esperado, i, total)
        if name != nome_esperado and name != "Não obtido":
            return None

        phone = extrair_elemento(driver, "//button[contains(@data-item-id, 'phone')]//div[contains(@class, 'Io6YTe')]", "Telefone", nome_esperado, i, total)
        address = extrair_elemento(driver, "//button[contains(@data-item-id, 'address')]//div[contains(@class, 'Io6YTe')]", "Endereço", nome_esperado, i, total)
        url = extrair_elemento(driver, "//a[contains(@data-item-id, 'authority')]//div[contains(@class, 'Io6YTe')]", "Site", nome_esperado, i, total)
        reputacao = extrair_reputacao(driver, nome_esperado, i, total)

        analise_site = verificar_site(url, verificar_completo=verificar_sites)

        local = {
            "Nome": name,
            "Endereço": address,
            "Telefone": phone,
            "Site": url,
            "Reputação": reputacao,
            "Site Próprio": analise_site["site_proprio"],
            "Velocidade Carregamento (s)": analise_site["velocidade_carregamento"],
            "Tem SSL": analise_site["tem_ssl"],
            "Domínio": analise_site["dominio"],
            "WhatsApp": analise_site["whatsapp"],
            "Instagram": analise_site["instagram"],
            "Tecnologias": analise_site["tecnologias"]
        }

        if strict_filter and (phone == "Não obtido" and url == "Não obtido"):
            return None
        return local

    except Exception as e:
        print(f"Erro ao processar {nome_esperado}: {str(e)}")
        return {
            "Nome": nome_esperado,
            "Endereço": "Não obtido",
            "Telefone": "Não obtido",
            "Site": "Não obtido",
            "Reputação": "Não obtido",
            "Site Próprio": "Não obtido",
            "Velocidade Carregamento (s)": "Não obtido",
            "Tem SSL": "Não obtido",
            "Domínio": "Não obtido",
            "WhatsApp": "Não obtido",
            "Instagram": "Não obtido",
            "Tecnologias": "Não obtido"
        }

def append_to_csv(local, filename):
    df = pd.DataFrame([local])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(filename, mode='w', header=True, index=False, encoding='utf-8')

def scrape_google_maps(search_query, max_results=5, strict_filter=True, max_tabs=4, verificar_sites=False):
    if not os.path.exists('output'):
        os.makedirs('output')

    filename = f"output/leads_{search_query.replace(' ', '_')}.csv"
    locais = []
    nomes_processados = set()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        print("ChromeDriver baixado e configurado com sucesso!")
    except Exception as e:
        print(f"Erro ao baixar ou configurar o ChromeDriver: {str(e)}")
        print("Certifique-se de que o Chrome está instalado e tente novamente.")
        return

    driver.get('https://www.google.com/maps')
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchboxinput'))
        )
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc'))
        )
    except TimeoutException as e:
        print("Erro: Falha ao carregar os resultados da busca.")
        driver.quit()
        return

    links = []
    total = scroll_to_load_results(driver, max_results)
    businesses = driver.find_elements(By.CLASS_NAME, 'hfpxzc')[:max_results]
    for i, business in enumerate(businesses):
        try:
            link = business.get_attribute('href')
            nome_esperado = business.get_attribute('aria-label') or f"Negócio {i + 1}"
            if link and nome_esperado not in nomes_processados:
                links.append((nome_esperado, link))
                nomes_processados.add(nome_esperado)
        except StaleElementReferenceException:
            continue

    processed_count = 0
    original_window = driver.current_window_handle

    for i in range(0, min(len(links), max_results), max_tabs):
        abas = []
        for j in range(max_tabs):
            if i + j < min(len(links), max_results):
                driver.execute_script("window.open('');")
                nova_aba = driver.window_handles[-1]
                abas.append((nova_aba, links[i + j]))

        for idx, (window_handle, (nome_esperado, link)) in enumerate(abas):
            sys.stdout.write(f"\r[{processed_count}/{max_results}] Processando: {nome_esperado[:30]}...{' ' * 20}")
            sys.stdout.flush()
            local = processar_aba(driver, window_handle, nome_esperado, link, strict_filter, i + idx + 1, len(links), verificar_sites)
            if local and (not strict_filter or local["Telefone"] != "Não obtido" or local["Site"] != "Não obtido"):
                processed_count += 1
                append_to_csv(local, filename)
                locais.append(local)
                sys.stdout.write(f"\r[{processed_count}/{max_results}] Adicionado: {nome_esperado[:30]}...{' ' * 20}")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\r[{processed_count}/{max_results}] Ignorado: {nome_esperado[:30]}...{' ' * 20}")
                sys.stdout.flush()

        for window_handle, _ in abas:
            driver.switch_to.window(window_handle)
            driver.close()
        driver.switch_to.window(original_window)
        time.sleep(random.uniform(1, 3))

    driver.quit()
    print(f"\nBusca concluída! {len(locais)} resultados salvos em {filename}")

def main():
    # Solicita ao usuário o termo de busca
    search_query = input("Por favor, insira o termo de busca: ").strip()

    max_results = int(input("Quantos resultados você deseja (padrão é 5)? ") or 5)
    strict_filter = input("Você deseja filtrar resultados sem telefone ou site? (s/n): ").strip().lower() == 's'
    verificar_sites = input("Deseja verificar os sites encontrados? (s/n): ").strip().lower() == 's'

    if max_results < 1 or max_results > 1000:
        print("Erro: O limite deve ser entre 1 e 1000.")
        return

    print(f"Buscando: '{search_query}' | Limite: {max_results} resultados...")
    
    # Coleta dos dados
    scrape_google_maps(search_query, max_results=max_results, strict_filter=strict_filter, verificar_sites=verificar_sites)

    # Pergunta se o usuário deseja receber os resultados por e-mail
    enviar_por_email = input("Você gostaria de receber os resultados por e-mail? (s/n): ").strip().lower()
    if enviar_por_email == 's':
        destinatario = input("Por favor, insira seu e-mail: ").strip()
        remetente = input("Por favor, insira seu e-mail (remetente): ").strip()
        senha = input("Por favor, insira sua senha: ").strip()

        # Formate os resultados, aqui é um exemplo simples
        resultado_em_string = "Aqui estão os resultados da pesquisa..."  # Substitua pelos resultados formatados

        enviar_email(destinatario, remetente, senha, "Resultados da Pesquisa", resultado_em_string)

if __name__ == "__main__":
    main()  # Chama a função principal ao executar o script