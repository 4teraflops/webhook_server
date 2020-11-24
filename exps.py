from datetime import datetime

now = datetime.now()
time = now.strftime('%Y-%m-%d %H:%M:%S')

print(time)