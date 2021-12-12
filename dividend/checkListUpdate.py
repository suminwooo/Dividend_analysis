from gspread_dataframe import get_as_dataframe
from datetime import datetime
from dividend.config import doc


def check_update():
    # 시트 및 데이터 가져오기
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")
    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)

    update_month = datetime.now().month  # 업데이트 월

    # 업데이트 유무 확인
    for i in list(
        existing_stocks_list_data.iloc[
            0,
        ]
    ):
        if i != update_month:
            return "NotUpdate"
    return "update"
