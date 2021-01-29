from flask import Flask, request, abort
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen

#https://sumesh-fsnd.jp.auth0.com/authorize?audience=image&response_type=token&client_id=koRHBc9CNgPbEvdI3rwi9nRhCHSFCKQ9&redirect_uri=https://localhost:8080/login-result
#toek = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IngzOThFR1RoWUQyUS1uYzRVRWxOcSJ9.eyJpc3MiOiJodHRwczovL3N1bWVzaC1mc25kLmpwLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExMTIwMzI2MTkyOTI1NjQxNjMzMyIsImF1ZCI6ImltYWdlIiwiaWF0IjoxNjExNzcwMzU1LCJleHAiOjE2MTE3Nzc1NTUsImF6cCI6ImtvUkhCYzlDTmdQYkV2ZEkzcndpOW5SaENIU0ZDS1E5Iiwic2NvcGUiOiIifQ.qGdVCDLy9kn6u7QVHFTQmtDNS6T5fHuTWIvbB8z8Wmc7kvcyoO2FwL03ncSmcrsCv6c49pg5RMbCsOKFJaDmlbViTGyACtjDJMqZa06zrswnZwnXnOcIhq93VzICAf_r-rnxSNaAcJJIDAcdLPw_Ev5-LupBtGy4NxQ3EUQAVI33aNgTyaQXbpS6aDvclCP8MMi2S7i1cBbj9Cm2URPMcwPhHkOwyGKn-NaBfx85tIuiYU8mV3pZK_yxg9uUBZ8pTDtr7bg-pjx0wYkMy7bg4ePFe1tmwjjpFcsVeLVRZ7lQO3mUyh8ON0VY9IC47iSEKhcWvglLoW40OC0JsmHZHw'
app = Flask(__name__)

AUTH0_DOMAIN = 'sumesh-fsnd.jp.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    print('get token')
    auth = request.headers.get('Authorization', None)
    print(auth)
    if not auth:
        print('auth key not found')
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        print('no bearer')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        print('token not found')
        raise AuthError({
            
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        print('token not found 2')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        print('kid not in')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    print('rsa key=',rsa_key)
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            print("payload",payload)
            return payload

        except jwt.ExpiredSignatureError:
            print('token expired')
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception as e:
            print('cannot parse header',e)
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)
def check_permissions(permission, payload):
    if 'permissions' not in payload:
                        raise AuthError({
                            'code': 'invalid_claims',
                            'description': 'Permissions not included in JWT.'
                        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True

def requires_auth(permission=''):
    def requires_auth_wrapper(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print('wrapper')
            token = get_token_auth_header()
            print('token=',token)
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            
            check_permissions(permission,payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_wrapper

@app.route('/images')
@requires_auth('read:images')
def headers(payload):
    print(payload)
    return 'Access Granted'