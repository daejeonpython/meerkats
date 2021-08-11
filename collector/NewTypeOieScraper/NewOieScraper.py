
print('로딩 중입니다.\n')

from NewTypeScraper import OieSubCrawler
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import re,os
import sqlite3,warnings
import pandas as pd
from tqdm import tqdm
from oiescraper_kor import translate_oie_reports
from oiescraper_totalhead import totalhead
import time
from bs4 import BeautifulSoup

def get_oie_data():
    '''
    각 report의 링크를 목록화
    '''

    # Webdriver에서 네이버 페이지 접속
    dr = webdriver.Chrome('./driver/chromedriver.exe')

    try:
        dr.get('https://wahis.oie.int/#/events')
        WebDriverWait(dr, 10).until(lambda x: x.find_element_by_class_name('filled-in childCheck'))
    except: pass
    finally:
        soup = BeautifulSoup(dr.page_source,'html.parser')
        k = str(soup.findAll('label'))
        want_linknumbers = re.findall(r'[0-9]{5}',k)
        print(want_linknumbers)
    dr.quit()
    con = sqlite3.connect('oie_reports.db')

    # 기존 db의 링크번호 가져옴
    # try:
    #     linknumber_db_df = pd.read_sql("SELECT [링크 번호] FROM oie_reports_kr", con)  # []: 칼럼명이나 테이블명에 공백이 있을 때
    #     linknumber_db_df.drop_duplicates(inplace=True)
    #
    #     linknumber_db_series = linknumber_db_df['링크 번호'].astype(str)  # 숫자형식을 문자형식으로 바꿈
    #
    # except: pass

    new_linknumbers = []
    oie_reports = pd.DataFrame()

    for want_linknumber in want_linknumbers:

        new_linknumbers.append(want_linknumber)

    '''새로 올라온 리포트의 데이터 추출'''

    print('데이터를 추출하고 있습니다.\n잠시만 기다려주세요.\n')


    for new_linknumber in tqdm(new_linknumbers):  # tqdm: 반복문에서의 리스트 원소 수를 백분율로 나타내어 진행표시줄을 만듦
        BOT = OieSubCrawler()
        # 서버 오류로 인해 timeout 에러가 났을 때 회피
        try:
            oie_report = BOT.OieSubPage(new_linknumber)

        except TimeoutError:
            new_error_linknumbers.append(new_linknumber)
            break

        if len(oie_report.index) != 0:
        # 추출한 데이터 및 링크번호 추가, 발생건이 하나도 확인되지 않는 df는 버림
            oie_reports = oie_reports.append(oie_report, ignore_index=True)  # df.append 사용 시 무조건 ignore_index=True!


        else: print('발생건이 없습니다')

        BOT.clear()
        time.sleep(1)

    want_columns = ['Link number',
                    'Disease','Country',
                    'Serotype','Report date',
                    'Number of outbreaks','Date of start of the outbreak',
                    'Region','Epidemiological unit',
                    'SPECIES','SUSCEPTIBLE','CASES','DEATHS',
                    'Killed and disposed of','Slaughtered/Killed for commercial use',
                    'VACCINATED','Movement control inside the country',
                    'Vaccination in response to the outbreak (s)','Surveillance outside containment and or the protection zone',
                    'Surveillance within containment and or the protection zone','Screening',
                    'Traceability','Quarantine',
                    'Official destruction of animal products','Official disposal of carcasses, by-products and waste',
                    'Process to inactivate the pathogenic agent in products or by-products','Stamping out',
                    'Selective killing and disposal','Control of wildlife reservoirs',
                    'Zoning','Disinfection',
                    'Disinfestation','Control of vectors',
                    'Vector surveillance','Ante and post-mortem inspections',
                    'Vaccination permitted (if a vaccine exists)','Vaccination prohibited',
                    'No treatment of affected animals','Treatment of affected animals',
                    'Slaughter','affected_population',
                    'Causal agent','report_type','report_ID']

    oie_reports = oie_reports[want_columns]
    trans_dfs = translate_oie_reports(oie_reports)

    # db 저장
    warnings.filterwarnings(action='ignore')  # 경고 메시지 안 띄우게 함. action='ignore': 무시 'default': 경고 발생 위치에 출력

    trans_dfs[0].to_sql('oie_reports', con, if_exists='append', index=False)
    trans_dfs[1].to_sql('oie_reports_kr', con, if_exists='append', index=False)

    # 총 두수 df
    totalhead_df = totalhead(trans_dfs[1])
    # 바탕화면에 엑셀파일 추출

    desktop_path = f'C:\\Users\\{os.getlogin()}\\Desktop\\'

    with pd.ExcelWriter(desktop_path + 'new_oie_reports.xlsx') as writer:
        trans_dfs[0].to_excel(writer, '원본', index=False)
        trans_dfs[1].to_excel(writer, '번역본', index=False)
        totalhead_df.to_excel(writer, '해동(총 두수)')


if __name__ == '__main__':
    get_oie_data()