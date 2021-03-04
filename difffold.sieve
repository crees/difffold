# This is not tested-- please ensure it works with test emails
# to avoid email loss
require ["vnd.dovecot.pipe", "copy", "imapsieve", "environment", "variables"];

if exists "list-id" {
	if header :regex "list-id" "<doc-committers.freebsd.org>" {
		filter "/usr/bin/env/python /usr/local/share/difffold/difffold.py";
	}
}
