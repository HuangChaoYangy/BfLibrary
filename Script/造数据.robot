*** Settings ***
Library           RequestsLibrary
Resource          ../Resource/基础关键字/资源文件.robot
Library           RequestsLibrary

*** Test Cases ***
指定某场比赛投注单注
    @{token_list}    Create List
    FOR    ${user}    IN    @{client_user_list}
        ${token}    Login    ${merchant}    ${user}    prefix=ll
        Append To List    ${token_list}    ${token}
    END
    log    ${token_list}
    Single Submit All Outcome    sr:match:27023778    网球    token=${token_list[0]}
