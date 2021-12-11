# 구글 스프레트 시트
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# 구글 스프레드 시트
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
json_file_name = "./api_key/google_key.json"

spread_credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(spread_credentials)
spreadsheet_url = (
    "https://docs.google.com/spreadsheets/d/1ZcYkDFfDqY8DsdH2o5k1oSJW4UXj1sHBhgOXBWebzQI/edit#gid=0"
)
doc = gc.open_by_url(spreadsheet_url)
