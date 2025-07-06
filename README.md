# HttpServer(urls)
### params 
- urls(dict[str, function]) : A dictionary containing the funtions for each url
### methods
- send_file(request: HttpRequest, file_path) : Sends html file as response
- html_response(request: HttpRequest, text) : Sends string in text as html response


# HttpRequest
### params
- method = HttpMethod : HTTP method 
- url = "" : relative url
- headers = {} : request headers in lower case
- body = "" : raw body data
- form_data = {} : form data from post request if content type is `application/x-www-form-urlencoded`
- files: Dict[str, UploadedFile] = {} : uploaded files from post request, can be accessed with name value of form input tag
- address = None : client ip and port

