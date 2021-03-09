def normalizeNum(num, pad):
	r = str(num)
	while len(r) < pad:
		r = '0' + r
	return r

def formatDate(date):
	return f'{date.day}/{date.month}/{date.year}'

def formatTime(date):
	return f'{normalizeNum(date.hour, 2)}:{normalizeNum(date.minute, 2)}'

def formatPostDate(date):
	return formatDate(date)

def formatCommentDate(date):
	return f'{formatDate(date)} {formatTime(date)}'