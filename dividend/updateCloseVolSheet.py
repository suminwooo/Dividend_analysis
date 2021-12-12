import pandas as pd
import FinanceDataReader as fdr
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dividend.config import doc


def _find_date():
    """
    시트에 입력할 날짜 데이터 가져오기
    """
    # 검색 날짜 선언
    today = datetime.now()
    today_date = today.strftime("%Y-%m-%d")
    before_one_month_date = (today + relativedelta(months=-1)).strftime("%Y-%m-%d")
    before_three_month_date = (today + relativedelta(months=-3)).strftime("%Y-%m-%d")
    before_six_month_date = (today + relativedelta(months=-6)).strftime("%Y-%m-%d")
    before_one_year_date = (today + relativedelta(months=-12)).strftime("%Y-%m-%d")
    before_three_year_date = (today + relativedelta(months=-36)).strftime("%Y-%m-%d")
    before_five_year_date = (today + relativedelta(months=-60)).strftime("%Y-%m-%d")
    before_ten_year_date = (today + relativedelta(months=-120)).strftime("%Y-%m-%d")

    check_date = [
        today_date,
        before_one_month_date,
        before_three_month_date,
        before_six_month_date,
        before_one_year_date,
        before_three_year_date,
        before_five_year_date,
        before_ten_year_date,
    ]

    return check_date


def _find_close_vol_data(tmp_stock, result):

    # 필요한 날짜 출력
    check_date = _find_date()

    # 종가, 거래량 관련 전체 데이터 출력(FinanceDataReader 활용)
    data_date_idx = (datetime.now() + relativedelta(months=-132)).strftime("%Y-%m-%d")  # 넉넉하게 11년전부터 데이터 출력
    data = fdr.DataReader(symbol=tmp_stock, start=data_date_idx)

    # 휴일에는 데이터 정보X -> 가까운 날짜 찾기
    data_date_int_lst = sorted([int(i.strftime("%Y%m%d")) for i in list(data.index)])
    check_date_int_lst = [int(i.replace("-", "")) for i in check_date]

    new_check_date = []
    for each_date in check_date_int_lst:
        tmp_dic = {}
        for each_idx_date in data_date_int_lst:
            tmp_dic[each_idx_date] = abs(each_idx_date - each_date)
        tmp_nearest_date = str(sorted(tmp_dic.items(), key=lambda item: item[1])[0][0])
        new_check_date.append(tmp_nearest_date[:4] + "-" + tmp_nearest_date[4:6] + "-" + tmp_nearest_date[6:])

    # 데이터 재정의(필요한 날짜의 종가와 거래량만 출력)
    volume_data = data["Volume"].loc[new_check_date].fillna(-1)  # 거래량 데이터
    close_date = data["Close"].loc[new_check_date].fillna(-1)  # 종가 데이터
    new_data = pd.merge(volume_data.reset_index(), close_date.reset_index())

    # 종가 거래량 계산
    tmp_close_ratio_lst = []
    for idx, i in enumerate(new_data["Close"]):
        if idx == 0:  # 현재 증가율 의미 X
            continue
        if (i == -1) | (i == 0):  # -1이라면 None 값이므로 계산 X
            tmp_close_ratio_lst.append("X")
        else:
            tmp_close_ratio_lst.append(round(((new_data["Close"][0] - i) / i) * 100, 1))

    # 거래량 비율 계산
    tmp_volume_ratio_lst = []
    for idx, i in enumerate(new_data["Volume"]):
        if idx == 0:  # 현재 증가율 의미 X
            continue
        if (i == -1) | (i == 0):  # -1이라면 None 값이므로 계산 X
            tmp_volume_ratio_lst.append("X")
        else:
            tmp_volume_ratio_lst.append(round(((new_data["Volume"][0] - i) / i) * 100, 1))

    # 데이터 입력
    new_data["close_ratio"] = [None] + tmp_close_ratio_lst
    new_data["vol_ratio"] = [None] + tmp_volume_ratio_lst
    new_data["Close"] = [round(i, 2) for i in new_data["Close"]]
    new_data["Volume"] = [round(i, 2) for i in new_data["Volume"]]
    new_data = new_data[["Close", "Volume", "close_ratio", "vol_ratio", "Date"]]

    tmp_value = [
        new_data.iloc[0, 0],  # 기준일 종가
        new_data.iloc[0, 1],  # 기준일 거래량
        # 종가 증가율
        new_data.iloc[1, 2],  # 한달전 대비 종가 증가율
        new_data.iloc[2, 2],  # 3달전 대비 종가 증가율
        new_data.iloc[3, 2],  # 6달전 대비 종가 증가율
        new_data.iloc[4, 2],  # 1년전 대비 종가 증가율
        new_data.iloc[5, 2],  # 3년전 대비 종가 증가율
        new_data.iloc[6, 2],  # 5년전 대비 종가 증가율
        new_data.iloc[7, 2],  # 10년전 대비 종가 증가율
        # 거래량 증가율
        new_data.iloc[1, 3],  # 한달전 대비 거래량 증가율
        new_data.iloc[2, 3],  # 3달전 대비 거래량 증가율
        new_data.iloc[3, 3],  # 6달전 대비 거래량 증가율
        new_data.iloc[4, 3],  # 1년전 대비 거래량 증가율
        new_data.iloc[5, 3],  # 3년전 대비 거래량 증가율
        new_data.iloc[6, 3],  # 5년전 대비 거래량 증가율
        new_data.iloc[7, 3],  # 10년전 대비 거래량 증가율
        # 종가 정리
        new_data.iloc[1, 0],  # 한달전 종가
        new_data.iloc[2, 0],  # 3달전 종가
        new_data.iloc[3, 0],  # 6달전 종가
        new_data.iloc[4, 0],  # 1년전 종가
        new_data.iloc[5, 0],  # 3년전 종가
        new_data.iloc[6, 0],  # 5년전 종가
        new_data.iloc[7, 0],  # 10년전 종가
        # 거래량 정리
        new_data.iloc[1, 1],  # 한달전 거래량
        new_data.iloc[2, 1],  # 3달전 거래량
        new_data.iloc[3, 1],  # 6달전 거래량
        new_data.iloc[4, 1],  # 1년전 거래량
        new_data.iloc[5, 1],  # 3년전 거래량
        new_data.iloc[6, 1],  # 5년전 거래량
        new_data.iloc[7, 1],  # 10년전 거래량
    ]

    result = [
        tmp_stock,
        result[0][tmp_stock]["sector_dic"]["name"],
        result[0][tmp_stock]["sector_dic"]["sector"],
        result[0][tmp_stock]["sector_dic"]["industry"],
    ] + tmp_value
    return result


def _find_all_stock_data(result):
    stock_lst = list(result[0].keys())
    total_lst = []
    for tmp_stock in stock_lst:
        each_result = _find_close_vol_data(tmp_stock, result)
        total_lst.append(each_result)
    return total_lst


def update_close_vol_sheet(div_split_statement_dic, IsUpdate):

    # 0. 필요한 시트 import
    close_vol_sheet = doc.worksheet("종가, 거래량 정보(결과)")
    close_vol_sheet_data = get_as_dataframe(close_vol_sheet)
    # # 1. 데이터 만들기
    data = _find_all_stock_data(div_split_statement_dic)
    # 2. 시트 초기화후 업데이트
    if IsUpdate is False:
        # 행 초기화
        set_with_dataframe(
            close_vol_sheet,
            pd.DataFrame([[None] * 34] * 200),
            row=4,
            include_index=False,
            include_column_header=False,
        )

    # 종가, 거래량 정보(결과) 업데이트
    set_with_dataframe(
        close_vol_sheet,
        pd.DataFrame(data),
        row=4 + len(close_vol_sheet_data["Symbol"].dropna()),
        include_index=False,
        include_column_header=False,
    )
