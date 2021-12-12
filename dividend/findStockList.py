from gspread_dataframe import get_as_dataframe
from dividend.config import doc


def find_stock_list(start_col):
    """
    종목 출력 함수 만들기
    """
    print("start_col : ", start_col)
    # 0. 필요한 시트 import
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")

    # 각 시트 데이터
    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)

    # 필요 데이터 출력
    check_stock_lst = list(existing_stocks_list_data.iloc[1:, start_col].dropna())

    return check_stock_lst
