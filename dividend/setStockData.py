from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import datetime
import pandas as pd
from dividend.config import doc


def set_stock_data():
    """
    추가할 종목 및 기존 종목 수정
    """
    # 0. 필요한 시트 import
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")
    add_stock_sheet = doc.worksheet("추가할 종목 시트(입력)")
    remove_stock_sheet = doc.worksheet("제외할 종목 시트(입력)")

    # 각 시트 데이터
    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)
    add_stock_data = get_as_dataframe(add_stock_sheet)
    remove_stock_data = get_as_dataframe(remove_stock_sheet)

    # 필요 데이터 출력
    update_month = datetime.now().month  # 업데이트 월
    add_stock_lst = list(add_stock_data["종목 코드"].dropna())  # 추가할 종목 리스트

    # 추가할 종목 리스트에서 제외할 종목 리스트빼기
    add_stock_lst = list(set(add_stock_lst) - set(list(remove_stock_data.iloc[:, 1].dropna())))

    # 1. 업데이트 되지 않은 셀 확인 -> 기존 종목 리스트에서 2행이 업데이트 월과 다를 경우 추가
    not_update_col = []
    for i in range(4):
        each_group_update_month = existing_stocks_list_data.iloc[0, i]
        if update_month != each_group_update_month:
            not_update_col.append(i)

    # 2. 추가할 종목 리스트 셋팅
    stock_list = []
    for i in not_update_col:
        stock_list.extend(list(existing_stocks_list_data.iloc[1:, i].dropna()))

    new_existing_stocks_lst = stock_list + add_stock_lst  # 전체 리스트와 추가된 리스트 합치기
    new_existing_stocks_50_lst = [
        new_existing_stocks_lst[i : i + 50] for i in range(0, len(new_existing_stocks_lst), 50)
    ]  # 50개씩 쪼개기

    # 3. 새로운 데이터 생성
    empty_df = pd.DataFrame([[None] * len(not_update_col)] * 50)

    for col, each_lst in enumerate(new_existing_stocks_50_lst):
        each_lst = list(set(each_lst))
        for row, each_stock in enumerate(each_lst):
            empty_df.iloc[row, col] = each_stock

    # 4. 데이터 입력 : 기존 종목 리스트 재생성
    set_with_dataframe(
        existing_stocks_list_sheet,
        empty_df,
        row=3,
        col=5 - len(empty_df.columns),
        include_index=False,
        include_column_header=False,
    )

    # 5. 값이 존재 하지 않을 경우 2행값 제거(마지막 업데이트 월)
    update_existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)
    for empty_cell in range(len(update_existing_stocks_list_data.columns)):
        if len(update_existing_stocks_list_data.iloc[:, empty_cell].dropna()) < 2:
            break

    empty_check_df = pd.DataFrame([None] * (4 - empty_cell)).T

    set_with_dataframe(
        existing_stocks_list_sheet,
        empty_check_df,
        row=2,
        col=1 + empty_cell,
        include_index=False,
        include_column_header=False,
    )
    # 업데이트 행이 존재하면 그부분은 무시하고 초기화 설정 필요
    # 6. 추가할 종목 초기화
    set_with_dataframe(
        add_stock_sheet,
        pd.DataFrame([[None, None, None]] * 30),
        row=2,
        include_index=False,
        include_column_header=False,
    )
    # 리스트 뽑을 칼럼 리턴
    start_col = not_update_col[0]
    if start_col >= 5:
        return "업데이트X"
    else:
        return start_col
