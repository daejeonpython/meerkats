import requests, json, time
import pandas as pd

class OieSubCrawler:

    def __init__(self):
        self.total_dict = {}
        self.response = None
        self.specifics_list = []
        self.want_list_ = []
        self.measure_df = None
        self.page_df = pd.DataFrame()
        self.linknumber = None

    def OieSubPage(self,linknumber):
        # URL 설정. 해당 데이터로 report ID만 넘어오도록 설정
        
        self.linknumber = linknumber
        url = 'https://wahis.oie.int/pi/getReport/{}'.format(str(linknumber))

        self.response = requests.get(url)
        if self.response.status_code == 204:
            print(f'{linknumber} 번은 204코드로 내용이 없는 것으로 판단됩니다')
            return self.page_df

        #JSON으로 변환해서 데이터 받기
        submit_JSON = self.response.json()

        # 일반 발생 건에 대한 데이터 추출하기 및 데이터프레임으로 변환하기
        if self.response.status_code == 400:
            print(f'{linknumber} 번은 서버 이상으로 판단됩니다')
            return self.page_df

        general = submit_JSON.get('generalInfoDto')

        if general == None:
            print(f'보고서 {linknumber}번의 세부발생정보 확인불가')
            return self.page_df

        report = submit_JSON['reportDto']

        if general['isAquatic'] == True:
            print(f'{linknumber} 번은 수생동물 발생건으로 판단됩니다')
            return self.page_df

        ''' 
        
        전체 (total) 데이터를 추출하는 코드
        
        '''

        # 링크넘버 추출
        self.total_dict['Link number'] = self.linknumber

        # 질병명 추출

        if general.get('diseaseName') == None:
            print(f'보고서 {linknumber}번의 세부발생정보 확인불가')
            return self.page_df

        self.total_dict['Disease'] = general['diseaseName']

        # 국가명 추출
        self.total_dict['Country'] = general['countryOrTerritory']

        # 보고일 추출
        self.total_dict['Report date'] = general['reportDate']
        self.total_dict['Report date'] = self.total_dict['Report date'].split('T')[0]

        #보고서 타입 추출(긴급 또는 추가 발생 등)
        self.total_dict['report_type'] = report['reportTitle']
        self.total_dict['report_ID'] = report['reportId']

        #원인체 추출
        self.total_dict['Causal agent'] = general['casualAgent']
        self.total_dict['Serotype'] = general.get('diseaseType',None)

        # 방역조치사항 추출하기
        livestock, wild = submit_JSON.get('eventCmDto',[{},{}])
        measure_All_list = list(set(livestock.get('cmApplied',"") + wild.get('cmApplied',"")))
        measure_list = [i.strip() for i in measure_All_list] # 앞뒤 빈칸을 삭제하기 위한 리스트_컴프리헨션

        # 세부발생조치 추출하기 // 보고서별로 세부 발생정보가 없는 경우 조기리턴으로 처리 -- 어렵다. ㅠㅠ
        test_specific_outbreak = submit_JSON.get('eventOutbreakDto')
        if test_specific_outbreak == None:
            print(f'보고서 {linknumber}번의 세부발생정보 확인불가')
            return self.page_df

        specific_outbreak = submit_JSON['eventOutbreakDto']['outbreakMap']
        specific_ID_keys = list(specific_outbreak.keys())


        # 발생건이 있는 경우만 append한 want_list 생성


        for j,i in enumerate(specific_ID_keys):
            specified_list_ = specific_outbreak[str(i)].get('speciesDetails')
            sub_list_ = []
            if specified_list_ == None:
                pass
            else:
                for idx,elem in enumerate(specified_list_):
                    if elem.get('spicieName') != None:
                        search_elem = [elem.get('susceptible'),elem.get('cases'),elem.get('deaths'),elem.get('killed'),elem.get('slaughtered'),elem.get('vaccinated')]
                        if any(search_elem) >= 1:  #해당 값 중 하나라도 0보다 큰 값이 확인되는 경우, 해당 건을 발생건으로 본다
                            if elem.get('vaccinated') == None: ## vaccinated값이 없는 경우를 채우기 위함
                                elem['vaccinated'] = 0
                            if elem.get('susceptible') == None:  ##susceptible값이 없는 경우를 채우기 위함
                                elem['susceptible'] = 0
                            if elem.get('slaughtered') == None:  ##susceptible값이 없는 경우를 채우기 위함
                                elem['slaughtered'] = 0
                            else: pass
                            sub_list_.append(elem)
                    else:
                        pass


            self.want_list_.append(sub_list_) ## 세부 리스트를 want_list에 담기

        number = []

        for i, j in enumerate(self.want_list_):
            if len(j) != 0:
                number.append(i)
        print('{}번 보고서의 {}개 세부보고서 중 {}개 세부보고서가 새로운 건으로 추정됩니다'.format(self.linknumber, len(specific_ID_keys), len(number)))

        # 발생건별 세부사항 추출하기

        for i in specific_ID_keys:
            check_num = specific_ID_keys.index(i)
            if check_num not in number:
                self.specifics_list.append([])
            else:
                specific_dict = {}
                _list_ = specific_outbreak[str(i)]
                time.sleep(1)

                # 발생지역 정리
                region = '{}, {}, {}, {}'.format(_list_.get('location'), _list_.get('thirdAdmDivision'), _list_.get('secondAdmDivision'),_list_.get('firstAdmDivision'))
                specific_dict['Region'] = region.replace(" None,","").strip(', ')
                # 세부 발생건 수 입력
                if _list_.get('isCluster') != False:
                    specific_dict['Number of outbreaks'] = _list_.get('noOfOutbreaks')
                else:
                    specific_dict['Number of outbreaks'] = "1"

                # 세부 축종 입력
                specific_dict['affected_population'] = _list_.get('affectedDesc')

                # 발생일 정보 입력
                specific_dict['Date of start of the outbreak'] = _list_['outbreakStartDate']

                # 역학단위(구분)자 입력
                specific_dict['Epidemiological unit'] = _list_['epiUnitType']

                # 발생위경도 입력
                specific_dict['Geolocation'] = str(_list_['geographicCoordinates'])


                self.specifics_list.append(specific_dict)


        want_mod_list =  [i for i in self.want_list_ if i!=[]]
        specific_mod_list = [i for i in self.specifics_list if i!=[]]


        want_columns = ['spicieName','susceptible','cases','deaths',
                        'killed','slaughtered','vaccinated','Number of outbreaks',
                        'affected_population','Date of start of the outbreak','Epidemiological unit']

        specific_total = pd.DataFrame()
        # print('취합 보고서를 표로 변환 중입니다. 10건 이상의 경우 시간이 소요됩니다')
        if len(specific_mod_list) == 0:
            pass
        else:
            for i,j in zip(want_mod_list,specific_mod_list):
                i_df = pd.DataFrame(i)
                j_df = pd.DataFrame.from_dict(j,orient = 'index').T ## geolocation의 값을 2행으로 잡는 문제를 해결하기 위함.
                x = pd.concat([i_df,j_df],axis=1)
                specific_total = specific_total.append(x,ignore_index=True)

            new_column_dict = {'spicieName':'SPECIES','susceptible':'SUSCEPTIBLE', 'cases':'CASES',
                            'deaths':'DEATHS', 'killed':'Killed and disposed of', 'slaughtered':'Slaughtered/Killed for commercial use',
                            'vaccinated':'VACCINATED','affected_population':'affected_population',
                            'Date of start of the outbreak':'Date of start of the outbreak','Epidemiological unit':'Epidemiological unit'}

            # specific_total = specific_total[want_columns]
            specific_total.rename(columns = new_column_dict, inplace = True)

            # 조치사항 전체 목록
            measure_header = ['Movement control inside the country', 'Vaccination in response to the outbreak (s)',
                              'Surveillance outside containment and or the protection zone',
                              'Surveillance within containment and or the protection zone', 'Screening', 'Traceability',
                              'Quarantine', 'Official destruction of animal products',
                              'Official disposal of carcasses, by-products and waste',
                              'Process to inactivate the pathogenic agent in products or by-products', 'Stamping out',
                              'Selective killing and disposal', 'Control of wildlife reservoirs', 'Zoning',
                              'Disinfection', 'Disinfestation', 'Control of vectors', 'Vector surveillance',
                              'Ante and post-mortem inspections',
                              'Vaccination permitted (if a vaccine exists)', 'Vaccination prohibited',
                              'No treatment of affected animals', 'Treatment of affected animals', 'Slaughter']

            # 위 칼럼명으로 된 빈 df 만들어 놓음
            self.measure_df = pd.DataFrame(index=range(0, len(specific_total)), columns=measure_header)

            try:
                for measure in measure_header:

                    if measure in measure_list:
                        self.measure_df[measure] = 'Y'
                    else:
                        continue
            except:
                print('방역조치가 없습니다!')

            total_df = pd.DataFrame(self.total_dict,index=[0])


            self.page_df = pd.concat([total_df,specific_total,self.measure_df],axis=1)
            self.page_df.iloc[:,0:7] = self.page_df.iloc[:,0:7].fillna(method='ffill')
            self.page_df[['Region','Serotype','Date of start of the outbreak','Epidemiological unit']] = self.page_df[['Region','Serotype','Date of start of the outbreak','Epidemiological unit']].fillna(method='ffill')
            self.page_df['Serotype'] = self.page_df['Serotype'].apply(lambda x:"-" if x == '' else x)



        return self.page_df

    def clear(self):
        self.total_dict = {}
        self.response = None
        self.specifics_list = []
        self.want_list_ = []
        self.measure_df = None
        self.page_df = None





if __name__ == '__main__':
    Bot = OieSubCrawler()
    Bot.OieSubPage(37986)
