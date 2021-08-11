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


trans_dfs = translate_oie_reports(oie_reports)
kr_reports = trans_dfs[1]


con.close()

with pd.ExcelWriter('oie_reports_test.xlsx') as writer:
    oie_reports.to_excel(writer, '원본', index=False)
    kr_reports.to_excel(writer, '번역본', index=False)