from util.request import Request
import bcrypt
import html

def extract_credentials(request):
    body = request.body.decode('utf-8')
    body = body.split('&')
    username = body[0]
    password = body[1]
    username = username.split('=')
    username = username[1]
    password = password.split('=')
    password = password[1]

    newpassword = ''
    index = 0
    while index < len(password):
        if password[index] == '%':
            hex = password[index + 1:index + 3]
            # print(hex)
            hex = chr(int(hex, 16))
            newpassword = newpassword + hex
            index += 3
        else:
            # print("1")
            newpassword = newpassword + password[index]
            index += 1
    return [html.escape(username), newpassword]


def validate_password(password):
    if len(password) < 8:
        return False
    lowercase = False
    uppercase = False
    number = False
    symbol = False
    special = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}
    for char in password:
        if char in special:
            symbol = True
        elif char.islower():
            lowercase = True
        elif char.isdigit():
            number = True
        elif char.isupper():
            uppercase = True
        else:
            return False

    return lowercase and uppercase and number and symbol


if __name__ == '__main__':
    word = "Qwert=yu8"
    print(validate_password(word))
    # word = word.encode('utf-8')
    # salt = bcrypt.gensalt()
    # hashed = bcrypt.hashpw(word,salt)
    # otherpass = "Qwert=yu8"
    # otherpass = otherpass.encode('utf-8')
    # result = bcrypt.checkpw(otherpass, hashed)
    # print(result)
    # print(hashed.decode('utf-8'))