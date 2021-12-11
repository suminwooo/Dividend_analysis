from gspread_dataframe import get_as_dataframe
from datetime import datetime
from new_file.config import doc


def find_stock_list():
    """
    종목 출력 함수 만들기
    """
    # 0. 필요한 시트 import
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")

    # 각 시트 데이터
    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)

    # 필요 데이터 출력
    update_month = datetime.now().month  # 업데이트 월

    # 1. 데이터 출력할 종목 리스트 출력
    # 몇 번째 열을 업데이트 할지 확인
    for i in range(4):
        each_group_update_month = existing_stocks_list_data.iloc[0, i]
        if each_group_update_month != update_month:
            check_col = i
            check_stock_lst = list(existing_stocks_list_data.iloc[:, check_col][1:].dropna())
            break

    return check_stock_lst
