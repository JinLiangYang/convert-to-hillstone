import re

line = ' extended permit object-group sxwifi-group any object sxwifi-10.190.178.139 '

pattern = re.compile(r'extended (permit|deny) object-group ((\w*)(-*)(\w*)(\d*)) any (object|object-group) ')
match = pattern.search(line)

if match:
    print(1)
else:
    print(0)
