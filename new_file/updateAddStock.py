from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
from datetime import datetime
from new_file.config import doc


def update_add_stock(result):
    # 1. 시트 및 데이터 가져오기
    except_stock_sheet = doc.worksheet("제외된 종목 리스트(결과)")
    remove_stock_sheet = doc.worksheet("제외할 종목 시트(입력)")
    existing_stocks_list_sheet = doc.worksheet("기존 종목 리스트")

    existing_stocks_list_data = get_as_dataframe(existing_stocks_list_sheet)
    except_stock_data = get_as_dataframe(except_stock_sheet)
    remove_stock_data = get_as_dataframe(remove_stock_sheet)

    update_month = datetime.now().month  # 업데이트 월

    # 2. 제외할 종목에 대한 리스트 생성
    except_lst = list(list(i) for i in except_stock_data[["종목 코드", "근거"]].dropna().values)  # 기존 데이터 두기

    # 기존 제외할 리스트에 추가된 종목
    for i in list(remove_stock_data["종목 코드"].dropna()):
        except_lst.append([i, "제외할 리스트에 추가되어 있음"])
    # "배당 데이터X"
    for i in result[1]:
        except_lst.append([i, "배당 데이터X"])

    # "2021년 배당 데이터X"
    for i in result[2]:
        except_lst.append([i, "2021년 배당 데이터X"])

    # "2018,19,20 배당 수 일정X"
    for i in result[3]:
        except_lst.append([i, "2018,19,20 배당 수 일정X"])
    # "데이터 존재X"
    for i in result[4]:
        except_lst.append([i, "데이터 존재X"])
    # "알수 없는 에러"
    for i in result[5]:
        except_lst.append([i, "알수 없는 에러"])

    # 3. 리스트 중복 제거
    new_except_lst, check_duplicate = [], []
    for i in except_lst:
        if i[0] in check_duplicate:
            continue
        else:
            check_duplicate.append(i[0])
            new_except_lst.append(i)

    # 3. 제외된 종목 리스트(결과) 초기화
    set_with_dataframe(
        except_stock_sheet,
        pd.DataFrame([[None] * 2] * 100),
        row=2,
        include_index=False,
        include_column_header=False,
    )

    # 4. 제외된 종목 리스트(결과) 데이터 입력
    set_with_dataframe(
        except_stock_sheet,
        pd.DataFrame(new_except_lst),
        row=2,
        include_index=False,
        include_column_header=False,
    )

    # 5. 업데이트 되지 않은 셀 확인
    not_update_col = []
    for i in range(4):
        each_group_update_month = existing_stocks_list_data.iloc[0, i]
        if update_month != each_group_update_month:
            not_update_col.append(i)

    # 5. 기존 종목 리스트 업데이트
    set_with_dataframe(
        existing_stocks_list_sheet,
        pd.DataFrame([None] * 51),
        row=2,
        col=not_update_col[0] + 1,
        include_index=False,
        include_column_header=False,
    )

    # 4. 제외된 종목 리스트(결과) 데이터 입력
    set_with_dataframe(
        existing_stocks_list_sheet,
        pd.DataFrame([update_month] + list(result[0].keys())),
        row=2,
        col=not_update_col[0] + 1,
        include_index=False,
        include_column_header=False,
    )
