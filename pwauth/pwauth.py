#!/usr/bin/env python

import subprocess

PWAUTH_ERROR_CODES = {
	1: 'UNKNOWN',
	2: 'INVALID',
	3: 'BLOCKED',
	4: 'EXPIRED',
	5: 'PW_EXPIRED',
	6: 'NOLOGIN',
	7: 'MANYFAILES',
	50: 'INT_USER',
	51: 'INT_ARGS',
	52: 'INT_ERR',
	53: 'INT_NOROOT',
}

PWAUTH_SUCCESS_CODES = {
	0: 'OK',
}

def pwauth(username=None,password=None,pwauth_path='/usr/sbin/pwauth'):
	p = subprocess.Popen([pwauth_path,],
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
	)
	if p.poll() is None:
		p.communicate('%s\n%s\n' % (username,password))
	if p.poll() is None:
		# something is wrong, terminate process, return false
		p.terminate()
		return False
	if p.returncode in PWAUTH_SUCCESS_CODES.keys():
		return True
	return False

