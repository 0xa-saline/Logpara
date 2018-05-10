#!/usr/bin/env python
# from slqmap
try:
    import cPickle as pickle
except:
    import pickle
finally:
    import pickle as picklePy
import urllib
import base64
import json
import re
import StringIO
import sys
import subprocess

# System variables
IS_WIN = subprocess.mswindows
# Encoding used for Unicode data
UNICODE_ENCODING = "utf8"

# Chars which can be used as a failsafe values in case of too long URL encoding value
URLENCODE_FAILSAFE_CHARS = '()|,'

# Table used for Base64 conversion in WordPress hash cracking routine

class PLACE:
    GET = "GET"
    POST = "POST"
    URI = "URI"
    COOKIE = "Cookie"
    USER_AGENT = "User-Agent"
    REFERER = "Referer"
    HOST = "Host"
    CUSTOM_POST = "(custom) POST"
    CUSTOM_HEADER = "(custom) HEADER"

def base64decode(value):
    """
    Decodes string value from Base64 to plain format

    >>> base64decode('Zm9vYmFy')
    'foobar'
    """

    return base64.b64decode(value)

def base64encode(value):
    """
    Encodes string value from plain to Base64 format

    >>> base64encode('foobar')
    'Zm9vYmFy'
    """

    return base64.b64encode(value)

def base64pickle(value):
    """
    Serializes (with pickle) and encodes to Base64 format supplied (binary) value

    >>> base64pickle('foobar')
    'gAJVBmZvb2JhcnEBLg=='
    """

    retVal = None

    try:
        retVal = base64encode(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
    except:
        warnMsg = "problem occurred while serializing "
        warnMsg += "instance of a type '%s'" % type(value)
        singleTimeWarnMessage(warnMsg)

        try:
            retVal = base64encode(pickle.dumps(value))
        except:
            retVal = base64encode(pickle.dumps(str(value), pickle.HIGHEST_PROTOCOL))

    return retVal

def base64unpickle(value, unsafe=False):
    """
    Decodes value from Base64 to plain format and deserializes (with pickle) its content

    >>> base64unpickle('gAJVBmZvb2JhcnEBLg==')
    'foobar'
    """

    retVal = None

    def _(self):
        if len(self.stack) > 1:
            func = self.stack[-2]
            if func not in PICKLE_REDUCE_WHITELIST:
                raise Exception, "abusing reduce() is bad, Mkay!"
        self.load_reduce()

    def loads(str):
        f = StringIO.StringIO(str)
        if unsafe:
            unpickler = picklePy.Unpickler(f)
            unpickler.dispatch[picklePy.REDUCE] = _
        else:
            unpickler = pickle.Unpickler(f)
        return unpickler.load()

    try:
        retVal = loads(base64decode(value))
    except TypeError: 
        retVal = loads(base64decode(bytes(value)))

    return retVal

def hexdecode(value):
    """
    Decodes string value from hex to plain format

    >>> hexdecode('666f6f626172')
    'foobar'
    """

    value = value.lower()
    return (value[2:] if value.startswith("0x") else value).decode("hex")

def hexencode(value):
    """
    Encodes string value from plain to hex format

    >>> hexencode('foobar')
    '666f6f626172'
    """

    return utf8encode(value).encode("hex")

def unicodeencode(value, encoding=None):
    """
    Returns 8-bit string representation of the supplied unicode value

    >>> unicodeencode(u'foobar')
    'foobar'
    """

    retVal = value
    if isinstance(value, unicode):
        try:
            retVal = value.encode(encoding or UNICODE_ENCODING)
        except UnicodeEncodeError:
            retVal = value.encode(UNICODE_ENCODING, "replace")
    return retVal


def unicode_encode(value, encoding=None):
    """
    Return 8-bit string representation of the supplied unicode value:

    >>> unicode_encode(u'test')
    'test'
    """

    ret_val = value
    if isinstance(value, unicode):
        try:
            ret_val = value.encode(encoding or UNICODE_ENCODING)
        except UnicodeEncodeError:
            ret_val = value.encode(UNICODE_ENCODING, "replace")
    return ret_val


def utf8encode(value):
    return unicode_encode(value, "utf-8")


def utf8decode(value):
    """
    Returns UTF-8 representation of the supplied 8-bit string representation

    >>> utf8decode('foobar')
    u'foobar'
    """

    return value.decode("utf-8")


def urldecode(value, encoding=None):
    """
    URL decodes given value
    >>> urldecode('AND%201%3E%282%2B3%29%23', convall=True)
    u'AND 1>(2+3)#'
    """
    result = None

    if value:
        try:
            # for cases like T%C3%BCrk%C3%A7e
            value = str(value)
        except ValueError:
            pass
        finally:
            result = urllib.unquote_plus(value)

    if isinstance(result, str):
        result = unicode(result, encoding or UNICODE_ENCODING, errors="replace")

    return result


def urlencode(value, safe="%&=", convall=False, limit=False):
    """
    URL encodes given value
    >>> urlencode('AND 1>(2+3)#')
    'AND%201%3E%282%2B3%29%23'
    """
    count = 0
    result = None

    if value is None:
        return result

    if convall or safe is None:
        safe = ""

    # corner case when character % really needs to be
    # encoded (when not representing url encoded char)
    if all(map(lambda x: '%' in x, [safe, value])):
        value = re.sub("%(?![0-9a-fA-F]{2})", "%25", value, re.DOTALL | re.IGNORECASE)

    while True:
        result = urllib.quote(utf8_encode(value), safe)

        if limit and len(result) > URLENCODE_CHAR_LIMIT:
            if count >= len(URLENCODE_FAILSAFE_CHARS):
                break

            while count < len(URLENCODE_FAILSAFE_CHARS):
                safe += URLENCODE_FAILSAFE_CHARS[count]
                count += 1
                if safe[-1] in value:
                    break
        else:
            break

    return result

def htmlunescape(value):
    """
    Returns (basic conversion) HTML unescaped value

    >>> htmlunescape('a&lt;b')
    'a<b'
    """

    retVal = value
    if value and isinstance(value, basestring):
        codes = (('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&nbsp;', ' '), ('&amp;', '&'))
        retVal = reduce(lambda x, y: x.replace(y[0], y[1]), codes, retVal)
        try:
            retVal = re.sub(r"&#x([^ ;]+);", lambda match: unichr(int(match.group(1), 16)), retVal)
        except ValueError:
            pass
    return retVal

def singleTimeWarnMessage(message):  # Cross-linked function
    sys.stdout.write(message)
    sys.stdout.write("\n")
    sys.stdout.flush()

def stdoutencode(data):
    retVal = None

    try:
        data = data or ""

        # Reference: http://bugs.python.org/issue1602
        if IS_WIN:
            output = data.encode(sys.stdout.encoding, "replace")

            if '?' in output and '?' not in data:
                warnMsg = "cannot properly display Unicode characters "
                warnMsg += "inside Windows OS command prompt "
                warnMsg += "(http://bugs.python.org/issue1602). All "
                warnMsg += "unhandled occurances will result in "
                warnMsg += "replacement with '?' character. Please, find "
                warnMsg += "proper character representation inside "
                warnMsg += "corresponding output files. "
                singleTimeWarnMessage(warnMsg)

            retVal = output
        else:
            retVal = data.encode(sys.stdout.encoding)
    except:
        retVal = data.encode(UNICODE_ENCODING) if isinstance(data, unicode) else data

    return retVal

def jsonize(data):
    """
    Returns JSON serialized data

    >>> jsonize({'foo':'bar'})
    '{\\n    "foo": "bar"\\n}'
    """

    return json.dumps(data, sort_keys=False, indent=4)

def dejsonize(data):
    """
    Returns JSON deserialized data

    >>> dejsonize('{\\n    "foo": "bar"\\n}')
    {u'foo': u'bar'}
    """

    return json.loads(data)


def to_param_dict(params):
    """a=1&b=2 to {'a':1,'b':2}"""
    param_dict = {}
    if not params:
        return param_dict
    try:
        split_params = params.split('&')
        for element in split_params:
            elem = element.split("=")
            if len(elem) >= 2:
                parameter = elem[0].replace(" ", "")
                value = "=".join(elem[1:])
                param_dict[parameter] = value
    except:
        pass

    return param_dict

def to_param_str(param_dict):
    """{'a':1,'b':2} to a=1&b=2"""
    params = '&'.join([k + '=' + v for k, v in param_dict.items()])
    return params

if __name__ == '__main__':
    url = '&lt;?xml&nbsp;version=&quot;1.0&quot;&nbsp;encoding=&quot;UTF-8&quot;?&gt;&lt;collection&gt;&lt;element&nbsp;ID=&quot;UserName&quot;&nbsp;Type=&quot;String&quot;&gt;&lt;![CDATA[test]]&gt;&lt;/element&gt;&lt;element&nbsp;ID=&quot;Password&quot;&nbsp;Type=&quot;String&quot;&gt;&lt;![CDATA[1234]]&gt;&lt;/element&gt;&lt;element&nbsp;ID=&quot;VerifyCode&quot;&nbsp;Type=&quot;String&quot;&gt;&lt;![CDATA[3kv3]]&gt;&lt;/element&gt;&lt;element&nbsp;ID=&quot;LoginImg&quot;&nbsp;Type=&quot;String&quot;&gt;&lt;![CDATA[]]&gt;&lt;/element&gt;&lt;element&nbsp;ID=&quot;Cancel&quot;&nbsp;Type=&quot;String&quot;&gt;&lt;![CDATA[]]&gt;&lt;/element&gt;&lt;/collection&gt;'
    print htmlunescape(url)