import vtkmodules
version = tuple(int(s) for s in vtkmodules.__version__.split('.'))

try:
    if version[1] > 0:
        from vtkmodules.vtkRenderingVR import *
    from vtkmodules.vtkRenderOpenVR import *
except ImportError:
    if version[1] > 0:
        from .vtkRenderingVR import *
    from .vtkRenderingOpenVR import *