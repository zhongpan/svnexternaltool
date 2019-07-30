# svnexternaltool
你是否遇到如下问题？
* svn中会建立一些外链，当进行分支时，有时需要对外链进行修改，手工修改会非常繁琐
* 时间长了之后，svn中有哪些外链可能会非常复杂，如何快速查找有哪些外链
本小工具就是用来解决上述问题。

# 实现原理
调用svn命令实现，具体参见源码。


# 用法
1. 查找某个svn路径上所有外链
```shell
python svnexternaltool.py https://svnpath
```

2. 查找某个svn路径的某个revision上所有外链
```shell
python svnexternaltool.py -v 12345 https://svnpath
```

3. 查找外链url满足条件的外链
```shell
python svnexternaltool.py -f xxxxx https://svnpath
```

4. 在上述基础上，排除某些svn路径
```shell
python svnexternaltool.py -f xxxxx -e yyyyy https://svnpath
```

5. 在上述基础上，将外链url中字符串进行替换
```shell
python svnexternaltool.py -f xxxxx -e yyyyy -r src:to https://svnpath
```
上述命令将满足条件的外链url中的字符串src替换为to，完成上述命令后在本地出现一个命令执行时间命名的目录，这是SVN本地副本，在其中执行commit即可。


