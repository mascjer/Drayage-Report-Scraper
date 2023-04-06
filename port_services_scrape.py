import pandas as pd
import numpy as np
from dash import html
import base64
import io
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from time import sleep
import datetime as dt
from datetime import datetime

pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)
#options = webdriver.EdgeOptions()
options = Options()
options.add_argument("headless")
options.add_experimental_option('excludeSwitches', ['enable-logging'])


url = 'http://webaccess.gaports.com/express/secure/Today.jsp?Facility=GCT'
user_id = 'inorberg'
password = 'ni2396'


def login(browser, user_id, password):

    try:
        wait = WebDriverWait(browser,10)
        login = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table/tbody/tr[2]/td/input").send_keys(user_id)
        sleep(1)
        password = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table/tbody/tr[4]/td/input").send_keys(password)
        sleep(1)
        submit = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table/tbody/tr[9]/td/center/button").click()
        sleep(1)
        containers = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[1]/td/div/table[2]/tbody/tr/td[1]/table/tbody/tr/td/a[3]").click()
        avl_inq = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/div/table/tbody/tr[2]/td/a").click()

    except TimeoutException:
        print("Trying to find the given element but unfortunately no element is found")
    sleep(5)

    return browser


def get_visible_cont(browser, df):
    pieces = []
    status = df['Status'].iloc[0]
    split_df_num = np.ceil(len(df)/50).astype(int)
    print('Number of Visible Containers to Scrape: ', len(df))
    for i in range(split_df_num):
        temp_df = dataframe_splitter(df,i)
        print('Temp DF Num: ', i+1)
        eqt_ids = browser.find_element("xpath","/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table[2]/tbody/tr[2]/td/form/table[1]/tbody/tr[1]/td[2]/textarea").clear()
        eqt_ids = browser.find_element("xpath","/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table[2]/tbody/tr[2]/td/form/table[1]/tbody/tr[1]/td[2]/textarea")
        for index, row in temp_df.iterrows():
            eqt_ids.send_keys(str(row["Container"]) + '\n')
        
        sumbit = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table[2]/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td/button").click()
        
        table = pd.read_html(browser.find_element(By.ID,"Table1").get_attribute('outerHTML'))[0]
        table.columns = ['AVAILABLE','EQUIP ID','PORT LFD','PORT PTD','PORT GTD','LOCATION','FACILITY','LINE STATUS','CUSTOM STATUS','AGRI STATUS','B/L NBR','OTHER HOLDS']
        table['Status'] = status
        pieces.append(table)
        #sleep(2)
    
    df_final = pd.concat(pieces, ignore_index = True)
    df_final = df_final.loc[df_final['EQUIP ID'] != 'No items found for this table.']
    #df_final = df_final[~df_final['LOCATION'].astype(str).str.startswith('V-')]
    df_final['is_visible'] = 'Y'

    return df_final


def transform_data(df):

    excel_data = df.loc[df['Port'] == 'Savannah']

    on_water = excel_data.loc[excel_data['Status'] == 'On the Water']
    on_water = on_water[(on_water['OTW ETA'] >  '1900-1-1'  ) & (on_water['OTW ETA'] <= datetime.strptime(str(datetime.today() + dt.timedelta(days=7)), '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d"))].reset_index()

    at_port = excel_data.loc[excel_data['Status'] == 'At Port'].reset_index()
    full_yard = excel_data.loc[excel_data['Status'] == 'Full In Yard'].reset_index()
    empty_yard = excel_data.loc[excel_data['Status'] == 'Empty In Yard'].reset_index()
    returned = excel_data.loc[excel_data['Status'] == 'Returned'].reset_index()

    frames_all = [on_water,at_port,full_yard,empty_yard,returned]
    all_containers = pd.concat(frames_all)

    #all_containers = all_containers.loc[all_containers['Container'].isin(['HMMU6271273','HMMU6271273', 'IMTU1051570'])]

    return all_containers


def dataframe_splitter(df,i):
    lower_bound = i*50
    upper_bound = (i*50)+49
    temp_df = df.iloc[lower_bound:upper_bound,:]
    print('Scraping Containers: ', lower_bound+1, ' to ', len(temp_df)+lower_bound+1)
    return temp_df
        

def get_container_history(browser, df):
    container_hist = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/div/table/tbody/tr[5]/td/a").click()

    df['available_date'] = None
    df['full_out_date'] = None
    df['empty_in_date'] = None

    num = len(df)

    for i in range(len(df)):
        os.system('cls')
        eqt_ids = browser.find_element("xpath","/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table[2]/tbody/tr/td/form/table[1]/tbody/tr/td[2]/input").clear()
        eqt_ids = browser.find_element("xpath","/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table[2]/tbody/tr/td/form/table[1]/tbody/tr/td[2]/input")
        eqt_ids.send_keys(df['Container'].iloc[i])
        submit = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/div/div/table[2]/tbody/tr/td/form/table[2]/tbody/tr[2]/td/button").click()

        available_date, full_out_date, empty_in_date = scrape_container_history_table(browser)

        if available_date is None and empty_in_date is not None and full_out_date is not None:
            empty_in_date = np.NaN
            full_out_date = np.NaN
        else:
            empty_in_date = empty_in_date
            full_out_date = full_out_date

        if empty_in_date is not None and available_date is not None and available_date > empty_in_date:
            empty_in_date = np.NaN

        if full_out_date is not None and available_date is not None and available_date > full_out_date:
            full_out_date = np.NaN

        pd.set_option('mode.chained_assignment', None)
        df['available_date'].iloc[i] = available_date
        df['full_out_date'].iloc[i] = full_out_date
        df['empty_in_date'].iloc[i] = empty_in_date

        print(i+1, ' of ', num, ' container histories examined')

        return_to_cont_hist = browser.find_element("xpath", "/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/div/table/tbody/tr[5]/td/a").click()

    df['available_date'] = df['available_date'].astype('datetime64[ns]')
    df['full_out_date'] = df['full_out_date'].astype('datetime64[ns]')
    df['empty_in_date'] = df['empty_in_date'].astype('datetime64[ns]')
    df['OTW ETA'] = df['OTW ETA'].astype('datetime64[ns]')

    df['available_date'] = df['available_date'].dt.date
    df['full_out_date'] = df['full_out_date'].dt.date
    df['empty_in_date'] = df['empty_in_date'].dt.date
    df['Transload Received'] = df['Transload Received'].dt.date
    df['OTW ETA'] = df['OTW ETA'].dt.date
    
    return df


def scrape_container_history_table(browser):
    table = pd.read_html(browser.find_element(By.ID,"Table1").get_attribute('outerHTML'))[0]

    #( 'Unit line exists: ', (table.Service == 'UNIT_LINE_AVAILABLE').any())
    if (table.Service == 'UNIT_CTR_AVAILABLE').any() == False:
        available_date = None
    else:
        avail_df = table.loc[table.Service == 'UNIT_CTR_AVAILABLE']
        available_date = avail_df.Date.iloc[0]
        available_date = datetime.strptime(available_date, '%m/%d/%y %I:%M:%S %p')
        #print(available_date)

    #print( 'Full Out Exists: ', (table.Service == 'FULL_OUT').any())
    if (table.Service == 'FULL_OUT').any() == False:
            if (table.Service == 'UNIT_OUT_RAIL').any() == False:
                full_out_date = None
            else:
                full_out_df = table.loc[table.Service == 'UNIT_OUT_RAIL']
                full_out_date = full_out_df.Date.iloc[0]
                full_out_date = datetime.strptime(full_out_date, '%m/%d/%y %I:%M:%S %p')
                #print(full_out_date)
    else:
        full_out_df = table.loc[table.Service == 'FULL_OUT']
        full_out_date = full_out_df.Date.iloc[0]
        full_out_date = datetime.strptime(full_out_date, '%m/%d/%y %I:%M:%S %p')
        #print(full_out_date)

    #print( 'Empty In Exists: ', (table.Service == 'EMPTY_IN').any())
    if (table.Service == 'EMPTY_IN').any() == False:
        if (table.Service == 'UNIT_IN_RAIL').any() == False:
            empty_in_date = None
        else:
            empty_in_df = table.loc[table.Service == 'UNIT_IN_RAIL']
            empty_in_date = empty_in_df.Date.iloc[0]
            empty_in_date = datetime.strptime(empty_in_date, '%m/%d/%y %I:%M:%S %p')
            #print(empty_in_date)
    else:
        empty_in_df = table.loc[table.Service == 'EMPTY_IN']
        empty_in_date = empty_in_df.Date.iloc[0]
        empty_in_date = datetime.strptime(empty_in_date, '%m/%d/%y %I:%M:%S %p')
        #print(empty_in_date)

    return available_date, full_out_date, empty_in_date


def new_status(df):

    df['new_status'] = np.nan
    pd.set_option('mode.chained_assignment', None)

    for i in range(len(df)):
        if(df.is_visible.iloc[i] != 1 and pd.notna(df.empty_in_date.iloc[i])):
            new_status = 'Returned' 
        elif(pd.isna(df.empty_in_date.iloc[i]) and pd.notna(df['Transload Received'].iloc[i])):
            new_status = 'Empty In Yard' 
        elif(pd.isna(df['Transload Received'].iloc[i]) and pd.notna(df.full_out_date.iloc[i])):
            new_status = 'Full In Yard'
        elif(pd.isna(df.full_out_date.iloc[i]) and pd.notna(df.available_date.iloc[i])):
            new_status = 'At Port' 
        elif pd.isna(df.available_date.iloc[i]):
            new_status = 'On the Water'
        else:
            new_status = 'ERROR'

        df['new_status'].iloc[i] = new_status

    return df


def parse_data(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "xlsx" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")

        df = transform_data(df)
        return df

    except Exception as e:
        error_string = "There was an error processing this file."
        return error_string



'''def main():

    file_name = 'C:/Users/MASCJER/Downloads/Kroger Drayage Report -ad.xlsx'
    sheet_name = 'Active'

    all_containers = get_data(file_name, sheet_name)
    #all_containers = all_containers.head(100)

    browser = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    browser.maximize_window()

    browser.get(url)


    browser = login(browser, user_id, password)
    visible_containers = get_visible_cont(browser, all_containers)

    visible_containers = visible_containers.drop(columns=['Status'])

    all_containers = get_container_history(browser,all_containers)
    all_containers = pd.merge(left=all_containers, right=visible_containers, how='left', left_on='Container', right_on='EQUIP ID')
    all_containers = all_containers[['Container', 'OTW ETA', 'Status', 'Transload Received','LOCATION', 'available_date', 'full_out_date', 'empty_in_date', 'is_visible']]
    all_containers = new_status(all_containers)
    all_containers.to_csv('test.csv', index=False)

    #print(all_containers)

    print('Finished')
    sleep(2)

    browser.quit()


if __name__ == "__main__":
    main()'''

