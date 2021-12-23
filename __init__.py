try:
    from Bf_Client import Bf_Client
    from ThridMerchant import Third_Merchant
    from H5_BfClient import H5_BfClient
    from H5_Odds import H5_Bfclient_odds
    from MysqlFunc import MysqlQuery
    from MongoFunc import DbQuery
except ModuleNotFoundError or ImportError:
    from .Bf_Client import Bf_Client
    from .ThridMerchant import Third_Merchant
    from .H5_BfClient import H5_BfClient
    from .H5_Odds import H5_Bfclient_odds
    from .MysqlFunc import MysqlQuery
    from .MongoFunc import DbQuery

# , H5_Bfclient_odds, H5_BfClient
class BfLibrary(Bf_Client, Third_Merchant):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    def __init__(self, mysql_info, mongo_info):

        Third_Merchant.__init__(self, mysql_info)
        Bf_Client.__init__(self, mysql_info, mongo_info)

        # H5_Bfclient_odds.__init__(self)
        # H5_BfClient.__init__(self, mysql_info, mongo_info, backend_url, merchant_url)

if __name__ == "__main__":
    yg = BfLibrary(['192.168.10.120', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306'],
                   ['app', '123456', '192.168.10.120', '27017'])
    print(dir(yg))