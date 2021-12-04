from dividend.config import doc


def add_except_stock(stock_lst, description, type_check=False):
    """
    제외된 종목 입력 코드
    type_check : 제일 먼저 실행될 경우 스프레트 시트 초기화(type_check = 1일 경우)
    """
    if len(stock_lst) == 0:  # 리스트 값이 0일 경우 실행 X
        return

    worksheet_remove_stock_sheet = doc.worksheet("제외된 종목 리스트(결과)")

    # 초기화 및 head 입력
    if type_check is True:
        worksheet_remove_stock_sheet.clear()
        worksheet_remove_stock_sheet.append_row(["종목 코드", "근거"])

    # 시트 입력
    for each_stock in stock_lst:
        worksheet_remove_stock_sheet.append_row([each_stock, description])
