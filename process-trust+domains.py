#!/usr/bin/env python3

## this script process trust+ domain blacklist file into configuration files for unbound
## TODO: multithreading, checking if unbound is installed, erase temporary file
import sys, subprocess, shlex, tempfile, os
import tldextract
import ipaddress
ip_addrs = []
unique_domains = []
subdomain_groups = {}
if len(sys.argv) == 1:
    sys.stderr.write("usage: {} domains-file output-conf-dir\n".format(sys.argv[0]))
    exit(1)
if not os.path.isfile(os.path.realpath(sys.argv[1])):
    sys.stderr.write("input file doesn't exists\n")
    exit(1)
if not os.path.isdir(os.path.realpath(sys.argv[2])):
    sys.stderr.write("output conf dir doesn't exists. creating it\n")
    os.mkdir(os.path.realpath(sys.argv[2])
cmdline = shlex.split("sed -e '/^\*\./d' {} ".format(sys.argv[1]))
cmdout = tempfile.mkstemp()
cmd0 = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
cmd1 = subprocess.Popen(["sort"], stdin=cmd0.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
cmd2 = subprocess.Popen(["uniq"], stdin=cmd1.stdout, stdout=cmdout[0], stderr=subprocess.STDOUT)
cmd0.wait()
cmd1.wait()
cmd2.wait()

with open(cmdout[1], 'r') as infile:
    progres = []
    for line in infile:
        #if line.startswith('*.'):
        #    continue
        line = line.strip()
        p = line[0]
        if p not in progres:
            print(p)
            progres.append(p)
        try:
            ipaddress.ip_address(line)
            ip_addrs.append(line)
            continue
        except ValueError:
            pass
        line_dom = tldextract.extract(line)
        if line_dom.registered_domain not in unique_domains and \
           line_dom.registered_domain not in subdomain_groups.keys():
            unique_domains.append(line_dom.registered_domain)
            #print(line_dom.registered_domain + " unique")
        else:
            if line_dom.registered_domain in unique_domains:
                unique_domains.remove(line_dom.registered_domain)
            #    print("create dom grp", line_dom.registered_domain)
                subdomain_groups[line_dom.registered_domain] = []
            subdomain_groups[line_dom.registered_domain].append(line)
            #print("add to grp", line)
os.remove(cmdout[1])
g = open(os.path.join(os.path.realpath(sys.argv[2]), "unique_domains.conf"))
for d in unique_domains:
    g.write('local-zone: "' + d + '" redirect\n')
    g.write('local-data: "' + d + ' IN A ' + redir_ip + '"\n')

for k in subdomain_groups.keys():
    h = open(k + '.conf','w')
    h.write('local-zone: "' + k + '" transparent\n')
    for d in subdoms[k]:
        h.write('local-data: "' + d + ' IN A ' + redir_ip + '"\n')
    h.close()
_ = [print(d) for d in unique_domains]
_ = [print(d) for d in ip_addrs]
for k,v in subdomain_groups:
    print("{} subdoms:")
    for e in v:
        print(e)
