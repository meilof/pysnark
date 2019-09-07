# Copytight (C) Meilof Veeningen, 2019

from .runtime import ignore_errors, guard, is_base_value

def guarded(cond):
    def _guarded(fn):
        def __guarded(*args, **kwargs):
            global guard, ignore_errors
            
            _orig_guard = guard
            _orig_ignore_errors = ignore_errors
            guard = cond if _orig_guard is None else cond&_orig_guard
            ignore_errors = (cond.value==0)
            
            try:
                ret = fn(*args, **kwargs)
                guard = _orig_guard
                ignore_errors = _orig_ignore_errors
            except:
                guard = _orig_guard
                ignore_errors = _orig_ignore_errors
                raise
        
            return ret
        
        return __guarded
    return _guarded
    
def if_then_else(cond, truev, falsev):
    if is_base_value(cond):
        if cond!=0 and cond!=1: 
            raise ValueError("not a boolean value: " + str(cond))
        return trueval if cond else falseval
    
    if callable(truev): trueval = guarded(cond)(truev)()
    if callable(falsev): falseval = guarded(1-cond)(falsev)()        
 
    if (not ignore_errors) and cond.value!=0 and cond.value!=1:
        raise(ValueError("not a bit: " + str(cond)))
    
    return falsev+cond*(truev-falsev)
