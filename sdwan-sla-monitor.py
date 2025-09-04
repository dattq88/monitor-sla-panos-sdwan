# -*- coding: utf-8 -*-
import requests
import xmltodict  # Dùng để chuyển đổi XML sang Dictionary
import json       # Dùng để làm việc với JSON
import xml.etree.ElementTree as ET
import urllib3
import logging

# Tắt các cảnh báo về SSL certificate không an toàn
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- PHẦN 1: CÁC HÀM CÀI ĐẶT VÀ XÁC THỰC ---

def setup_logging():
    """
    Thiết lập hệ thống logging để chỉ hiển thị trên console.
    """
    # Xóa các handlers cũ nếu có để tránh ghi log lặp lại
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Cấu hình logging cơ bản để chỉ in ra console
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.StreamHandler()])

def get_api_key(ip, username, password):
    """Lấy API key bằng phương thức POST để bảo mật thông tin đăng nhập."""
    url = f"https://{ip}/api/?type=keygen"
    payload = {'user': username, 'password': password}
    try:
        response = requests.post(url, data=payload, verify=False, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        if root.get('status') == 'success':
            api_key = root.find('.//key').text
            logging.info("Lấy API Key thành công!")
            return api_key
        else:
            error_msg = root.find('.//msg').text
            logging.error(f"Lỗi khi lấy API Key: {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Đã xảy ra lỗi request khi lấy API Key: {e}")
        return None

# --- PHẦN 2: HÀM LẤY THÔNG TIN SD-WAN ---

def get_sdwan_stats_as_json(ip, key):
    """Thực thi lệnh 'show sd-wan path-monitor stats' và trả về kết quả dưới dạng chuỗi JSON."""
    cmd_xml = "<show><sd-wan><path-monitor><stats></stats></path-monitor></sd-wan></show>"
    url = f"https://{ip}/api/?type=op&cmd={cmd_xml}&key={key}"
    try:
        logging.info("Đang gửi yêu cầu lấy thông tin SD-WAN path monitor...")
        response = requests.get(url, verify=False, timeout=15)
        response.raise_for_status()
        parsed_dict = xmltodict.parse(response.text)
        if parsed_dict.get('response', {}).get('@status') == 'success':
            logging.info("Thực thi lệnh thành công. Đang chuyển đổi sang JSON...")
            result_data = parsed_dict.get('response', {}).get('result', {})
            json_output = json.dumps(result_data, indent=2, ensure_ascii=False)
            return json_output
        else:
            error_msg = parsed_dict.get('response', {}).get('result', {}).get('msg', 'Không rõ lỗi.')
            logging.error(f"Lỗi khi thực thi lệnh SD-WAN: {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Đã xảy ra lỗi request khi lấy thông tin SD-WAN: {e}")
        return None

# --- PHẦN 3: KHỐI THỰC THI CHÍNH ---

if __name__ == "__main__":
    # Thiết lập logging
    setup_logging()

    # --- THAY ĐỔI CÁC THÔNG SỐ NÀY ---
    FIREWALL_IP = "192.168.1.1"      # Thay bằng IP của firewall
    USERNAME    = "admin"                # Thay bằng username có quyền API
    PASSWORD    = "your_password"        # Thay bằng mật khẩu
    # ------------------------------------

    logging.info(f"--- Bắt đầu kịch bản trên Firewall {FIREWALL_IP} ---")
    
    # 1. Lấy API Key
    api_key = get_api_key(FIREWALL_IP, USERNAME, PASSWORD)
    
    # 2. Nếu có API Key, thực thi lệnh và in kết quả
    if api_key:
        sdwan_stats_json = get_sdwan_stats_as_json(FIREWALL_IP, api_key)
        if sdwan_stats_json:
            print("\n" + "="*55)
            print(" KẾT QUẢ SD-WAN STATS (ĐỊNH DẠNG JSON)")
            print("="*55)
            print(sdwan_stats_json)

    logging.info("--- Kịch bản hoàn tất. ---")
