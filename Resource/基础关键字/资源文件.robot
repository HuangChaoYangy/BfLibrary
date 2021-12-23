*** Settings ***
Library           C:\\Python\\Lib\\site-packages\\BfLibrary    ${mysql_info}    ${mongo_info}
Library           Collections

*** Variables ***
@{mysql_info}     192.168.10.120    root    s3CDfgfbFZcFEaczstX1VQrdfRFEaXTc    3306
@{mongo_info}     app    123456    192.168.10.120    27017
${merchant_url}    http://192.168.10.11
${backend_url}    http://192.168.10.120:8092
@{merchant_list}    李扬测试商户1
@{运动类型}           足球    篮球    网球    排球    羽毛球    乒乓球    棒球    冰上曲棍球
@{币种列表}           人民币    美元    泰铢    印尼盾    越南盾    日元    韩元    印度卢比
@{client_user_list}    USD_result11
${merchant}       李扬测试商户1
