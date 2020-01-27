#!/usr/bin/env python3
"""

:Author: Anemone Xu
:Email: anemone95@qq.com
:copyright: (c) 2020 by Anemone Xu.
:license: Apache 2.0, see LICENSE for more details.
"""
import time

import requests
import websocket._core


# burp0_url = "https://www.overleaf.com:443/socket.io/1/?t=1580045496999"
burp0_cookies = {"_ga": "GA1.2.478645579.1578535220", "gke-route": "1580040871.695.284.307812", "_gid": "GA1.2.645118176.1580040889", "hidei18nNotification": "true", "overleaf_session2": "s%3ATfY8D35k6H4YJccEffelAgfhlTXmTpw6.PDPysaJuvzyLGrgyxlbjYAJ%2B8CAHJS0u1Nwf3JoOsT0", "_gat": "1"}
# requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)

text="""
GET /socket.io/1/websocket/YanrTxH-C1jdZ1FM_baO HTTP/1.1
Origin: https://www.overleaf.com
Sec-WebSocket-Key: 4f5Z2uhBuGcdRYY7+gKiSA==
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Version: 13
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
Host: www.overleaf.com
Cache-Control: no-cache
Cookie: gke-route=1580107614.63.284.395821; overleaf_session2=s%3AGkgHLQLOcsW1lCTA0NvmzpgeH5pzThTO.KmOOOmlup1%2FXCBqQsGkMKHCEsDkG0m0C4VPLGLV0fXo; _ga=GA1.2.1143826100.1580107620; _gid=GA1.2.1189049313.1580107620; _gat=1
"""

def test():
    burp0_headers = {"Origin": "https://www.overleaf.com", "Sec-WebSocket-Key": "L7xuDs4GQz99aN1PhsMcDg==",
                     "Connection": "Upgrade", "Upgrade": "websocket", "Sec-WebSocket-Version": "13",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
                     "Cache-Control": "no-cache"}
    ws = websocket._core.create_connection("wss://www.overleaf.com/socket.io/1/websocket/6J5KX1MNYITueV41_ba9", header=burp0_headers, cookies=burp0_cookies)
    print("Sending 'Hello, World'...")
    # ws.send(text.replace("\r\n","\n").replace("\n","\r\n"))
    print(ws.headers)
    print("Receiving...")
    result = ws.recv()
    print("Received '%s'" % result)
    result = ws.recv()
    print("Received '%s'" % result)
    ws.close()


if __name__ == '__main__':
    test()
