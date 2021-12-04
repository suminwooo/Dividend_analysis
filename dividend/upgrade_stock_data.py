import pandas as pd
import FinanceDataReader as fdr
from gspread_dataframe import get_as_dataframe, set_with_dataframe

from dividend.config import doc
from dividend.util import add_except_stock


def _import_stock_info() -> None:
    """
    미국 종목 출력 코드
    """

    # 종목 출력(나스닥, S&P500, NYSE, AMEX)
    df_NASDAQ = fdr.StockListing("NASDAQ")[["Symbol", "Name", "Industry"]]  # 나스닥 전체 출력
    df_SP500 = fdr.StockListing("S&P500")[["Symbol", "Name", "Industry"]]  # S&P 전체 출력
    df_NYSE = fdr.StockListing("NYSE")[["Symbol", "Name", "Industry"]]  # NYSE 전체 출력
    df_AMEX = fdr.StockListing("AMEX")[["Symbol", "Name", "Industry"]]  # AMEX 전체 출력

    # 데이터 합치기
    data = pd.concat([df_NASDAQ, df_SP500, df_NYSE, df_AMEX], axis=0).drop_duplicates(subset=["Symbol"])
    return data


def upgrade_data():
    """
    분석에 사용할 데이터 출력
    """

    # 구글 스프레드 시트 ---------------------------------------------------------------
    # 추가할 종목
    worksheet_raw_dividend_stock_sheet = doc.worksheet("추가할 종목 시트(입력)")
    add_stock_lst = worksheet_raw_dividend_stock_sheet.col_values(2)[1:]

    # 제외할 목록
    worksheet_raw_remove_stock_sheet = doc.worksheet("제외할 종목 시트(입력)")
    remove_stock_lst = worksheet_raw_remove_stock_sheet.col_values(2)[1:]
    add_except_stock(remove_stock_lst, "제외할 리스트에 추가되어 있음", type_check=True)  # 제외 종목 추가

    # 기존 분석 목록
    analysis_stock_sheet = doc.worksheet("분석 종목 시트(과정)")
    existing_stock_data = get_as_dataframe(analysis_stock_sheet)
    existing_stock_data = existing_stock_data.loc[
        existing_stock_data["Symbol"].dropna().index
    ]  # 종목명으로 dropna() 실행, 다른값은 데이터가 존재하지 않을 가능성 존재
    existing_stock_lst = existing_stock_data["Symbol"].tolist()

    # -------------------------------------------------------------------------------

    # 기존 분석 목록에서 제외할 목록에 추가되었다면 제거
    delete_from_existring_stock_lst = list(set(remove_stock_lst) & set(existing_stock_lst))

    if len(delete_from_existring_stock_lst) != 0:
        using_idx = list(
            set(existing_stock_data.index)
            - set(
                existing_stock_data[
                    existing_stock_data["Symbol"].isin(delete_from_existring_stock_lst)
                ].index.tolist()
            )
        )

        new_existing_stock_data = existing_stock_data.loc[using_idx].reset_index(drop=True)
        analysis_stock_sheet.clear()
        set_with_dataframe(analysis_stock_sheet, new_existing_stock_data)

    # 주식 정보 데이터
    data = _import_stock_info()

    # 포함되지 않은 주식 리스트
    not_include_stock_lst = list(set(add_stock_lst) - set(data["Symbol"]))
    add_except_stock(not_include_stock_lst, "나스닥, S&P500, NYSE, AMEX에 정보가 존재하지 않음")  # 제외 종목 추가

    # 추가할 목록
    add_stock_lst = list(set(add_stock_lst) - set(remove_stock_lst))

    if len(add_stock_lst) != 0:
        # 새로 추가된 데이터 입력 및 시트 초기화
        new_stock_data = data[data["Symbol"].isin(add_stock_lst)]

        if len(set(add_stock_lst) - set(existing_stock_lst)) != 0:
            for i in [list(i) for i in new_stock_data.values]:
                analysis_stock_sheet.append_row(i)
            worksheet_raw_dividend_stock_sheet.clear()
            worksheet_raw_dividend_stock_sheet.append_row(["종목명", "종목 코드", "영문명"])
            worksheet_raw_dividend_stock_sheet.update_acell("D2", "종목 코드 필수")
            worksheet_raw_dividend_stock_sheet.update_acell("D3", "종목명, 영문명 선택")
