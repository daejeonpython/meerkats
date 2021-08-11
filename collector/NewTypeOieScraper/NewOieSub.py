from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup
import os


class OieSubPage:
    def __init__(self):
        self.result = []
        self.result_concate = []
        self.driver = webdriver.Chrome('./driver/chromedriver.exe')
        self.driver.implicitly_wait(3)
        self.total_dict = {}
        self.specific_outbreak = None
        self.measure_df = None
        self.link_number = ""
        self.sub_total = None
        self.specific_linknumber = []
        self.modified_concate = []

    def driver_maker(self,link_number):
        self.link_number = link_number
        '''
        크롬 웹드라이버 생성 및 페이지 창 열기 작업용 함수
        '''
        url = 'https://wahis.oie.int/#/report-info?reportId={}'.format(str(self.link_number))
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "summary-bottom-detail")))
        element = self.driver.find_element_by_xpath("//*[@class='expand-all']")
        self.driver.execute_script('arguments[0].click();',element)
        time.sleep(1)


    def table_data(self,result):
        self.driver.find_elements_by_class_name("species-name") # 테이블 태그를 모두 추출하기 위한 driver 탐색 구문
        time.sleep(1)
        self.result = self.driver.page_source
        # 세부 테이블 정보만 불러오는 함수
        result = self.result
        try:
            self.df = pd.read_html(result, flavor='lxml')[2:]
        except:
            print('발생건이 없습니다')

        #
        for idx, df_ in enumerate(self.df):
            a_list = df_.columns
            if a_list[0]!='SPECIES':
               pass
            else:
                b = df_[(df_['SPECIES'] != '-') & (df_['Unnamed: 1'] == 'NEW')]
                self.result_concate.append(b)

        for i,j in enumerate(self.result_concate):
            if j['SUSCEPTIBLE'][0] == '-' and j['CASES'][0] == '-' and j['DEATHS'][0] == '-':
                pass
            else:
                self.specific_linknumber.append(str(i+1))
                self.modified_concate.append(j)


        if len(self.modified_concate) == 1:
            self.specific_outbreak = self.modified_concate[0]

        elif len(self.modified_concate) == 0:
            pass

        else:
            self.specific_outbreak = pd.concat(self.modified_concate)
            self.specific_outbreak.reset_index(inplace=True)


        self.driver.find_elements_by_class_name("reporter-summary-data-key")  # 테이블 태그를 모두 추출하기 위한 driver 탐색 구문
        time.sleep(1)
        result = self.driver.page_source
        soup = BeautifulSoup(result, 'html.parser')
        number = len(soup.find_all("div", {"class": "obt-header"})) + 1 ##세부 항목정보의 개수를 확인하기 위함(반복문 사용 기준)
        report_type = soup.select_one('.report-number-section > div.report-number')
        report_id = soup.select_one(
            '.reporter-summary-wrap > div > div:nth-child(2) > div:nth-child(1) > div.reporter-summary-data-val>span')
        country = soup.select_one('.report-number-section > div.report-desc')
        sero_exist = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(1) > span.title')

        serotype = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(1) > span.detail')
        causal_agent = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(4) > span:nth-child(2)')
        if causal_agent == None:  # causal_agent를 None으로 반환시, 다음 child 검색
            causal_agent = soup.select_one(
                '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(3) > span:nth-child(2)')
        else:
            pass

        report_date = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(3) > p:nth-child(3) > span.detail')
        step_titles = self.driver.find_elements_by_class_name("step-title")

        ## 세부 발생건수를 확인하기 위해, 세부 발생정보의 위치를 추적하는 리스트 생성 후, 'Outbreak'위치를 반환하도록 index로 찾기

        step_title_list = [i.text for i in step_titles]
        time.sleep(1)
        t = step_title_list.index('Outbreaks') + 2 ##'outbreaks'의 위치를 찾은 후에, 0부터 시작하니까 +1해주고, 시작항목은 outbreaks의 내부항목이므로, 다시 하나 더 들어가서 +1 해주기


        # 방역조치 추출하기
        measure = soup.select_one(
            '.stepSummary-container > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(1) > p > span.detail >span')

        '''
        조치사항 박스
            - 이를 위 summary_발생 건 df와 결합하여 최종 df 완성
        '''

        # 조치사항 전체 목록
        measure_header = ['Movement control inside the country', 'Vaccination in response to the outbreak (s)',
                          'Surveillance outside containment and or protection zone',
                          'Surveillance within containment and or protection zone', 'Screening', 'Traceability',
                          'Quarantine', 'Official destruction of animal products',
                          'Official disposal of carcasses, by-products and waste',
                          'Process to inactivate the pathogenic agent in products or by-products', 'Stamping out',
                          'Selective killing and disposal', 'Control of wildlife reservoirs', 'Zoning',
                          'Disinfection', 'Disinfestation', 'Control of vectors', 'Vector surveillance',
                          'Ante and post-mortem inspections',
                          'Vaccination permitted (if a vaccine exists)', 'Vaccination prohibited',
                          'No treatment of affected animals', 'Treatment of affected animals', 'Slaughter']

        # 위 칼럼명으로 된 빈 df 만들어 놓음
        self.measure_df = pd.DataFrame(index=range(0, len(self.specific_linknumber)), columns=measure_header)

        try:
            measure_text = measure.findAll('p')
            measure_proto = [i.text for i in measure_text]
            measure_list = list(map(lambda x: x.strip().lstrip('[-]').strip(), measure_proto))
            for measure in measure_header:

                if measure in measure_list:
                    self.measure_df[measure] = 'Y'
                else:
                    continue

        except: print('방역조치가 없습니다!')


        # 세부 발생정보에 관한 데이터 모음
        specific_list = []
        for j,i in enumerate(self.specific_linknumber):
            specific_dict = {}
            print(f'보고서:{self.link_number}의 {len(self.specific_linknumber)}개 세부보고서 중 {j+1}번째 데이터를 수집중입니다')

            self.driver.find_elements_by_class_name("stepSummary-container > div:nth-child(" + str(
                t) + ") > div > div.outbreak-wrapper > div:nth-child(" + str(
                i) + ") > div.bottom-detail-container > div:nth-child(1) > div")  # refresh해서 세부사항이 담긴 class를 소환

            outbreak_date = soup.select_one('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(1) > p:nth-child(2) > span.detail')

            epidimiological_unit = soup.select_one('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(1) > p:nth-child(3) > span.detail')

            number_of_outbreak = soup.select_one(('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(2) > p:nth-child(1) > span.detail'))

            affected_population = soup.select_one(('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(2) > p:nth-child(3) > span.detail'))

            first_div = soup.select_one('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(1) > span.detail')
            second_div = soup.select_one('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(2) > span.detail')
            third_div = soup.select_one('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(3) > span.detail')
            fourth_div = soup.select_one('.stepSummary-container > div:nth-child(' + str(
                t) + ') > div > div.outbreak-wrapper > div:nth-child(' + str(
                i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(2) > p:nth-child(4) > span.detail')

            self.driver.find_elements_by_class_name("stepSummary-container > div:nth-child(" + str(
                t) + ") > div > div.outbreak-wrapper > div:nth-child(" + str(
                i) + ") > div.bottom-detail-container > div:nth-child(1) > div")  # refresh해서 세부사항이 담긴 class를 소환

            specific_dict['Date of start of the outbreak'] = outbreak_date.text

            if second_div.text == '-' and third_div.text == '-':
                specific_dict['Region'] = '{},{}'.format(fourth_div.text,first_div.text)
            elif fourth_div.text == '-':
                specific_dict['Region'] = '{},{},{}'.format(third_div.text, second_div.text,first_div.text)
            elif third_div.text == '-':
                specific_dict['Region'] = '{},{},{}'.format(fourth_div.text, second_div.text,first_div.text)
            elif second_div.text == '-':
                specific_dict['Region'] = '{},{},{}'.format(fourth_div.text,third_div.text,first_div.text)
            else:
                specific_dict['Region'] = '{},{},{},{}'.format(fourth_div.text,third_div.text,second_div.text,first_div.text)

            specific_dict['Epidemiological unit'] = epidimiological_unit.text

            if number_of_outbreak.text != '-':
                specific_dict['Number of outbreaks'] = number_of_outbreak.text
            else:
                specific_dict['Number of outbreaks'] = "1"

            specific_dict['affected_population'] = affected_population.text

            specific_list.append(specific_dict)


        self.total_dict['Link number'] = self.link_number

        # 전체 질병명에서 질병명과 국가명을 분리 (split함)
        self.total_dict['Disease'] = country.text.split(',')[0]
        self.total_dict['Country'] = country.text.split(',')[1]
        if sero_exist.text == 'Genotype/ serotype/ subtype':  ##serotype이 있는지를 확인하고 없으면 공란을 반환
            self.total_dict['Serotype'] = serotype.text
        else:
            self.total_dict['Serotype'] = ""
        self.total_dict['Report date'] = report_date.text

        self.total_dict['report_type'] = report_type.text
        self.total_dict['report_ID'] = report_id.text
        self.total_dict['Causal agent'] = causal_agent.text

        Total_df = pd.DataFrame(self.total_dict, index=[0])
        if len(specific_list) == 1:
            specific_total = specific_list[0]
            specific_df = pd.DataFrame(specific_total, index=[0])
            self.sub_total = pd.concat([Total_df, specific_df], axis=1)
            try:
                self.sub_total = self.sub_total.fillna(method='ffill')
            except:
                pass

        elif len(specific_list) == 0:
            pass

        else:
            specific_total = pd.DataFrame(specific_list)
            self.sub_total = pd.concat([Total_df, specific_total], axis=1)
            self.sub_total = self.sub_total.fillna(method='ffill')


        '''
        self.sub_total = 발생건별 정리본
        self.measure_df = 조치사항 정리본
        self.specific_outbreak = 발생건 별 사육,폐사,살처분 정리표
        '''
        self.page_df = pd.concat([self.sub_total,self.specific_outbreak,self.measure_df], axis=1)
        self.page_df.reset_index()
        self.page_df.iloc[:,0:11] = self.page_df.iloc[:,0:11].fillna(method='ffill')

        return  self.page_df

    def driver_close(self):
        self.driver.close()

    def driver_quit(self):
        self.driver.quit()

    def _reset_(self):
        self.result = []
        self.result_concate = []
        self.total_dict = {}
        self.specific_outbreak = None
        self.link_number = ""
        self.sub_total = None
        self.sub_total_merge = None
        self.specific_linknumber = []
        self.modified_concate = []



if __name__ == '__main__':
    a = OieSubPage()
    b = a.driver_maker(30661)
    c = a.table_data(b)