from dividend.checkUpdateOrMake import check_update_or_make
from dividend.setStockData import set_stock_data
from dividend.findStockList import find_stock_list
from dividend.makeDivStatementData import make_dividend_statement_data
from dividend.updateDivSplitStatementSheet import update_div_split_statement_sheet
from dividend.updateCloseVolSheet import update_close_vol_sheet
from dividend.updateAddStock import update_add_stock
from dividend.checkListUpdate import check_update
from dividend.resetStockList import reset_stock_list


def main():

    # 0. 추가할지 새로 만들지 설정
    print("type_check")
    type_check = check_update_or_make()
    IsUpdate = None
    if type_check == "all update":
        reset_stock_list()
        return
    elif type_check == "make new data":
        IsUpdate = False
    elif type_check == "update data":
        IsUpdate = True

    # 1. 추가할 종목 제외할 종목을 활용한 기존 종목 리스트 업데이트
    print("start_col")
    start_col = set_stock_data()
    if start_col == "업데이트X":
        return

    # 2. 업데이트할 종목 리스트 찾기
    print("check_stock_lst")
    check_stock_lst = find_stock_list(start_col)
    print(check_stock_lst)
    # 3. 1번에서 찾은 종목에 대한 배당, 재무정보 찾기
    print("make_dividend_statement_data")
    result = make_dividend_statement_data(check_stock_lst)

    # 임시 -------------------------------
    import pickle

    # save data
    with open("user.pickle", "wb") as fw:
        pickle.dump(result, fw)

    # load data
    with open("user.pickle", "rb") as fr:
        result = pickle.load(fr)

    # 임시 -------------------------------

    # 4. 배당, 재무 정보 업데이트
    print("update_div_split_statement_sheet")
    update_div_split_statement_sheet(result, IsUpdate)

    # 5. 종가, 거래량 정보 업데이트
    print("update_close_vol_sheet")
    update_close_vol_sheet(result, IsUpdate)

    # 6. 기존 종목 업데이트 및 데이터가 존재하지 않은 종목 처리
    print("update_add_stock")
    update_add_stock(result)

    # 7. 시트 업데이트 유무 확인
    check_update()


if __name__ == "__main__":
    main()
