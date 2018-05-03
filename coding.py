# 说明：
# UTF兼容ISO8859-1和ASCII，
# GB18030兼容GBK，GBK兼容GB2312，GB2312兼容ASCII

CODES = ['UTF-8', 'UTF-16', 'GB18030', 'BIG5']

# UTF-8 BOM前缀字节
UTF_8_BOM = b'\xef\xbb\xbf'
 
# 获取文件编码类型
def file_encoding(file_path):
 """
 获取文件编码类型\n
 :param file_path: 文件路径\n
 :return: \n
 """
 with open(file_path, 'rb') as f:
  test=string_encoding(f.read())
  return string_encoding(f.read())
 

# 获取字符编码类型
def string_encoding(b, bytes):
"""
 获取字符编码类型\n
 :param b: 字节数据\n
 :return: \n
 """
# 遍历编码类型
  for code in CODES:
   try:
    b.decode(encoding=code)
    if 'UTF-8' == code and b.startswith(UTF_8_BOM):
     return 'UTF-8-SIG'
    return code
   except Exception:
    continue
  return '未知的字符编码类型'
''''''