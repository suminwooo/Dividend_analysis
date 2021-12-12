from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
from datetime import datetime
from dividend.config import doc


def reset_stock_list():
    # 시트 및 데이터 가져오기
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")

    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)

    update_month = datetime.now().month  # 업데이트 월

    # 업데이트 된 데이터 가져오기
    new_existing_stocks_lst = []
    for i in range(4):
        each_final_stock_lst = list(existing_stocks_list_data.iloc[1:, i].dropna())
        new_existing_stocks_lst.extend(each_final_stock_lst)

    # 50개씩 쪼개기
    new_existing_stocks_50_lst = [
        new_existing_stocks_lst[i : i + 50] for i in range(0, len(new_existing_stocks_lst), 50)
    ]

    # 빈 데이터 프레임 설정
    empty_df = pd.DataFrame([[None] * 4] * 51)

    # 기존 종목 시트
    set_with_dataframe(
        existing_stocks_list_sheet,
        empty_df,
        row=2,
        include_index=False,
        include_column_header=False,
    )

    # 종목 데이터 입력
    for idx, i in enumerate(new_existing_stocks_50_lst):
        empty_df.iloc[: len(i) + 1, idx] = [update_month] + i

    # 기존 종목 리스트 업데이트
    set_with_dataframe(
        existing_stocks_list_sheet,
        empty_df,
        row=2,
        include_index=False,
        include_column_header=False,
    )
