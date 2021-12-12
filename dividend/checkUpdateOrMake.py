from gspread_dataframe import get_as_dataframe
from datetime import datetime
from dividend.config import doc


def check_update_or_make():
    # 시트 및 데이터 가져오기
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")
    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)

    update_month = datetime.now().month  # 업데이트 월

    type_check = None

    put_data_size = len(list(existing_stocks_list_data.iloc[0].dropna()))

    for i in range(put_data_size):
        if update_month != existing_stocks_list_data.iloc[0, i]:
            if i == 0:
                type_check = "make new data"
            else:
                type_check = "update data"

    if type_check == None:
        type_check = "all update"
    return type_check
