#!/user/bin/python
# -*- coding: UTF-8 -*-

import os
import subprocess
import argparse
from lxml import etree as ET
from io import BytesIO
import time

class Util(object):
    @staticmethod
    def runshell(cmdline, outfile=None, env=None):
        out = subprocess.PIPE
        if outfile != None:
            out = outfile
        handle = subprocess.Popen(cmdline, stdout=out, stderr=out, stdin=subprocess.PIPE, shell=True, env=env)
        if outfile != None:
            return handle.wait(),""
        else:
            output,unused_err = handle.communicate()
            retcode = handle.poll()
            if retcode:
                print "%s error : %s" % (cmdline, unused_err)
            return retcode,output
            
def getalldir(svndir, layer):
    cmdline = 'svn ls "%s"' % svndir
    ret,output = Util.runshell(cmdline)
    if ret != 0:
        return ret
    lines = output.split("\r\n")
    for i in range(len(lines)):
        if layer == 0:
            print "%0.2f%%" % ((i + 1) * 100.0 / len(lines))
        line = lines[i]
        if len(line) == 0 or not line.endswith("/"):
            continue
        subdir = "%s%s" % (svndir, line)
        cmdline = 'svn update --depth=empty "%s"' % subdir
        ret,output = Util.runshell(cmdline)
        if ret != 0:
            return ret
        ret = getalldir(subdir, layer + 1)
        if ret != 0:
            return ret
    return 0

def getworkcopydir(rootdir, rooturl, url):
    return url.replace(rooturl, rootdir)
    
def run():
    parser = argparse.ArgumentParser(description='cmd options')
    parser.add_argument("target", help="address")
    parser.add_argument("-f", "--filter", help="filter")
    parser.add_argument("-e", "--exclude", help="exclude")
    parser.add_argument("-r", "--replace", help="replace")
    parser.add_argument("-v", "--revision", help="revision", default="HEAD")
    args = parser.parse_args()
    if args.replace and args.replace.find(":") < 0:
        print "replace must contains ':'"
        return
    try:
        rootdir = time.strftime('%Y%m%d%H%M%S', time.localtime())
        propfilename = "externals.txt"
        #step1:checkout dirs to local
        print("checkout dir ...")
        cmdline = "svn co --depth=empty -r %s %s %s" % (args.revision, args.target, rootdir)
        ret,output = Util.runshell(cmdline)
        if ret != 0:
            return
        #step2:get prop
        print "propget ..."
        cmdline = "svn -R --xml propget svn:externals %s@%s" % (args.target, args.revision)
        ret,output = Util.runshell(cmdline)
        if ret != 0:
            return
        tree = ET.fromstring(output)
        nodes = tree.findall(".//property[@name='svn:externals']")
        for node in nodes: 
            target = node.getparent().get("path")
            localdir = getworkcopydir(rootdir, args.target, target)
            if args.exclude and localdir.find(args.exclude) >= 0:
            	continue
            externals = node.text.split("\n")
            result = []
            found = False
            for i in range(len(externals)):
                external = externals[i]
                if len(external) == 0:
                    continue
                url,localpath = external.split(" ")
                if args.filter and url.find(args.filter) >= 0:
                    found = True
                result.append((url,localpath))
            if len(result) > 0 and (not args.filter or found):
                print "found %s : %s" % (target, result)
                #step3:replace  
                if args.replace:
                    newexternals = []
                    src,to = args.replace.split(":")
                    propfile = open(propfilename, "w")
                    for i in range(len(result)):
                        newexternals.append("%s %s\n" % (result[i][0].replace(src,to), result[i][1]))
                    propfile.writelines(newexternals)
                    propfile.close()
                    print "replace to new : %s" %  newexternals
                    cmdline = 'svn update --parents --depth=empty -r %s "%s"' % (args.revision, localdir)
                    ret,output = Util.runshell(cmdline)
                    if ret != 0:
                        return
                    cmdline = 'svn propset svn:externals "%s" -F %s' % (localdir, propfilename)
                    ret,output = Util.runshell(cmdline)
                    if ret != 0:
                        return                                                
    except Exception,e:
        print e 

if __name__ == "__main__":
    run()

