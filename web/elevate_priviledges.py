from python.db import getDB

username = input('Username: ')

uuid = getDB().getUserUUID(username)

print('UUID: ' + uuid)

print('Permission level: ' + str(getDB().getUserPerms(uuid)))

new_level = int(input('New permission level: '))

getDB().setUserPerms(uuid, new_level)


print('Permission level set')