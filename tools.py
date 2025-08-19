from langchain_core.messages import tool


@tool
def get_official_price_list():
    with open("company_info/price_list.txt", "r") as file:
        price_list = file.read()
    return price_list


@tool
