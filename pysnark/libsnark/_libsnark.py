import distutils.sysconfig
import sys

def __bootstrap__():
    global __bootstrap__, __loader__, __file__
    import sys, pkg_resources, imp
    ext_suffix_var = 'SO'
    if sys.version_info[:2] >= (3, 5):
        ext_suffix_var = 'EXT_SUFFIX'
    libname = '_libsnark' + distutils.sysconfig.get_config_var(ext_suffix_var)
    __file__ = pkg_resources.resource_filename(__name__, libname)
    __loader__ = None; del __bootstrap__, __loader__
    imp.load_dynamic("_libsnark",__file__)
__bootstrap__()
