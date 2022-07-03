###############################################################################
# Copyright cocotb contributors
# Licensed under the Revised BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-3-Clause
###############################################################################

import os
import importlib
import re
from cocotb.decorators import bfm_param_int_t

import_info_l = []
export_info_l = []


# 用于注册bfm
def register_bfm_type(T, hdl):
    # print('register_bfm_type')
    global import_info_l
    global export_info_l
    # BfmTypeInfo：里面包含了T——具体的BFM类，hdl——HDL文件和路径，import_info——需要被导入的方法列表，export_info——需要被导出的方法列表
    type_info = BfmTypeInfo(T, hdl, import_info_l.copy(), export_info_l.copy())
    # 通过bfm管理器实例给具体的bfm类添加对应的bfm类型信息
    BfmMgr.inst().add_type_info(T, type_info)
    import_info_l = []
    export_info_l = []


# 用于将被装饰的方法放进全局列表中，方法的id设为当前列表长度; info: BfmMethodInfo
def register_bfm_import_info(info):
    # print('register_bfm_import_info')
    info.id = len(import_info_l)
    import_info_l.append(info)


# 用于将被装饰的方法放进全局列表中，方法的id设为当前列表长度; info: BfmMethodInfo
def register_bfm_export_info(info):
    # print('register_bfm_export_info')
    info.id = len(export_info_l)
    export_info_l.append(info)

def bfm_hdl_path(py_file, template):
    return os.path.join(
        os.path.dirname(os.path.abspath(py_file)),
        template)


# BfmMethodParamInfo：用于描述单个数据类型的信息，包括参数名和参数类型
class BfmMethodParamInfo:
    '''
    Information about a single BFM-method parameter
    '''

    def __init__(self, pname, ptype):
        self.pname = pname
        self.ptype = ptype


# BfmMethodInfo：用于描述某BFM的方法信息，包括方法类型、参数类型
class BfmMethodInfo:
    '''
    Information about a single BFM method
    - Method type
    - User-specified parameter signature
    '''

    def __init__(self, T, signature):
        fullname = T.__qualname__
        fi = T.__code__

        self.T = T
        self.signature = []
        self.type_info = []
        self.id = -1

        locals_idx = fullname.find("<locals>")
        if locals_idx != -1:
            fullname = fullname[locals_idx+len("<locals>."):]

        if fullname.find('.') == -1:
            raise Exception("Attempting to register a global method as a BFM method")

        args = fi.co_varnames[1:fi.co_argcount]
        if len(signature) != len(args):
            raise Exception("Wrong number of parameter-type elements: expect " + str(len(args)) + " but received " + str(len(signature)))

        for a,t in zip(args, signature):
            # BfmMethodParamInfo：用于描述单个数据类型的信息，包括参数名和参数类型
            self.signature.append(BfmMethodParamInfo(a, t))
            try:
                import simulator
            except Exception:
                # When we're not running in simulation, don't
                # worry about being able to access constants from simulation
                self.type_info.append(None)
            else:
                if isinstance(t, bfm_param_int_t):
                    if t.s:
                        self.type_info.append(simulator.BFM_SI_PARAM)
                    else:
                        self.type_info.append(simulator.BFM_UI_PARAM)


# BfmTypeInfo：里面包含了T——具体的BFM类，hdl——HDL文件和路径，import_info——需要被导入的方法列表，export_info——需要被导出的方法列表
class BfmTypeInfo:
    def __init__(self, T, hdl, import_info, export_info):
        self.T = T
        self.hdl = hdl
        self.import_info = import_info
        self.export_info = export_info


# bfm的信息
class BfmInfo:
    def __init__(self, bfm, id, inst_name, type_info):
        self.bfm = bfm
        self.id = id
        self.inst_name = inst_name
        self.type_info = type_info

    def call_method(self, method_id, params):
        self.type_info.export_info[method_id].T(
            self.bfm, *params)


# bfm管理器
# BFM管理器BfmMgr,它被放在__init__.py的177行进行初始化，初始化时将verilog中注册的所有bfm都放进管理器
class BfmMgr:
    # bfm管理器实例
    _inst = None

    def __init__(self):
        # 列表-存放bfm实例, 如: <spi_bfms.spi_initiator_bfm.SpiInitiatorBfm object at 0x7f7dac40f430>
        self.bfm_l = []
        # 字典-具体的bfm类和其对应的bfm类型信息
        self.bfm_type_info_m = {}
        self.m_initialized = False

    # 给具体的bfm类添加对应的bfm类型信息
    def add_type_info(self, T, type_info):
        # print('add_type_info')
        self.bfm_type_info_m[T] = type_info

    @staticmethod
    def get_bfms():
        return BfmMgr.inst().bfm_l

    @staticmethod
    def find_bfm(path_pattern):
        # bfm管理器实例
        inst = BfmMgr.inst()
        bfm = None
        # 编译正则表达式，生成一个 Pattern 对象       ".*u_bfm"
        path_pattern_re = re.compile(path_pattern)

        # Find the BFM instance that matches the specified pattern
        matches = (
            b
            for b in inst.bfm_l
            if path_pattern_re.match(b.bfm_info.inst_name)
            # b: <spi_bfms.spi_initiator_bfm.SpiInitiatorBfm object at 0x7f05b933a430>
            # b.bfm_info: <cocotb.bfms.BfmInfo object at 0x7f05b8a63d30>
            # b.bfm_info.inst_name: spi_initiator_smoke_tb.u_bfm
        )
        return next(matches, None)

    @staticmethod
    def inst():
        if BfmMgr._inst is None:
            BfmMgr._inst = BfmMgr()

        return BfmMgr._inst

    # 将verilog中注册的所有bfm都放进管理器       bfm_l列表
    def load_bfms(self):
        # print('load_bfms')
        '''
        Obtain the list of BFMs from the native layer
        '''
        import simulator
        # 注册到Cocotb的BFM数量
        n_bfms = simulator.bfm_get_count()
        for i in range(n_bfms):
            # info: ('spi_initiator_smoke_tb.u_bfm', 'spi_bfms.spi_initiator_bfm.SpiInitiatorBfm')
            # 返回特定BFM的信息,包括实例名和类名
            info = simulator.bfm_get_info(i)
            # instname: 'spi_initiator_smoke_tb.u_bfm'
            instname = info[0]
            # clsname: 'spi_bfms.spi_initiator_bfm.SpiInitiatorBfm'
            clsname = info[1]
            try:
                # pkgname: 'spi_bfms.spi_initiator_bfm'
                # clsleaf: 'SpiInitiatorBfm'
                pkgname, clsleaf = clsname.rsplit('.', 1)

            except ValueError:
                raise Exception("Incorrectly-formatted BFM class name {!r}".format(clsname))

            try:
                # 动态导入模块--导入spi_bfms.spi_initiator_bfm模块
                pkg = importlib.import_module(pkgname)
            except Exception:
                raise Exception("Failed to import BFM package {!r}".format(pkgname))

            if not hasattr(pkg, clsleaf):
                raise Exception("Failed to find BFM class \"" + clsleaf + "\" in package \"" + pkgname + "\"")

            # pkg: spi_bfms.spi_initiator_bfm模块
            # clsleaf: 'SpiInitiatorBfm'
            # bfmcls:	 <class 'spi_bfms.spi_initiator_bfm.SpiInitiatorBfm'>
            bfmcls = getattr(pkg, clsleaf)
            # type_info:	 <cocotb.bfms.BfmTypeInfo object at 0x7f4c557d4280>
            type_info = self.bfm_type_info_m[bfmcls]
            # SpiInitiatorBfm类对象    # __call__()注册bfm
            bfm = bfmcls()
            # BfmInfo: BFM信息
            bfm_info = BfmInfo(
                bfm,
                len(self.bfm_l),    # bfm编号
                instname,
                type_info)
            # Add       用于设置 bfm_info属性值，该属性不一定是存在的
            setattr(bfm, "bfm_info", bfm_info)
            # 存入bfm对象列表
            self.bfm_l.append(bfm)

    # BFM管理器BfmMgr, 它被放在__init__.py的177行进行初始化，初始化时将verilog中注册的所有bfm都放进管理器
    @staticmethod
    def init():
        import simulator
        # bfm管理器实例
        inst = BfmMgr.inst()
        if not inst.m_initialized:
            simulator.bfm_set_call_method(BfmMgr.call)
            # 将verilog中注册的所有bfm都放进管理器
            BfmMgr.inst().load_bfms()
            inst.m_initialized = True

    @staticmethod
    def call(
            bfm_id,
            method_id,
            params):
        inst = BfmMgr.inst()
        bfm = inst.bfm_l[bfm_id]

        if not hasattr(bfm, "bfm_info"):
            raise AttributeError("BFM object does not contain 'bfm_info' field")

        bfm.bfm_info.call_method(method_id, params)
