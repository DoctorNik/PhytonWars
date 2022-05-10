import requests as r

# link = 'http://127.0.0.1:8080/api/katas/difficulty/6/htl'
# link = 'http://127.0.0.1:8080/api/users/experience/2/123'
# link = 'http://127.0.0.1:8080/api/user/12'
#
# link = "http://127.0.0.1:8080/api/kata/3"
# link = "http://127.0.0.1:8080/api/katas/difficulty/1/htl"
# link = "http://127.0.0.1:8080/api/users/createdKatas/1/lth"
# print(requests.get(link).json())

print(requests.post("http://127.0.0.1:8080/api/postuser").json())