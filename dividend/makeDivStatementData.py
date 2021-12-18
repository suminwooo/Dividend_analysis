import yfinance as yf
import collections
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time


def import_data(stock_name):
    """
    데이터 불러오기
    """
    ticker = yf.Ticker(stock_name)
    info_data = ticker.info

    # 데이터가 존재하지 않을 경우 바로 예외처리 해주기
    if (len(info_data) < 5) | ("sector" not in info_data) | ("industry" not in info_data):
        return "데이터 존재X"

    cashflow_data = ticker.cashflow.reset_index()
    earnings_data = ticker.earnings.reset_index()
    actions_data = ticker.actions.reset_index()
    price_data = yf.download(stock_name)
    return info_data, cashflow_data, earnings_data, actions_data, price_data


def _change_money_size(money_lst):
    """
    1000불이상일경우 k붙이기
    """
    new_lst = []
    for i in money_lst:
        if abs(i) >= 100000:
            new_lst.append(str(int(i / 1000)) + "k")
        else:
            new_lst.append(int(i))

    return new_lst


def find_sector_industry(info_data):
    sector = info_data["sector"]
    industry = info_data["industry"]
    name = info_data["shortName"]
    if (sector == None) | (industry == None):
        return "sector, industry 존재 X"
    return {"sector": sector, "industry": industry, "name": name}


def find_dividend_info(info_data, actions_data, price_data):
    """
    배당 관련 정보 출력
    """
    # 필요 변수 선언
    isDividendCompare2008 = False
    isDividendCompare2020 = False
    isDividendCompare2008Ratio = False
    isDividendCompare2020Ratio = False

    # 배당 데이터 수정
    dividend_data = actions_data[["Date", "Dividends"]]
    dividend_data = dividend_data[dividend_data["Dividends"] > 0]  # 주식분할 정보있을경우 배당이 0으로 표시됨
    dividend_data["Year"] = [str(i)[:4] for i in list(dividend_data["Date"])]  # year 출력
    dividend_data["Month"] = [str(i)[5:7] for i in list(dividend_data["Date"])]  # month 출력

    # 배당 데이터 존재 유무 체크
    if len(dividend_data) == 0:
        return "배당 데이터X"

    # 배당 유무 확인
    if len(dividend_data[dividend_data["Year"] == "2021"]) == 0:
        return "2021년 배당 데이터X"

    # 마지막 배당일
    lastDividendDate = str(dividend_data.iloc[-1]["Date"])[:10]

    # 마지막 배당 당시 주가(시가 배당률 계산에 필요)
    tmp_price_data = price_data.loc[lastDividendDate]["Close"]

    # 2018,19,20년 배당 수가 일정한지 체크
    dividend_cnt_2018 = len(dividend_data[dividend_data["Year"] == "2018"])
    dividend_cnt_2019 = len(dividend_data[dividend_data["Year"] == "2019"])
    dividend_cnt_2020 = len(dividend_data[dividend_data["Year"] == "2020"])

    if (
        (dividend_cnt_2018 != dividend_cnt_2019)
        | (dividend_cnt_2019 != dividend_cnt_2020)
        | (dividend_cnt_2018 != dividend_cnt_2020)
    ):
        return "2018,19,20 배당 수 일정X"

    # 배당주기 셋팅(1=연배당 / 2=반기배당 / 4=분기배당 / 12=월배당)
    dividendCycle_cnt = dividend_cnt_2020

    # 시가 배당률 입력(marketDividendRate = 마지막배당금액 / 마지막배당당시주가)
    marketDividendRate = str(round((info_data["lastDividendValue"] / tmp_price_data) * 100, 2)) + "%"

    # 꾸준하게 배당 연속 지급 시작 연도
    for each_yr, each_yr_val in collections.Counter(list(dividend_data["Year"][::-1])).items():
        if each_yr_val != dividendCycle_cnt:
            break
    dividendStart = str(int(each_yr) - 1) + "~" + str(int(each_yr))

    # 최근 배당 연속 증가 횟수
    tmp_min = 999
    increasedCount = 0
    # i는 위에서 배당 연속 지급 년도 마지막
    for each_div in list(dividend_data[dividend_data["Year"] >= str(int(each_yr) + 1)]["Dividends"][::-1]):
        if each_div <= tmp_min:
            tmp_min = each_div
            increasedCount += 1
        else:
            break

    # 최근 1년간 배당 기간 입력
    if dividendCycle_cnt == 1:  # 연배당
        dividendCycle = "연간배당"
        dividendMonth = [str(i)[:10] for i in dividend_data["Date"]][-1]
        forwardNextDividendDate = (
            datetime.strptime(lastDividendDate, "%Y-%m-%d") + relativedelta(months=12)
        ).strftime("%Y-%m-%d")
        raw_increasedDate = increasedCount
        increasedDate = str(round(raw_increasedDate / 12, 2)) + "년 이상"

        # 2008, 2020 배당 조건 체크
        if len(dividend_data[dividend_data["Year"] == "2008"]) == 1:
            isDividendCompare2008 = True
        if len(dividend_data[dividend_data["Year"] == "2020"]) == 1:
            isDividendCompare2020 = True

    elif dividendCycle_cnt == 2:  # 반기 배당
        dividendCycle = "반기배당"
        dividendMonth = [str(i)[:10] for i in dividend_data["Date"]][-2:]
        forwardNextDividendDate = (
            datetime.strptime(lastDividendDate, "%Y-%m-%d") + relativedelta(months=6)
        ).strftime("%Y-%m-%d")
        raw_increasedDate = increasedCount * 2
        increasedDate = str(round(raw_increasedDate / 12, 2)) + "년 이상"

        # 2008, 2020 배당 조건 체크
        if len(dividend_data[dividend_data["Year"] == "2008"]) == 2:
            isDividendCompare2008 = True
        if len(dividend_data[dividend_data["Year"] == "2020"]) == 2:
            isDividendCompare2020 = True

    elif dividendCycle_cnt == 4:  # 분기 배당
        dividendCycle = "분기배당"
        dividendMonth = [str(i)[:10] for i in dividend_data["Date"]][-4:]
        forwardNextDividendDate = (
            datetime.strptime(lastDividendDate, "%Y-%m-%d") + relativedelta(months=3)
        ).strftime("%Y-%m-%d")
        raw_increasedDate = increasedCount * 4
        increasedDate = str(round(raw_increasedDate / 12, 2)) + "년 이상"

        # 2008, 2020 배당 조건 체크
        if len(dividend_data[dividend_data["Year"] == "2008"]) == 4:
            isDividendCompare2008 = True
        if len(dividend_data[dividend_data["Year"] == "2020"]) == 4:
            isDividendCompare2020 = True

    elif dividendCycle_cnt == 12:  # 월 배당
        dividendCycle = "월배당"
        dividendMonth = [str(i)[:10] for i in dividend_data["Date"]][-12:]
        forwardNextDividendDate = (
            datetime.strptime(lastDividendDate, "%Y-%m-%d") + relativedelta(months=1)
        ).strftime("%Y-%m-%d")
        raw_increasedDate = increasedCount * 12
        increasedDate = str(round(raw_increasedDate / 12, 2)) + "년 이상"

        # 2008, 2020 배당 조건 체크
        if len(dividend_data[dividend_data["Year"] == "2008"]) == 12:
            isDividendCompare2008 = True
        if len(dividend_data[dividend_data["Year"] == "2020"]) == 12:
            isDividendCompare2020 = True

    # 배당 비교
    tmp_mean_2007 = (dividend_data[dividend_data["Year"] == "2007"]["Dividends"]).mean()
    tmp_mean_2008 = (dividend_data[dividend_data["Year"] == "2008"]["Dividends"]).mean()
    tmp_mean_2019 = (dividend_data[dividend_data["Year"] == "2019"]["Dividends"]).mean()
    tmp_mean_2020 = (dividend_data[dividend_data["Year"] == "2020"]["Dividends"]).mean()

    if tmp_mean_2007 <= tmp_mean_2008:
        isDividendCompare2008Ratio = True
    if tmp_mean_2019 <= tmp_mean_2020:
        isDividendCompare2020Ratio = True

    # 배당 성향 종류 정리
    if raw_increasedDate < 5:
        typePayout = "해당 없음"
    elif raw_increasedDate / 12 < 10:
        typePayout = "배당 블루칩"
    elif raw_increasedDate / 12 < 25:
        typePayout = "배당 챔피언"
    elif raw_increasedDate / 12 < 50:
        typePayout = "배당 귀족"
    else:
        typePayout = "배당킹"

    # 5년전 평균 배당 수익률 값 없을 경우 -> None
    if info_data["fiveYearAvgDividendYield"] == None:
        fiveYearAvgDividendYield = "-"
    else:
        fiveYearAvgDividendYield = str(info_data["fiveYearAvgDividendYield"]) + "%"

    # 최종 결과 데이터
    result = {
        # 배당 지표 및 정보
        "lastDividendValue": str(info_data["lastDividendValue"]) + "$",
        "lastDividendDate": lastDividendDate,
        "dividendRate": str(info_data["dividendRate"]) + "%",
        "dividendYield": str(round(info_data["dividendYield"] * 100, 4)) + "%",
        "marketDividendRate": marketDividendRate,
        "payoutRatio": str(round(info_data["payoutRatio"] * 100, 4)) + "%",
        "trailingAnnualDividendYield": str(info_data["trailingAnnualDividendYield"] * 100) + "%",
        "trailingAnnualDividendRate": str(info_data["trailingAnnualDividendRate"]) + "%",
        "fiveYearAvgDividendYield": fiveYearAvgDividendYield,
        # 배당 기간 관련 정보
        "dividendCycle": dividendCycle,
        "dividendMonth": dividendMonth,
        "forwardNextDividendDate": str(forwardNextDividendDate) + " 전 후 예상",
        "dividendStart": dividendStart,
        "increasedDate": increasedDate,
        "increasedCount": str(increasedCount) + "회",
        "typePayout": typePayout,
        # 과거 비교
        "isDividendCompare2008": isDividendCompare2008,
        "isDividendCompare2020": isDividendCompare2020,
        "isDividendCompare2008Ratio": isDividendCompare2008Ratio,
        "isDividendCompare2020Ratio": isDividendCompare2020Ratio,
    }
    return result


def find_split_info(actions_data, price_data):

    split_data = actions_data[["Date", "Stock Splits"]]
    split_data = split_data[split_data["Stock Splits"] > 0].reset_index(drop=True)
    split_data["Date"] = split_data["Date"].astype(str)

    if len(split_data) == 0:
        return "액면 분할 정보 없음"

    last_split_date = split_data.iloc[-1, 0]
    last_split_ratio = "1:" + str(int(split_data.iloc[-1, 1]))

    last_after_one_month = (datetime.strptime(last_split_date, "%Y-%m-%d") + relativedelta(months=1)).strftime(
        "%Y-%m-%d"
    )
    last_split_stock_price = price_data.loc[last_split_date]["Close"]  # 액면 분할 당시 가격
    if len(price_data.loc[last_after_one_month:]) != 0:
        last_split_stock_price_after_one_month = price_data.loc[last_after_one_month:]["Close"][
            0
        ]  # 액면 분할 후 한달후 가격
        last_price_ratio = round(
            (
                (last_split_stock_price - last_split_stock_price_after_one_month)
                / last_split_stock_price_after_one_month
            )
            * 100,
            2,
        )
    else:
        last_split_stock_price_after_one_month = "아직 한달이 지나지 않음"
        last_price_ratio = "존재하지 않음"
    total_split_data_cnt = len(split_data)
    five_yr_before_today_split_data = split_data[
        split_data["Date"]
        >= (datetime.strptime(last_split_date, "%Y-%m-%d") + relativedelta(years=-5)).strftime("%Y-%m-%d")
    ]
    within_5_year_cnt = len(five_yr_before_today_split_data)

    result = {
        "last_split_date": last_split_date,
        "last_split_ratio": last_split_ratio,
        "last_price_ratio": last_price_ratio,
        "total_split_cnt": total_split_data_cnt,
        "split_cnt_within_5yr": within_5_year_cnt,
    }
    return result


def find_statement_info(info_data, earnings_data, cashflow_data):
    """
    재무 데이터 출력
    """
    # 순이익, 매출액, 현금 흐름
    earning_4yr_lst = _change_money_size(list(earnings_data["Earnings"])[::-1])  # 순이익
    revenue_4yr_lst = _change_money_size(list(earnings_data["Revenue"])[::-1])  # 매출액
    cash_flow_4yr_lst = _change_money_size(
        (
            cashflow_data[
                (cashflow_data["index"] == "Total Cashflows From Investing Activities")
                | (cashflow_data["index"] == "Total Cash From Operating Activities")
                | (cashflow_data["index"] == "Other Cashflows From Financing Activities")
            ]
        )
        .sum()
        .tolist()[1:][::-1]
    )  # 현금 흐름

    # 변화율
    earning_ratio_lst = []
    revenue_ratio_lst = []
    cash_ratio_lst = []
    for i in range(3):
        # earning 변화율
        earning_tmp_lst = list(earnings_data["Earnings"])[::-1]
        earning_ratio_lst.append(
            str(round(((earning_tmp_lst[i + 1] - earning_tmp_lst[i]) / abs(earning_tmp_lst[i])) * 100, 2)) + "%"
        )
        # revenue 변화율
        revenue_tmp_lst = list(earnings_data["Revenue"])[::-1]
        revenue_ratio_lst.append(
            str(round(((revenue_tmp_lst[i + 1] - revenue_tmp_lst[i]) / abs(revenue_tmp_lst[i])) * 100, 2)) + "%"
        )
        # 현금 흐름 변화율
        cash_tmp_lst = (
            (
                cashflow_data[
                    (cashflow_data["index"] == "Total Cashflows From Investing Activities")
                    | (cashflow_data["index"] == "Total Cash From Operating Activities")
                    | (cashflow_data["index"] == "Other Cashflows From Financing Activities")
                ]
            )
            .sum()
            .tolist()[1:][::-1]
        )
        cash_ratio_lst.append(
            str(round(((cash_tmp_lst[i + 1] - cash_tmp_lst[i]) / abs(cash_tmp_lst[i])) * 100, 2)) + "%"
        )

    # 아래 5개의 값은 데이터가 없을 경우를 위해 처리(중요한 데이터X)
    # forwardEps 처리
    if info_data["forwardEps"] == None:
        forwardEps = "-"
    else:
        forwardEps = info_data["forwardEps"]

    # trailingEps 처리
    if info_data["trailingEps"] == None:
        trailingEps = "-"
    else:
        trailingEps = info_data["trailingEps"]

    # trailingPE 처리
    try:
        if info_data["trailingPE"] == None:
            trailingPE = "-"
        else:
            trailingPE = info_data["trailingPE"]
    except:
        trailingPE = "-"

    # forwardPE 처리
    try:
        if info_data["forwardPE"] == None:
            forwardPE = "-"
        else:
            forwardPE = info_data["forwardPE"]
    except:
        forwardPE = "-"

    # returnOnEquity 처리
    try:
        if info_data["returnOnEquity"] == None:
            returnOnEquity = "-"
        else:
            returnOnEquity = info_data["returnOnEquity"]
    except:
        returnOnEquity = "-"

    result = {
        "earning_4yr_lst": earning_4yr_lst,
        "revenue_4yr_lst": revenue_4yr_lst,
        "cash_flow_4yr_lst": cash_flow_4yr_lst,
        "earning_ratio_lst": earning_ratio_lst,
        "revenue_ratio_lst": revenue_ratio_lst,
        "cash_ratio_lst": cash_ratio_lst,
        "forwardEps": forwardEps,
        "trailingEps": trailingEps,
        "trailingPE": trailingPE,
        "forwardPE": forwardPE,
        "returnOnEquity": returnOnEquity,
    }
    return result


def find_total_information(stock_name):
    # data import
    data_lst = import_data(stock_name)
    if data_lst == "데이터 존재X":
        return "데이터 존재X"
    info_data, cashflow_data, earnings_data, actions_data, price_data = data_lst

    # 데이터 분류 및 정리
    sector_dic = find_sector_industry(info_data)
    devidend_dic = find_dividend_info(info_data, actions_data, price_data)
    split_dic = find_split_info(actions_data, price_data)
    statement_dic = find_statement_info(info_data, earnings_data, cashflow_data)

    result = {
        "sector_dic": sector_dic,
        "devidend_dic": devidend_dic,
        "split_dic": split_dic,
        "statement_dic": statement_dic,
    }
    return result


def make_dividend_statement_data(stock_lst):
    print("pass")
    total_dic = {}
    no_dividend_data_stock_lst = []  # "배당 데이터X"
    no_2021_dividend_data_stock_lst = []  # "2021년 배당 데이터X"
    not_constant_data_during_20181920_stock_lst = []  # "2018,19,20 배당 수 일정X"
    no_data_stock_lst = []  # "데이터 존재X"
    unknown_err_lst = []  # "알수 없는 에러"
    for idx, each_stock in enumerate(stock_lst):
        try:
            print(each_stock)
            print(round(idx / len(stock_lst) * 100, 2), "% 진행중")
            tmp_dic = find_total_information(each_stock)

            if tmp_dic == "데이터 존재X":
                print("데이터 존재X")
                no_data_stock_lst.append(each_stock)
                continue
            if tmp_dic["devidend_dic"] == "배당 데이터X":
                print("배당 데이터X")
                no_dividend_data_stock_lst.append(each_stock)
                continue
            elif tmp_dic["devidend_dic"] == "2021년 배당 데이터X":
                print("2021년 배당 데이터X")
                no_2021_dividend_data_stock_lst.append(each_stock)
                continue
            elif tmp_dic["devidend_dic"] == "2018,19,20 배당 수 일정X":
                print("2018,19,20 배당 수 일정X")
                not_constant_data_during_20181920_stock_lst.append(each_stock)
                continue
            total_dic[each_stock] = tmp_dic
            print(each_stock, "입력 완료")
            print("*" * 100)
        except Exception as e:
            print(each_stock, "예외가 발생했습니다.", e)
            unknown_err_lst.append(each_stock)
            print("*" * 100)
        time.sleep(5)
    result = [
        total_dic,
        no_dividend_data_stock_lst,
        no_2021_dividend_data_stock_lst,
        not_constant_data_during_20181920_stock_lst,
        no_data_stock_lst,
        unknown_err_lst,
    ]
    return result
