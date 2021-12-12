from gspread_dataframe import set_with_dataframe, get_as_dataframe
import pandas as pd
from dividend.config import doc


def _fill_div_statement_data(result, IsUpdate):

    # 0. 필요한 시트 import
    split_statemene_sheet = doc.worksheet("액면분할, 재무제표 정보(결과)")
    split_statemene_sheet_data = get_as_dataframe(split_statemene_sheet)

    # 데이터 만들기
    final_data = []
    for stock_name in result[0].keys():
        try:
            tmp_stock_data = [
                stock_name,
                result[0][stock_name]["sector_dic"]["name"],
                result[0][stock_name]["sector_dic"]["sector"],
                result[0][stock_name]["sector_dic"]["industry"],
                result[0][stock_name]["split_dic"]["last_split_date"],
                result[0][stock_name]["split_dic"]["last_split_ratio"],
                result[0][stock_name]["split_dic"]["last_price_ratio"],
                result[0][stock_name]["split_dic"]["total_split_cnt"],
                result[0][stock_name]["split_dic"]["split_cnt_within_5yr"],
                result[0][stock_name]["statement_dic"]["forwardEps"],
                result[0][stock_name]["statement_dic"]["trailingEps"],
                result[0][stock_name]["statement_dic"]["trailingPE"],
                result[0][stock_name]["statement_dic"]["forwardPE"],
                result[0][stock_name]["statement_dic"]["returnOnEquity"],
                result[0][stock_name]["statement_dic"]["revenue_ratio_lst"],
                result[0][stock_name]["statement_dic"]["earning_ratio_lst"],
                result[0][stock_name]["statement_dic"]["cash_ratio_lst"],
                result[0][stock_name]["statement_dic"]["revenue_4yr_lst"],
                result[0][stock_name]["statement_dic"]["earning_4yr_lst"],
                result[0][stock_name]["statement_dic"]["cash_flow_4yr_lst"],
            ]
        except:
            tmp_stock_data = [
                stock_name,
                result[0][stock_name]["sector_dic"]["name"],
                result[0][stock_name]["sector_dic"]["sector"],
                result[0][stock_name]["sector_dic"]["industry"],
                "액면 분할 하지 않음",
                "-",
                "-",
                "-",
                "-",
                result[0][stock_name]["statement_dic"]["forwardEps"],
                result[0][stock_name]["statement_dic"]["trailingEps"],
                result[0][stock_name]["statement_dic"]["trailingPE"],
                result[0][stock_name]["statement_dic"]["forwardPE"],
                result[0][stock_name]["statement_dic"]["returnOnEquity"],
                result[0][stock_name]["statement_dic"]["revenue_ratio_lst"],
                result[0][stock_name]["statement_dic"]["earning_ratio_lst"],
                result[0][stock_name]["statement_dic"]["cash_ratio_lst"],
                result[0][stock_name]["statement_dic"]["revenue_4yr_lst"],
                result[0][stock_name]["statement_dic"]["earning_4yr_lst"],
                result[0][stock_name]["statement_dic"]["cash_flow_4yr_lst"],
            ]

        final_data.append(tmp_stock_data)

    # 데이터 시트 입력
    if IsUpdate is False:
        # 초기화
        set_with_dataframe(
            split_statemene_sheet,
            pd.DataFrame([[None] * 20] * 200),
            row=4,
            include_index=False,
            include_column_header=False,
        )

    # 입력
    set_with_dataframe(
        split_statemene_sheet,
        pd.DataFrame(final_data),
        row=4 + len(split_statemene_sheet_data.iloc[2:]["Symbol"].dropna()),
        include_index=False,
        include_column_header=False,
    )


def _fill_dividend_page(result, IsUpdate):
    # 0. 필요한 시트 import
    dividend_sheet = doc.worksheet("배당 관련 정보(결과)")
    dividend_sheet_data = get_as_dataframe(dividend_sheet)

    # 데이터 생성
    final_data = []
    for stock_name in result[0].keys():
        tmp_stock_data = [
            stock_name,
            result[0][stock_name]["sector_dic"]["name"],
            result[0][stock_name]["sector_dic"]["sector"],
            result[0][stock_name]["sector_dic"]["industry"],
            result[0][stock_name]["devidend_dic"]["lastDividendValue"],
            result[0][stock_name]["devidend_dic"]["lastDividendDate"],
            result[0][stock_name]["devidend_dic"]["dividendRate"],
            result[0][stock_name]["devidend_dic"]["dividendYield"],
            result[0][stock_name]["devidend_dic"]["marketDividendRate"],
            result[0][stock_name]["devidend_dic"]["payoutRatio"],
            result[0][stock_name]["devidend_dic"]["trailingAnnualDividendYield"],
            result[0][stock_name]["devidend_dic"]["trailingAnnualDividendRate"],
            result[0][stock_name]["devidend_dic"]["fiveYearAvgDividendYield"],
            result[0][stock_name]["devidend_dic"]["dividendCycle"],
            result[0][stock_name]["devidend_dic"]["dividendMonth"],
            result[0][stock_name]["devidend_dic"]["forwardNextDividendDate"],
            result[0][stock_name]["devidend_dic"]["dividendStart"],
            result[0][stock_name]["devidend_dic"]["increasedDate"],
            result[0][stock_name]["devidend_dic"]["increasedCount"],
            result[0][stock_name]["devidend_dic"]["typePayout"],
            result[0][stock_name]["devidend_dic"]["isDividendCompare2008"],
            result[0][stock_name]["devidend_dic"]["isDividendCompare2020"],
            result[0][stock_name]["devidend_dic"]["isDividendCompare2008Ratio"],
            result[0][stock_name]["devidend_dic"]["isDividendCompare2020Ratio"],
        ]
        final_data.append(tmp_stock_data)

    if IsUpdate is False:
        # 초기화
        set_with_dataframe(
            dividend_sheet,
            pd.DataFrame([[None] * 24] * 200),
            row=4,
            include_index=False,
            include_column_header=False,
        )
    print(pd.DataFrame(final_data))
    # 입력
    set_with_dataframe(
        dividend_sheet,
        pd.DataFrame(final_data),
        row=4 + len(dividend_sheet_data.iloc[2:]["Symbol"].dropna()),
        include_index=False,
        include_column_header=False,
    )


def update_div_split_statement_sheet(result, IsUpdate):
    _fill_div_statement_data(result, IsUpdate)
    _fill_dividend_page(result, IsUpdate)
