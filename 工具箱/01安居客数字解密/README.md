# 安居客数字解密

## 背景说明
在获取安居客写字楼楼盘信息时，通常会有数字内容源码部分被加密的问题，对于后续数据加工处理造成难度。样例如下：
![](images/安居客加密数字样例.png)

## 使用说明
确保以下库均安装
    ```python
        import base64
        import re
        from io import BytesIO
        from fontTools.ttLib import TTFont 
    ```

## 编码思路
查看网页源代码后部分JavaScript中包含了解密钥匙，且加密方式为BASE64。
![](images/解密钥匙.png)

对应乱码表示为：
![](images/安居客加密数字样例2.png)

因此思路为：
1. 根据解密钥匙获取key_map

    ```python
        def get_keymap(html):
                """
                    对base64加密的页面内容进行解密
                """
                #获取密码
                keys_map = re.search(r'<script>!function\(w,d\)(.*?)<\/script>',html).group(1)
                #对密码解密转为map映射
                base64_str = re.search(r';base64,(.*?)\'\)', keys_map).group(1)
                font_content = base64.b64decode(base64_str)
                font = TTFont(BytesIO(font_content))
                keys = font.getBestCmap()
                keys = {hex(k)[2:] : str(int(v[-2:]) - 1) for k, v in keys.items()}
            return keys
    ```
    
2. 对加密价格执行替换
    
    ```python
        def keymap_replace(price,keys):
                for k, v in keys.items():
                    price = price.replace(f'&#x{k};', v)
            return price
    ```
    
