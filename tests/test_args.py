import argparse
parser = argparse.ArgumentParser(prog="cocotb-bfmgen")

# 使用add_subparsers()方法去创建子命令
subparser = parser.add_subparsers()
# 【required】 - 此命令行选项是否可省略 （仅选项可用）。
subparser.required = True
# 【dest】 - 被添加到 parse_args() 所返回对象上的属性名。
subparser.dest = 'command'

generate_cmd = subparser.add_parser("generate")
# set_defaults() 允许添加一些在不检查命令行的情况下确定的附加属性, 可以将子命令绑定特定的函数

# 向该对象中添加你要关注的命令行参数和选项
# 以'-'（默认）开头的参数为可选参数
# 【name or flags】 - 一个命名或者一个选项字符串的列表，例如 foo 或 -f, --foo。
# 【action】 - 当参数在命令行中出现时使用的动作基本类型, 定义了ArgumentParser对象实例如何对传入的参数进行“理解”
#        append：将值保存到一个列表中，如果参数重复则保存多个值
# 【default】 - 当参数未在命令行中出现并且也不存在于命名空间对象时所产生的值。
generate_cmd.add_argument("-m", action='append')
generate_cmd.add_argument("-l", "--language", default="vlog")
generate_cmd.add_argument("-o", default=None)

parser.parse_args('generate -m 13'.split(' '))
args = parser.parse_args('generate -m 16'.split(' '))
# 执行函数功能
# args.func(args)
print(args.m)

