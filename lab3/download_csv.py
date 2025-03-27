import urllib.request
import pandas as pd
import os
from datetime import datetime
import re

country = "UKR"
year_1 = 1981
year_2 = 2024
type_data = "Mean"
dir_data = r"C:/Users/User/vhi_venv/data_csv"

def clean_directory(dir_data):
    if not os.path.exists(dir_data):
        os.makedirs(dir_data)
        print(f"Директорія {dir_data} створена.")
    
    for filename in os.listdir(dir_data):
        filepath = os.path.join(dir_data, filename)
        if filename.endswith(".csv"):
            os.remove(filepath)
        
    print("Директорія очищена від старих файлів.")

def download_csv(country, year_1, year_2, type_data, dir_data):
    for province_id in range(1, 28):
        url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country={country}&provinceID={province_id}&year1={year_1}&year2={year_2}&type={type_data}" 
        try: 
            with urllib.request.urlopen(url) as response: 
                text = response.read()
        except urllib.error.URLError as e: 
            print(f"!!! Помилка завантаження для області {province_id}: {e}") 
            return
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"VHI_province_{province_id}_{timestamp}.csv"
        filepath = os.path.join(dir_data, filename)

        try:
            with open(filepath, 'wb') as out_file: 
                out_file.write(text) 
                print(f"Файл {filename} завантажено успішно.") 
        except IOError as e: 
            print(f"Помилка запису файлу {filename}: {e}")
    
def remove_html_tags(text):
    if isinstance(text, str):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    return text

def load_vhi_data(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".csv")]

    if not files:
        print("!!! Помилка: У директорії немає CSV-файлів.")
        return None

    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    all_data = []

    for file in files:
        filepath = os.path.join(directory, file)
        
        parts = file.split('_')
        region_id = parts[2] if len(parts) > 2 else None
        
        df = pd.read_csv(filepath, header=1, names=headers, converters={'Year': remove_html_tags})
        df = df.drop(columns=['empty'], errors='ignore')
        df.replace(-1, pd.NA, inplace=True)
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        df.insert(0, "Region_ID", region_id)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(by=["Region_ID", "Year", "Week"]).reset_index(drop=True)

    return final_df

def replace_region_ids(data_frames):

    region_mapping = {
        1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21, 11: 9,
        13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 21: 17, 22: 18, 
        23: 6, 24: 1, 25: 2, 26: 7, 27: 5
    }

    data_frames_cp = data_frames.copy()

    if "Region_ID" in data_frames_cp.columns:
        data_frames_cp["Region_ID"] = pd.to_numeric(data_frames_cp["Region_ID"], errors="coerce").astype("Int64")
        data_frames_cp["Year"] = pd.to_numeric(data_frames_cp["Year"], errors="coerce").astype("Int64")
        data_frames_cp["VHI"] = pd.to_numeric(data_frames_cp["VHI"], errors="coerce")
        
        data_frames_cp.loc[:, "Region_ID"] = data_frames_cp["Region_ID"].replace(region_mapping)
        print("Індекси областей успішно оновлені!")
    else:
        print("!!! Помилка: у DataFrame немає колонки 'Region_ID'")

    return data_frames_cp