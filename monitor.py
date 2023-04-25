#This program is a web monitor that is able to return status codes when provided with url links to http websites (http only), it is also able to follow redirected links and refrenced images allowing with their status codes.
import sys
import socket

# get urls_file name from command line
if len(sys.argv) != 2:
    print('Usage: monitor urls_file')
    sys.exit()

# text file to get list of urls
urls_file = sys.argv[1]
#This function parses the URLs for their port, host, and path
def parse(line, redirected = "false", refrenced = "false"):
    host = ""
    path = ""
    port = ""
    url = ""
    line = line.strip()
    url = line
    if line.startswith("http://"):
        port = "80"
        line = line[7:]
    elif line.startswith("https://"):
        port = "443"
        line = line[8:]
    path_start = line.find("/")
    if path_start == -1:
        path = "/"  # no path found, set empty string
    else:
        path = line[path_start:]
    line = line.split("/")[0] #remove first "/" and anything after 
    host = line
    if redirected == "true":
        connect(host, path, port, url, redirected = "true")
    elif refrenced == "true":
        imgconnect(host, path, port, url)
    else:
        connect(host, path, port, url)
#since images are not encoded with UTF-8 a different connect function is needed for refrenced image links
def imgconnect(host, path, port, url):
    sock = None
    try:
        sock = socket.create_connection((host, port), timeout=5)
    except Exception as e:
        print(f"URL: {url}")
        print("Status: Network Error")
    # send an HTTP GET request
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
    sock.send(request.encode())
    response = b''
    while True:
        data = sock.recv(1024)
        if not data:
            break
        response += data
    status = int(response.split(b' ')[1])
    print(f"Refrenced URL: {url}")
    statuscheck(status)
#This is the main connect function that sends the Get request, recieves the response, and parses the http header for the status code
def connect(hostm, pathm, portm, urlm, redirected = "false" ):
    sock = None
    # create client socket, connect to server
    try:
        sock = socket.create_connection((hostm, portm), timeout=5)
    except Exception as e:
        print(f"URL: {urlm}")
        print("Status: Network Error")
    else:
        if sock:
            status = ""
            # send http request
            request = f'GET {pathm} HTTP/1.0\r\n'
            request += f'Host: {hostm}\r\n'
            request += '\r\n'
            try:
                sock.send(bytes(request, 'utf-8'))
            except Exception as e:
                print(f"URL: {urlm}")
                print("Status: Network Error")
            else:
                response = sock.recv(1024).decode('utf-8').strip()
                sock.close()
                s = response
                index = -1
                for i in range(3):
                    index = s.find("\n", index + 1)
                    if index == -1:
                        break
                #get string on 3rd line
                if index != -1:
                    s = s[index + 1:]
                    if s.startswith('Content-Length: 0'):
                        print(f"URL: {urlm}")
                        print("Status: Network Error\n")
                        status = "Network Error"
                # print(response) #RESPONSE READER LINE
                if portm == "80" and status != "Network Error":
                    s1 = response
                    s1 = slice(9,12)
                    status = response[s1]
                    if redirected == "false":
                        print(f"URL: {urlm}")
                        statuscheck(status)
                    else: 
                        print(f"Redirected URL: {urlm}")
                        statuscheck(status)
                    imgcheck(response, hostm)
                    if status == "302" or status == "301":
                        redirect(response)
                    else:
                        print("\n")
                        
#This function parses any 302 or 301 redirects to find the new link
def redirect(responsem):
    index = -1
    for i in range(13):
        index = responsem.find("\n", index + 1)
        if index == -1:
            break
    # create a new string that starts at the index of the fourth "\n" character
    if index != -1:
        responsem = responsem[index + 1:]
        start_index = responsem.find('"')
        end_index = responsem.find('"', start_index + 1)
        # extract the characters within the double quotes
        if start_index != -1 and end_index != -1:
            url = responsem[start_index + 1:end_index]
            parse(url, redirected="true")
#This function checks if a header inlcludes a refrencded image
def imgcheck(responsei, host):
    index = -1
    for i in range(15):
        index = responsei.find("\n", index + 1)
        if index == -1:
            break
    if index != -1:
        responsei = responsei[index + 1:]
    if responsei.startswith("<img src="):
        start_index = responsei.find('"')
        end_index = responsei.find('"', start_index + 1)
        # extract the characters within the double quotes
        if start_index != -1 and end_index != -1:
            refurl = responsei[start_index + 1:end_index]
        if refurl.startswith("http"):
            parse(refurl)
        else:
            refurl = "http://" + host + refurl
            parse(refurl, refrenced = "true")
    else: 
        pass
#This function attaches the status message to its repsetive status code and prints
def statuscheck(status):
    if status == "200":
        print(f"Status: {status} OK")
    elif status == "404":
        print(f"Status: {status} Not Found")
    elif status == "301":
        print(f"Status: {status} Moved Permanently")
    elif status == "302":
        print(f"Status: {status} Moved Temporarily")
    elif status == "400":
        print(f"Status: {status} Bad Request")
    elif status == "404":
        print(f"Status: {status} Not Found")
    elif status == "403":
        print(f"Status: {status} Forbidden")
    else:
        print(f"Status: {status}")
#This loops through every line (url) within the specified file to perfom the above functions 
with open(urls_file, 'r') as file:
    for line in file:
        parse(line)
        


