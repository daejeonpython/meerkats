# coding = UTF-8

import re, sqlite3, datetime, pandas as pd
from country_continent_sort import country_match, continent_match
from disease_sort import disease_match
from species_sort import species_match, place_sort, place_species_sort, place_species_detail_sort, place_susceptible_sort


def translate_oie_reports(oie_reports):

    print('\n번역 중입니다.\n잠시만 기다려주세요.')
    
    kr_reports = oie_reports.copy()  # 복사. 원본 파일도 나중에 엑셀 파일로 저장할 것이므로 원본을 변형하지 않아야 함

    Dict = {"Link number": "링크 번호",
         "Disease": "질병",
         "Country": "국가",
         "Serotype": "혈청형",
         "Report date": "보고일",
         "report_type": "보고서 유형",
         "report_ID": "보고서 ID",
         "Causal agent": "원인체",
         "Date of start of the outbreak": "발생일",
         "Region": "발생 지역",
         "Epidemiological unit": "구분",
         "Number of outbreaks": "건수",
         "affected_population": "세부내역",
         "index": "인덱스번호",
         "SPECIES": "축종",
         "Unnamed: 1": "미번호 1",
         "MEASURING UNIT": "측정단위",
         "SUSCEPTIBLE": "사육",
         "CASES": "감염",
         "DEATHS": "폐사",
         "Killed and disposed of": "살처분",
         "Slaughtered/Killed for commercial use": "도축",
         "VACCINATED": "백신접종",
         "Unnamed: 9": "미번호 9",
         "Movement control inside the country": "국내이동제한",
         "Vaccination in response to the outbreak (s)": "발생대응예방접종",
         "Surveillance outside containment and or protection zone": "봉쇄지역 및/또는 보호지역 외 예찰",
         "Surveillance within containment and or protection zone": "봉쇄지역 및/또는 보호지역 내 예찰",
         "Screening":"스크리닝",
         "Traceability":"이력 추적",
         "Quarantine":"격리",
         "Official destruction of animal products": "동물성 생산물 공식처리",
         "Official disposal of carcasses, by-products and waste": "사체·부산물·폐기물 공식처리",
         "Process to inactivate the pathogenic agent in products or by-products": "생산물 또는 부산물 내 병원체 불활화 처리",
         "Stamping out":"살처분",
         "Selective killing and disposal": "선택적 살처분",
         "Control of wildlife reservoirs": "야생보균원 관리",
         "Zoning": "방역대 설정",
         "Disinfection": "소독",
         "Disinfestation": "해충구제",
         "Control of vectors": "야생매개체 관리",
         "Vector surveillance": "매개체 예찰",
         "Ante and post-mortem inspections": "생·해체검사",
         "Vaccination permitted (if a vaccine exists)": "백신접종 허용(백신이 있는 경우)",
         "Vaccination prohibited": "백신접종 금지",
         "No treatment of affected animals": "감염동물 미치료",
         "Treatment of affected animals": "감염동물 치료",
         "Slaughter": "도축*"}

    want_columns = ['Link number',
                    'Disease',
                    'Country',
                    'Serotype',
                    'Report date',
                    'Number of outbreaks',
                    'Date of start of the outbreak',
                    'Region',
                    'Epidemiological unit',
                    'SPECIES',
                    'SUSCEPTIBLE',
                    'CASES',
                    'DEATHS',
                    'Killed and disposed of',
                    'Slaughtered/Killed for commercial use',
                    'VACCINATED',
                    'Movement control inside the country',
                    'Vaccination in response to the outbreak (s)',
                    'Surveillance outside containment and or the protection zone',
                    'Surveillance within containment and or the protection zone',
                    'Screening',
                    'Traceability',
                    'Quarantine',
                    'Official destruction of animal products',
                    'Official disposal of carcasses, by-products and waste',
                    'Process to inactivate the pathogenic agent in products or by-products',
                    'Stamping out',
                    'Selective killing and disposal',
                    'Control of wildlife reservoirs',
                    'Zoning',
                    'Disinfection',
                    'Disinfestation',
                    'Control of vectors',
                    'Vector surveillance',
                    'Ante and post-mortem inspections',
                    'Vaccination permitted (if a vaccine exists)',
                    'Vaccination prohibited',
                    'No treatment of affected animals',
                    'Treatment of affected animals',
                    'Slaughter',
                    'affected_population',
                    'Causal agent',
                    'report_type',
                    'report_ID']



    # 컬럼명 한글로 재설정
    header_kr = ['링크 번호', '질병', '국가', '혈청형', '보고일', '건수', '발생일',
                 '발생 지역', '구분', '축종', '사육', '감염', '폐사', '살처분', '도축',
                 '백신접종', '국내이동제한', '발생대응 예방접종',
                 '봉쇄지역 및/또는 보호지역 외 예찰', '봉쇄지역 및/또는 보호지역 내 예찰',
                 '스크리닝', '이력 추적', '격리', '동물성 생산물 공식처리', '사체·부산물·폐기물 공식처리',
                 '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분', '야생보균원 관리',
                 '방역대 설정', '소독', '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사',
                 '백신접종 허용(백신이 있는 경우)', '백신접종 금지', '감염동물 미치료', '감염동물 치료', '도축*', '세부내역', '원인체', '리포트 번호', '보고서 ID']

    kr_reports.columns = header_kr


    '''혈청형 한글화'''
    
    def serotype_convert(serotype):
        
        serotype_kr = serotype
        
        if pd.notna(serotype):
            
            if serotype == 'Not typed' or serotype == 'Pending':
                serotype_kr = '미정'
                
        return serotype_kr
    
    kr_reports['혈청형'] = kr_reports['혈청형'].map(serotype_convert)

    
    '''숫자 문자열 int화'''

    int_columns = ['링크 번호', '건수', '사육', '감염', '폐사', '살처분', '도축']
    
    kr_reports[int_columns] = kr_reports[int_columns].apply(pd.to_numeric, errors='coerce')  
    # coerce: 숫자로 변환할 수 없는 문자열 같은 경우 강제로 nan 반환
    

    '''
    날짜 문자열을 날짜 객체로 변환 
        - 'dd/mm/yy'을 'yy-mm-dd'로 변환
    '''

    def date_convert(date_str, shape):

        date_kr = date_str

        if pd.notna(date_str):
            # 날짜 문자열의 형식(shape)을 파악한 후 날짜 객체로 변환
            date_kr = datetime.datetime.strptime(date_str, shape).date()

        return date_kr

    kr_reports['보고일'] = kr_reports['보고일'].apply(date_convert, args=('%Y-%m-%d',))
    kr_reports['발생일'] = kr_reports['발생일'].apply(date_convert, args=('%Y-%m-%d',))
    # args=('%d/%m/%Y',): date_convert 함수의 매개변수 shape에 들어갈 인자. apply 함수의 인자(args)는 항상 튜플 형식으로 들어감


    '''국가/대륙 한글화 - country_continent_sort.py에서 country_match와 continent_match 함수 불러옴'''
    kr_reports['국가'] = kr_reports['국가'].map(country_match)
    kr_reports['지역'] = kr_reports['국가'].map(continent_match)


    '''
    질병/축종 한글화
        - 값을 소문자로 변환
        - disease_sort.py에서 disease_match 함수 불러옴
        - species_sort.py에서 species_match 함수 불러옴
    '''
    kr_reports['질병'] = kr_reports['질병'].map(disease_match)
    kr_reports['축종'] = kr_reports['축종'].map(species_match)


    '''
    사육/야생 구분 한글화
    1. 장소로 구분
    2. 동물로 구분
    3. 세부 축종 내용으로 구분
    4. 사육 두수로 구분
        - species_sort.py에서 place_sort와 place_species_sort, place_species_detail_sort, place_susceptible_sort 함수를 불러옴
    '''


    # 장소로 구분

    kr_reports['구분'] = kr_reports.apply(
        lambda x: place_sort(x['구분'], x['축종'], x['사육']), axis=1)


    # 질병명으로 구분
    def Disease_seperate(x):
        diz = re.compile('non-poultry including wild birds')
        if diz.search(x):
            x = '야생'
        else: pass
        return x


    kr_reports['질병확인용'] = oie_reports['Disease']

    kr_reports['구분'] = kr_reports['질병확인용'].apply(lambda x:Disease_seperate(x))


    # 동물로 구분
    kr_reports['구분'] = kr_reports.apply(
        lambda x: place_species_sort(x['구분'], x['축종']), axis=1)

    # 세부 축종으로 구분
    # kr_reports['구분'] = kr_reports.apply(
    #     lambda x: place_species_detail_sort(x['구분'], x['세부 축종']), axis=1)

    # 사육 두수로 구분
    kr_reports['구분'] = kr_reports.apply(
        lambda x: place_susceptible_sort(x['구분'], x['사육']), axis=1)

    # '구분' 열에서 '사육' 값인 행의 '축종' 열 값이 '조류'이면 '가금'으로 변환
    kr_reports.loc[(kr_reports['구분'] == '사육') & (kr_reports['축종'] == '조류'), '축종'] = '가금'


    '''
    리포트 번호 추출
        - 'Immediate'이면 '긴급', 'Follow-up'이면 숫자 추출 후 반환
    '''

    def report_type_kr(x):

        report_type = x

        if pd.notna(x):
            '''I로 시작하면 긴급, F로 시작하면 숫자 추출'''
            if re.match('^[I]', x):
                report_type = '긴급'

            elif re.match('^[F]', x):
                followup_number = re.search('[0-9]+', x).group()
                report_type = followup_number

        return report_type

    kr_reports['리포트 번호'] = kr_reports['리포트 번호'].map(report_type_kr)


    '''요청에 맞게 열 위치 수정'''

    header_kr_modi = header_kr[:2] + ['지역'] + header_kr[2:]
    kr_reports = kr_reports[header_kr_modi]

    return oie_reports, kr_reports


if __name__ == '__main__':

    # db에서 원하는 부분 가져오기 - 원하는 데이터만 가져와 한글화가 필요할 때
    import os

    '''
    'oiescraper' 폴더에 db파일이 있음
    현재 경로에 db파일이 있으면(현재 경로가 'oiescraper' 폴더라면) 그대로, 없으면 'oiescraper' 폴더로 경로 설정
    '''
    
    if 'oie_reports.db' in os.listdir():  # os.listdir(path): path의 하위 폴더 및 파일 리스트. path 넣지 않으면 현재 경로로 설정
        con = sqlite3.connect('oie_reports.db')
    else:
        con = sqlite3.connect('./oiescraper/oie_reports.db')  # doc(.): 현재 경로

    # # 전체 db
    oie_reports = pd.read_sql("SELECT * FROM oie_reports", con)  # FROM: 해당 테이블, SELECT: 데이터 가져오기
    kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr", con)  # FROM: 해당 테이블, SELECT: 데이터 가져오기

    # # 특정 행
    # oie_reports = pd.read_sql("SELECT * FROM oie_reports WHERE rowid BETWEEN 12648 AND 13764", con)  # rowid: 행
    # kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr WHERE rowid BETWEEN 12648 AND 13764", con)  # rowid: 행

    # 특정 날짜 - WHERE: 조건, ORDER BY: 정렬(ASC: 오름차순, DESC: 내림차순)
    # kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr WHERE 보고일 BETWEEN '2020-08-15' and '2020-10-08' ORDER BY 보고일 ASC", con)
    # kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr WHERE 보고일 BETWEEN '2020-08-15' and '2020-10-08'", con)
    # kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr WHERE 보고일 >= '2017-01-01'", con)

    # # 국가가 한국인 것 - LIKE: 특정 글자 포함
    # # oie_reports = pd.read_sql("SELECT * FROM oie_reports WHERE Country LIKE '%korea (rep. of)'", con)  # 대, 소문자 상관없음,
    # kr_reports = pd.read_sql('''
    #                           SELECT * FROM oie_reports_kr WHERE 
    #                           국가 IN ('벨기에', '폴란드', '헝가리') AND 
    #                           질병 = '아프리카돼지열병' AND 
    #                           보고일 BETWEEN '2014-01-01' AND 
    #                           '2018-12-31' ORDER BY 보고일 ASC
    #                           ''', con)

    # 국가가 헝가리나 폴란드이면서 질병이 hpai인 것
    # oie_reports = pd.read_sql(
    #     "SELECT * FROM oie_reports WHERE Country IN ('Hungary', 'Poland') AND Disease LIKE 'Highly pathogenic%'", con)
    # kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr WHERE 국가 IN ('헝가리', '폴란드') AND 질병 LIKE '고병원성%'", con)

    # # 조치사항 중 감염동물치료 및 미치료는 둘 중 하나는 값이 있을테니
    # measure_deburg = pd.read_sql('SELECT [No treatment of affected animals], [Treatment of affected animals] FROM oie_reports', con)

    # # 특정 행 이후
    # oie_reports = pd.read_sql("SELECT * FROM oie_reports WHERE rowid >= 82504", con)  # rowid: 행
    # # kr_reports = pd.read_sql("SELECT * FROM oie_reports_kr WHERE rowid > 80846", con)  # rowid: 행

    # # 럼피스킨이면서 긴급인 것
    # oie_reports = pd.read_sql(
    #     '''
    #     SELECT * FROM oie_reports WHERE Disease GLOB 'Lumpy*' AND [Report type] GLOB 'I*'
    #     ''', con)  # GLOB: 패턴 검색. *: 0개 이상. 'Lumpy*': Lumpy 뒤에 임의의 문자가 0개 이상인 것
    # kr_reports = pd.read_sql(
    #     "SELECT * FROM oie_reports_kr WHERE 질병 GLOB '럼피스킨*' AND [리포트 번호] == '긴급'", con)


    # # 한글화
    trans_dfs = translate_oie_reports(oie_reports)
    kr_reports = trans_dfs[1]

    # # db 저장
    # import warnings
    
    # warnings.filterwarnings(action='ignore')  # 경고 메시지 안 띄우게 함. action='ignore': 무시 'default': 경고 발생 위치에 출력

    # trans_dfs[0].to_sql('oie_reports', con, if_exists='replace', index=False)
    # trans_dfs[1].to_sql('oie_reports_kr', con, if_exists='replace', index=False)    

    con.close()

    with pd.ExcelWriter('oie_reports_test.xlsx') as writer:
        oie_reports.to_excel(writer, '원본', index=False)
        kr_reports.to_excel(writer, '번역본', index=False)