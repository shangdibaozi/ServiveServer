import json

from KBEDebug import DEBUG_MSG
from urllib.parse import unquote, quote

STATUS_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
}

class Request:
    def __init__(self, r):
        self.content = r
        self.method = r.split()[0]
        self.path = r.split()[1]
        self.body = r.split('\r\n\r\n', 1)[1]
        self.jsondata = self._parseData()
        DEBUG_MSG("Request: content=%s" % (self.content))
        DEBUG_MSG("Request: method=%s" % (self.method))
        DEBUG_MSG("Request: path=%s" % (self.path))
        DEBUG_MSG("Request: body=%s" % (self.body))
        DEBUG_MSG("Request: jsondata=%s" % (self.jsondata))
        
    def from_body(self):
        return self._parse_parameter(self.body)

    def parse_path(self):
        index = self.path.find('?')
        if index == -1:
            return self.path, {}
        else:
            path, query_string = self.path.split('?', 1)
            query = self._parse_parameter(query_string)
            return path, query

    @property
    def headers(self):
        header_content = self.content.split('\r\n\r\n', 1)[0].split('\r\n')[1:]
        result = {}
        for line in header_content:
            k, v = line.split(': ')
            result[quote(k)] = quote(v)
        return result

    @staticmethod
    def _parse_parameter(parameters):
        args = parameters.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = unquote(v)

        return query

    def _parseData(self):
        if len(self.body) != 0:
            index0 = self.body.find("{")
            index1 = self.body.rfind("}")
            if index0 != -1 and index1 != -1:
                return self.body[index0:(index1 + 1)]
        return ""

    def getResponse(self, status):
        data = {}
        if status != 400:
            if len(self.jsondata) != 0:
                data['data'] = json.loads(self.jsondata)
                data['error'] = 0
            else:
                data['error'] = 0
                data['data'] = {}
        else:
            data['error'] = 1
            data['message'] = "数据处理失败"
        content = json.dumps(data)

        response = 'HTTP/1.1 %d %s\r\n' % (status, STATUS_CODES.get(status, "UNKNOWN RESPONSE"))
        response += 'Content-Type: application/json\r\n'
        response += 'Content-Length: %d\r\n' % len(content)
        response += '\r\n'
        response += content
        return response
