# -*- coding: utf-8 -*-
import requests
import xmltodict  # Dung de chuyen doi XML sang Dictionary
import json       # Dung de lam viec voi JSON
import xml.etree.ElementTree as ET
import urllib3
import logging

# Tat cac canh bao ve SSL certificate khong an toan
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- PHAN 1: CAC HAM CAI DAT VA XAC THUC ---

def setup_logging():
    """
    Thiet lap he thong logging de chi hien thi tren console.
    """
    # Xoa cac handlers cu neu co de tranh ghi log lap lai
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Cau hinh logging co ban de chi in ra console
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.StreamHandler()])

def get_api_key(ip, username, password):
    """Lay API key bang phuong thuc POST de bao mat thong tin dang nhap."""
    url = f"https://{ip}/api/?type=keygen"
    payload = {'user': username, 'password': password}
    try:
        response = requests.post(url, data=payload, verify=False, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        if root.get('status') == 'success':
            api_key = root.find('.//key').text
            logging.info("Lay API Key thanh cong!")
            return api_key
        else:
            error_msg = root.find('.//msg').text
            logging.error(f"Loi khi lay API Key: {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Da xay ra loi request khi lay API Key: {e}")
        return None

# --- PHAN 2: CAC HAM LAY THONG TIN SD-WAN ---

def get_sdwan_stats_as_json(ip, key):
    """Thuc thi lenh 'show sdwan path-monitor stats' va tra ve ket qua duoi dang chuoi JSON."""
    cmd_xml = "<show><sdwan><path-monitor><stats></stats></path-monitor></sdwan></show>"
    url = f"https://{ip}/api/?type=op&cmd={cmd_xml}&key={key}"
    try:
        logging.info("Dang gui yeu cau lay thong tin SD-WAN path monitor...")
        response = requests.get(url, verify=False, timeout=15)
        response.raise_for_status()
        parsed_dict = xmltodict.parse(response.text)
        if parsed_dict.get('response', {}).get('@status') == 'success':
            logging.info("Thuc thi lenh 'path-monitor stats' thanh cong. Dang chuyen doi sang JSON...")
            result_data = parsed_dict.get('response', {}).get('result', {})
            json_output = json.dumps(result_data, indent=2, ensure_ascii=False)
            return json_output
        else:
            error_msg = parsed_dict.get('response', {}).get('result', {}).get('msg', 'Khong ro loi.')
            logging.error(f"Loi khi thuc thi lenh 'path-monitor stats': {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Da xay ra loi request khi lay thong tin 'path-monitor stats': {e}")
        return None

def get_sdwan_connections_as_json(ip, key):
    """Thuc thi lenh 'show sdwan connection all' va tra ve ket qua duoi dang chuoi JSON."""
    cmd_xml = "<show><sdwan><connection><all></all></connection></sdwan></show>"
    url = f"https://{ip}/api/?type=op&cmd={cmd_xml}&key={key}"
    try:
        logging.info("Dang gui yeu cau lay thong tin SD-WAN connection all...")
        response = requests.get(url, verify=False, timeout=15)
        response.raise_for_status()
        parsed_dict = xmltodict.parse(response.text)
        if parsed_dict.get('response', {}).get('@status') == 'success':
            logging.info("Thuc thi lenh 'connection all' thanh cong. Dang chuyen doi sang JSON...")
            result_data = parsed_dict.get('response', {}).get('result', {})
            json_output = json.dumps(result_data, indent=2, ensure_ascii=False)
            return json_output
        else:
            error_msg = parsed_dict.get('response', {}).get('result', {}).get('msg', 'Khong ro loi.')
            logging.error(f"Loi khi thuc thi lenh 'connection all': {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Da xay ra loi request khi lay thong tin 'connection all': {e}")
        return None

# --- PHAN 3: KHOI THUC THI CHINH ---

if __name__ == "__main__":
    # Thiet lap logging
    setup_logging()

    # --- THAY DOI CAC THONG SO NAY ---
    FIREWALL_IP = "192.168.1.1"      # Thay bang IP cua firewall
    USERNAME    = "admin"                # Thay bang username co quyen API
    PASSWORD    = "your_password"        # Thay bang mat khau
    # ------------------------------------

    logging.info(f"--- Bat dau kich ban tren Firewall {FIREWALL_IP} ---")
    
    # 1. Lay API Key
    api_key = get_api_key(FIREWALL_IP, USERNAME, PASSWORD)
    
    # 2. Neu co API Key, thuc thi cac lenh va in ket qua
    if api_key:
        # Thuc thi va in ket qua lenh thu nhat
        sdwan_stats_json = get_sdwan_stats_as_json(FIREWALL_IP, api_key)
        if sdwan_stats_json:
            print("\n" + "="*55)
            print(" KET QUA: SHOW SDWAN PATH-MONITOR STATS (JSON)")
            print("="*55)
            print(sdwan_stats_json)

        # Thuc thi va in ket qua lenh thu hai
        sdwan_connections_json = get_sdwan_connections_as_json(FIREWALL_IP, api_key)
        if sdwan_connections_json:
            print("\n" + "="*55)
            print(" KET QUA: SHOW SDWAN CONNECTION ALL (JSON)")
            print("="*55)
            print(sdwan_connections_json)

    logging.info("--- Kich ban hoan tat. ---")
