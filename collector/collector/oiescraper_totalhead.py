import pandas as pd, os, numpy as np


def totalhead(table) -> object:

    def first_groupby():
        total_first_list = []
        for x in first_list:
            total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].first()
            if total.name == '발생일':
                total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].unique()
                total.name = '시작일'
            else:
                pass
            total_first_list.append(total)
        return total_first_list

    def last_groupby():
        total_last_list = []
        for x in last_list:
            total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].last()
            if total.name == '발생일':
                total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].unique()
                total.name = '종료일'
            else:
                pass
            total_last_list.append(total)
        return total_last_list

    def sum_groupby():
        total_sum_list = []
        for x in sum_list:
            if x == '구분':
                total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].apply(lambda x: "%s" % ','.join(x))
            elif x == '링크 번호':
                # total[x] = total[x].astype(str)
                total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].unique()
            else:
                total = table_modify.groupby(['질병', '국가', '리포트 번호', '혈청형', '축종'])[x].sum()
            total_sum_list.append(total)
        return total_sum_list

    def immediate_followup(x):
        if x == "긴급":
            return "긴급"
        else:
            return "추가"

    def wild_livestock(x):
        if type(x) == float:
            pass
        elif '사육' in x and '야생' in x:
            return "사육,야생"
        elif '사육' in x and '야생' not in x:
            return "사육"
        else:
            return "야생"

    def link_number_arrange(x):
        link_number = []
        if x not in link_number:
            link_number.append(x)
        else:
            pass
        return link_number

    table_modify = table.copy()
    table_modify['혈청형'] = table_modify['혈청형'].apply(lambda x: "-" if pd.isnull(x) else x)
    table_modify['리포트 번호'] = table_modify['리포트 번호'].apply(immediate_followup)

    first_list = ['리포트 번호', '원인체', '발생일', '발생 지역', '국내이동제한', '발생대응 예방접종', '봉쇄지역 및/또는 보호지역 외 예찰',
                  '봉쇄지역 및/또는 보호지역 내 예찰', '스크리닝', '이력 추적', '격리', '동물성 생산물 공식처리', '사체·부산물·폐기물 공식처리',
                  '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분', '야생보균원 관리', '방역대 설정', '소독',
                  '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사', '백신접종 허용(백신이 있는 경우)', '백신접종 금지',
                  '감염동물 미치료', '감염동물 치료', '도축*']

    last_list = ['보고일', '발생일']
    sum_list = ['구분', '건수', '사육', '감염', '폐사', '살처분', '도축', '링크 번호']

    total_list = first_groupby() + last_groupby() + sum_groupby()
    total_df = pd.concat([i for i in total_list], axis=1)
    total_data = total_df.copy()
    total_data['발생기간'] = ""
    # total_data['시작일']=total_data['시작일'].apply(lambda x:x.sort())
    total_data = total_data[
        ['링크 번호', '원인체', '구분', '발생기간', '보고일', '시작일', '발생 지역', '종료일', '건수', '사육', '감염', '폐사', '살처분', '도축', '국내이동제한',
         '발생대응 예방접종',
         '봉쇄지역 및/또는 보호지역 외 예찰', '봉쇄지역 및/또는 보호지역 내 예찰', '스크리닝', '이력 추적', '격리', '동물성 생산물 공식처리',
         '사체·부산물·폐기물 공식처리', '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분',
         '야생보균원 관리', '방역대 설정', '소독', '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사',
         '백신접종 허용(백신이 있는 경우)', '백신접종 금지', '감염동물 미치료', '감염동물 치료', '도축*']]

    total_data['구분'] = total_data['구분'].apply(wild_livestock)
    # total_data['링크 번호'] = total_data['링크 번호'].apply(link_number_arrange)
    total_data[['시작일','종료일']]=total_data[['시작일','종료일']].applymap(lambda x: list(x)).applymap(lambda x: sorted(x))

    i = 0
    outbreak_period_list = []
    while i < len(total_data['시작일']):
        if total_data['시작일'][i][0] != total_data['종료일'][i][-1]:
            outbreak_period_list.append(str(total_data['시작일'][i][0]) + '~' + str(total_data['종료일'][i][-1]))
        else:
            outbreak_period_list.append(str(total_data['시작일'][i][0]))
        i += 1
    total_data.drop(['시작일', '종료일'], inplace=True, axis=1)
    total_data['발생기간'] = outbreak_period_list


    total_data1 = total_data.swaplevel(0, 1)
    # total_data.reset_index(inplace=True) # 멀티인덱스 삭제하기
    total_data1 = total_data1.sort_index(axis=0, level=0).copy()

    return total_data1


if __name__ == '__main__':


    '''
    SQL 문을 읽어서 
    'oiescraper' 폴더에 db파일이 있음
    현재 경로에 db파일이 있으면(현재 경로가 'oiescraper' 폴더라면) 그대로, 없으면 'oiescraper' 폴더로 경로 설정
    '''

    # db에서 원하는 부분 가져오기 - 원하는 데이터만 가져와 한글화가 필요할 때
    # import os, sqlite3
    #


    #
    # if 'oie_reports.db' in os.listdir():  # os.listdir(path): path의 하위 폴더 및 파일 리스트. path 넣지 않으면 현재 경로로 설정
    #     con = sqlite3.connect('oie_reports.db')
    # else:
    #     con = sqlite3.connect('./oiescraper/oie_reports.db')  # doc(.): 현재 경로
    #
    # # # 특정 행 이후
    # table = pd.read_sql("SELECT * FROM oie_reports_kr WHERE rowid BETWEEN 84999 AND 85130", con)  # rowid: 행
    #
    # con.close()

    '''
    파일을 읽어서 바꾸는 방법 
    '''
    path = input('경로를 입력하세요')

    table = pd.read_excel(path,sheet_name='번역본')
    totalhead_df = totalhead(table)

    with pd.ExcelWriter('totalhead_ex.xlsx') as writer:
        table.to_excel(writer, '번역본', index=False)
        totalhead_df.to_excel(writer, '해동(총 두수)')