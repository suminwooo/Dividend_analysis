import pandas as pd
import yfinance as yf
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import datetime
from dateutil.relativedelta import relativedelta

from dividend.config import doc
from dividend.util import add_except_stock


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


def find_value():
    # data 불러오기
    analysis_stock_sheet = doc.worksheet("분석 종목 시트(과정)")
    stock_data = get_as_dataframe(analysis_stock_sheet)
    stock_data = stock_data.loc[stock_data["Symbol"].dropna().index]
    stock_lst = list(stock_data["Symbol"])

    # 필요한 날짜 출력
    check_date = _find_date()

    # 종가, 거래량 관련 전체 데이터 출력(yahoo 활용)
    data_date_idx = (datetime.now() + relativedelta(months=-132)).strftime("%Y-%m-%d")  # 넉넉하게 11년전부터 데이터 출력
    data = yf.download(stock_lst, start=data_date_idx)

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

    # 인덱스 재정의
    data.index = [str(i)[:10] for i in data.index]

    # 데이터 재정의(null 값 처리)
    volume_data = data["Volume"].loc[new_check_date].fillna(-1)  # 거래량 데이터
    close_date = data["Close"].loc[new_check_date].fillna(-1)  # 종가 데이터
    data = data.reset_index().rename(columns={"index": "Date"})

    # 데이터 정리 및 추가하기
    final_data_lst = []
    for tmp_stock in stock_lst:
        tmp_data = pd.merge(
            volume_data[[tmp_stock]].rename(columns={tmp_stock: "vol"}).reset_index(),
            close_date[[tmp_stock]].rename(columns={tmp_stock: "close"}).reset_index(),
        ).rename(columns={"index": "Date"})

        tmp_close_ratio_lst = []
        for idx, i in enumerate(tmp_data["close"]):
            if idx == 0:  # 현재 증가율 의미 X
                continue
            if (i == -1) | (i == 0):  # -1이라면 None 값이므로 계산 X
                tmp_close_ratio_lst.append("X")
            else:
                tmp_close_ratio_lst.append(round(((tmp_data["close"][0] - i) / i) * 100, 1))

        tmp_volume_ratio_lst = []
        for idx, i in enumerate(tmp_data["vol"]):
            if idx == 0:  # 현재 증가율 의미 X
                continue
            if (i == -1) | (i == 0):  # -1이라면 None 값이므로 계산 X
                tmp_volume_ratio_lst.append("X")
            else:
                tmp_volume_ratio_lst.append(round(((tmp_data["vol"][0] - i) / i) * 100, 1))

        tmp_data["close_ratio"] = [None] + tmp_close_ratio_lst
        tmp_data["vol_ratio"] = [None] + tmp_volume_ratio_lst
        tmp_data["close"] = [round(i, 2) for i in tmp_data["close"]]
        tmp_data["vol"] = [round(i, 2) for i in tmp_data["vol"]]
        tmp_data = tmp_data[["close", "vol", "close_ratio", "vol_ratio", "Date"]]

        tmp_value = [
            tmp_data.iloc[0, 0],  # 기준일 종가
            tmp_data.iloc[0, 1],  # 기준일 거래량
            # 종가 증가율
            tmp_data.iloc[1, 2],  # 한달전 대비 종가 증가율
            tmp_data.iloc[2, 2],  # 3달전 대비 종가 증가율
            tmp_data.iloc[3, 2],  # 6달전 대비 종가 증가율
            tmp_data.iloc[4, 2],  # 1년전 대비 종가 증가율
            tmp_data.iloc[5, 2],  # 3년전 대비 종가 증가율
            tmp_data.iloc[6, 2],  # 5년전 대비 종가 증가율
            tmp_data.iloc[7, 2],  # 10년전 대비 종가 증가율
            # 거래량 증가율
            tmp_data.iloc[1, 3],  # 한달전 대비 거래량 증가율
            tmp_data.iloc[2, 3],  # 3달전 대비 거래량 증가율
            tmp_data.iloc[3, 3],  # 6달전 대비 거래량 증가율
            tmp_data.iloc[4, 3],  # 1년전 대비 거래량 증가율
            tmp_data.iloc[5, 3],  # 3년전 대비 거래량 증가율
            tmp_data.iloc[6, 3],  # 5년전 대비 거래량 증가율
            tmp_data.iloc[7, 3],  # 10년전 대비 거래량 증가율
            # 종가 정리
            tmp_data.iloc[1, 0],  # 한달전 종가
            tmp_data.iloc[2, 0],  # 3달전 종가
            tmp_data.iloc[3, 0],  # 6달전 종가
            tmp_data.iloc[4, 0],  # 1년전 종가
            tmp_data.iloc[5, 0],  # 3년전 종가
            tmp_data.iloc[6, 0],  # 5년전 종가
            tmp_data.iloc[7, 0],  # 10년전 종가
            # 거래량 정리
            tmp_data.iloc[1, 1],  # 한달전 거래량
            tmp_data.iloc[2, 1],  # 3달전 거래량
            tmp_data.iloc[3, 1],  # 6달전 거래량
            tmp_data.iloc[4, 1],  # 1년전 거래량
            tmp_data.iloc[5, 1],  # 3년전 거래량
            tmp_data.iloc[6, 1],  # 5년전 거래량
            tmp_data.iloc[7, 1],  # 10년전 거래량
        ]

        tmp_final_value = stock_data[stock_data["Symbol"] == tmp_stock].values[0].tolist() + tmp_value
        final_data_lst.append(tmp_final_value)

    # 데이터 존재하지 않는 리스트 처리
    except_stock_lst = []
    new_final_data_lst = []
    for idx, i in enumerate(final_data_lst):
        if i[3] == -1:
            except_stock_lst.append(i[0])
        else:
            new_final_data_lst.append(i)

    # 데이터 존재하지 않는 리스트 처리
    except_stock_lst = []
    new_final_data_lst = []
    for idx, i in enumerate(final_data_lst):
        if i[3] == -1:
            except_stock_lst.append(i[0])
        else:
            new_final_data_lst.append(i)

    if len(except_stock_lst) != 0:
        add_except_stock(except_stock_lst, "데이터가 존재하지 않음")

    # 구글 스프레드 시트 입력
    close_vol_sheet = doc.worksheet("종가, 거래량 정보(결과)")
    set_with_dataframe(
        close_vol_sheet,
        pd.DataFrame(new_final_data_lst),
        row=4,
        include_index=False,
        include_column_header=False,
    )
