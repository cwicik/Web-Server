import socket

HTTP_OK = "HTTP/1.1 200 OK\r\n"
ERROR_404 = "HTTP/1.1 404 OK\r\n"
ERROR_403 = "HTTP/1.1 403 Forbidden\r\n"
ERROR_302 = "HTTP/1.1 302 Found\r\n"
ERROR_500 = "HTTP/1.1 500 Internal Server Error\r\n"
ACC = "\r\nAccept:text/html\r\n"
CONTENT_LENGTH = "\r\nContent-Length:"
CONTENT_IMAGE = "Content-Type: image/jpeg"
CONTENT_GIF = "Content-Type: image/gif"
CONTENT_JS = "Content-Type: text/javascript; charset=UTF-8"
CONTENT_CSS = "Content-Type: text/css"
CONTENT_HTML = "Content-Type: text/html; charset=utf-8"


def create_server_socket(ip, port):
    """ input :  ip and port  output : server_socket    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)
    except socket.error as msg:
        server_socket.close()
        server_socket = None
        print(msg)
    return server_socket


class AccessDenied(Exception):
    pass


class RedirectToHomePage(Exception):
    pass


class InternalError(Exception):
    pass


def main():
    server_socket = create_server_socket('0.0.0.0', 2008)
    while True:
        client_socket, address = server_socket.accept()
        while True:
            try:
                data = client_socket.recv(1024).decode()
                print(data)
                if data == "":
                    break
                headers = data.split("\n")
                if headers[0].startswith('GET'):
                    resource = headers[0][headers[0].find("/") + 1:headers[0].rfind(" ")]
                    if resource == "":
                        resource = "index.html"
                    try:
                        content_type = CONTENT_HTML
                        if resource.endswith('.jpg'):
                            content_type = CONTENT_IMAGE
                        elif resource.endswith('.gif'):
                            content_type = CONTENT_GIF
                        elif resource.endswith('.js'):
                            content_type = CONTENT_JS
                        elif resource.endswith('.css'):
                            content_type = CONTENT_CSS
                        if resource.startswith('Forbidden'):
                            raise AccessDenied
                        if resource.startswith('RedirectToHome'):
                            raise RedirectToHomePage
                        if resource.startswith('ServerError'):
                            raise InternalError
                        with open(resource, 'rb') as page:
                            content = page.read()
                        res_str = HTTP_OK + content_type + CONTENT_LENGTH + str(len(content)) + ACC + "\r\n"
                    except FileNotFoundError:
                        resource = "404_error.html"
                        with open(resource, 'rb') as page:
                            content = page.read()
                        res_str = ERROR_404 + CONTENT_HTML + CONTENT_LENGTH + str(len(content)) + ACC + "\r\n"
                    except AccessDenied:
                        resource = "forbidden.html"
                        with open(resource, 'rb') as page:
                            content = page.read()
                        res_str = ERROR_403 + CONTENT_HTML + CONTENT_LENGTH + str(len(content)) + ACC + "\r\n"
                    except RedirectToHomePage:
                        resource = "RedirectToHome.html"
                        with open(resource, 'rb') as page:
                            content = page.read()
                        res_str = ERROR_302 + CONTENT_HTML + CONTENT_LENGTH + str(len(content)) + ACC + "\r\n"
                    except InternalError:
                        resource = "ServerError.html"
                        with open(resource, 'rb') as page:
                            content = page.read()
                        res_str = ERROR_500 + CONTENT_HTML + CONTENT_LENGTH + str(len(content)) + ACC + "\r\n"
                client_socket.send(res_str.encode() + content)
            except BaseException as e:
                print('error:', e)
                break


if __name__ == '__main__':
    main()
