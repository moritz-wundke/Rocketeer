# Rocketeer
Welcome Rocketeer, a simple script to build your Unreal Engine 4 Rocket distros!

Usage: `rocketeer.[ps1|sh] root [Options] [Target Platforms]`
 - `root`: path to engine root, if noting set we will use the engine this script is in

Options:
 - `-BuildDDC`: Build a full DDC, this may take quite some time
 - `-SignExecutables`: Sign all build executebales
 - `-EnableSymStore`: Enable debug symbols
 - `-Clean`: Make a rebuild cleaning any previous stuff
 - `-Zip`: Zip the final build
 - `-MakeDistro`: Create an installed engine build
 - `-Build`: Build the engine solution first, if -Clean is specified we will rebuild the solution 

Target Platforms:
 - `-HostPlatformOnly`: Only build for the current OS
 - `-Win64`: Build with Win64 support
 - `-Win32`: Build with Win32 support
 - `-Mac`: Build with Mac support
 - `-Android`: Build with Android support
 - `-IOS`: Build with IOS support
 - `-TVO`: Build with TVO support
 - `-Linux`: Build with Linux support
 - `-HTML5`: Build with HTML5 support
 - `-Switch`: Build with Switch support
 - `-PS4`: Build with PS4 support
 - `-XboxOne`: Build with XboxOne support
 - `-AllTargets`: Will build with support for all targets
