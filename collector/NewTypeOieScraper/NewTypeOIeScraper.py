import requests, json, datetime
from NewTypeScraper import OieSubCrawler
import re, os
import sqlite3, warnings
import pandas as pd
from tqdm import tqdm
from oiescraper_kor import translate_oie_reports
from oiescraper_totalhead import totalhead
import time
import xlsxwriter

def get_oie_data():

    '''
    보고서 목록을 최근 100개에 대해 추출하고, 각각의 보고서 목록 아이디를 크롤러에 삽입하는 함수 생성
    '''

    url = 'https://wahis.oie.int/pi/getReportList'

    today = datetime.datetime.now()
    period = datetime.timedelta(days=7)
    weekago = today-period
    # today_str = today.strftime("%Y-%m-%d")
    # weekago_str = weekago.strftime("%Y-%m-%d")

    today_str = today.strftime("%Y-%m-%d")
    weekago_str = '2001-01-01'

    data = {"pageNumber":1,"pageSize":100,"searchText":"",
            "sortColName":"","sortColOrder":"ASC",
            "reportFilters":{"reportDate":{"startDate":"{}".format(weekago_str),"endDate":"{}".format(today_str)}},
            "languageChanged":False}

    response = requests.post(url, data=json.dumps(data))

    OutBreakJson = response.json()
    _weekList_ = OutBreakJson.get('homePageDto')
    time.sleep(2)

    # 보고서 번호 추출
    want_linknumbers = []
    print('최근 7일간 보고서 번호를 추출하고 있습니다')

    for i in _weekList_:
        number = i['reportInfoId']
        want_linknumbers.append(number)


    con = sqlite3.connect('oie_reports.db')

    # 기존 db의 링크번호 가져옴
    try:
        linknumber_db_df = pd.read_sql("SELECT [링크 번호] FROM oie_reports_kr", con)  # []: 칼럼명이나 테이블명에 공백이 있을 때
        linknumber_db_df.drop_duplicates(inplace=True)

        linknumber_db_series = linknumber_db_df['링크 번호'].astype(str)  # 숫자형식을 문자형식으로 바꿈

    except: linknumber_db_series = []

    new_linknumbers = []
    oie_reports = pd.DataFrame()

    for want_linknumber in want_linknumbers:
        want_linknumber = str(want_linknumber)
        if want_linknumber not in list(linknumber_db_series):
            new_linknumbers.append(want_linknumber)

    '''새로 올라온 리포트의 데이터 추출'''

    print('총 보고서 중 중복되지 않는 보고서만 추출중입니다.\n잠시만 기다려주세요.\n새 보고서는 {}개입니다'.format(len(new_linknumbers)))

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


        else:
            print('발생건이 없습니다')

        BOT.clear()
        time.sleep(1.5)
        print('-'*30)

    # 뽑아낸 총 프레임에 발생건이 한건도 포함되지 않는 경우, 예외처리 필요함
    try:
        want_columns = ['Link number',
                        'Disease', 'Country',
                        'Serotype', 'Report date',
                        'Number of outbreaks', 'Date of start of the outbreak',
                        'Region', 'Epidemiological unit',
                        'SPECIES', 'SUSCEPTIBLE', 'CASES', 'DEATHS',
                        'Killed and disposed of', 'Slaughtered/Killed for commercial use',
                        'VACCINATED', 'Movement control inside the country',
                        'Vaccination in response to the outbreak (s)',
                        'Surveillance outside containment and or the protection zone',
                        'Surveillance within containment and or the protection zone', 'Screening',
                        'Traceability', 'Quarantine',
                        'Official destruction of animal products',
                        'Official disposal of carcasses, by-products and waste',
                        'Process to inactivate the pathogenic agent in products or by-products', 'Stamping out',
                        'Selective killing and disposal', 'Control of wildlife reservoirs',
                        'Zoning', 'Disinfection',
                        'Disinfestation', 'Control of vectors',
                        'Vector surveillance', 'Ante and post-mortem inspections',
                        'Vaccination permitted (if a vaccine exists)', 'Vaccination prohibited',
                        'No treatment of affected animals', 'Treatment of affected animals',
                        'Slaughter', 'affected_population',
                        'Causal agent', 'report_type', 'report_ID']

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


    except:
        print("금일 총 발생건이 없거나, 네트워크 문제가 있을 수 있습니다")


if __name__ == '__main__':
    get_oie_data()