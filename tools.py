from langchain_core.messages import tool


@tool
def prislista():
    """
    Returns a very detailed price list for the companys services.
    """
    with open("company_info/prislista.txt", "r") as file:
        price_list = file.read()
    return price_list
