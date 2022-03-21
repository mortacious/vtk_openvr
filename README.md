# VTK OpenVR

Build VTK's [Rendering/OpenVR](https://github.com/Kitware/VTK/tree/master/Rendering/OpenVR) 
module as a standalone installable library with optional python bindings.

Due to relying on the VTK module build system, this library requires VTK 9.0 or above.

# Installation

### From source (Python)

```bash
git clone https://github.com/mortacious/vtk-openvr.git
cd vtk-openvr
python setup.py install
```


### From source (C++)
```bash
git clone https://github.com/mortacious/vtk-openvr.git
cd vtk-openvr
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make && sudo make install
```

## Usage

### Linux

An Application using this library must be launched with the steam runtime enabled if `STEAM_RUNTIME=1`, e.g.:

```bash
~/.steam/steam/ubuntu12_64/steam-runtime/run.sh ./<application>
```

or

```bash
~/.steam/steam/ubuntu12_64/steam-runtime/run.sh python <application>
```

### Windows 

¯\_(ツ)_/¯


## Acknowlegements

This library provides the vtkRenderingOpenVR module of the VTK library as a standalone (python) package. VTK
is available under the following license:

Program:   Visualization Toolkit
Module:    Copyright.txt

Copyright (c) 1993-2015 Ken Martin, Will Schroeder, Bill Lorensen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither name of Ken Martin, Will Schroeder, or Bill Lorensen nor the names
  of any contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.