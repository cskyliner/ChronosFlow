import pandas as pd

df = pd.read_excel("address")

ttl = df.loc[:, ['日期', '交易额']]

col = ['日期', '总金额', '周']
result = pd.DataFrame(columns=col)

ttl = ttl.sort_values(by='日期')

sum = 0
date = ttl.values[0][0]

my_week = {3: 'Sunday', 4: 'Monday', 5: 'Tuesday', 6: 'Wednesday', 0: 'Thursday', 1: 'Friday', 2: 'Saturday'}

for i in range(len(ttl)):
	if date == ttl.values[i][0]:
		if not pd.isna(ttl.values[i][1]):
			sum += int(ttl.values[i][1])
	else:
		# 3月1日星期五
		day = int(date[8:]) % 7
		week = my_week[day]
		result.loc[date] = [date, sum, week]
		sum = 0
		if not pd.isna(ttl.values[i][1]):
			sum += int(ttl.values[i][1])
		date = ttl.values[i][0]

result.sort_values(by='总金额', inplace=True)

print(' '.join(map(str, result.values[0])))
print(' '.join(map(str, result.values[1])))
print(' '.join(map(str, result.values[2])))

