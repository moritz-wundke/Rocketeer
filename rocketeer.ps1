Param(
	[string]$root = $null,
	[string]$output = $null,

	# Build options
	[Switch]$BuildDDC,
	[Switch]$SignExecutables,
	[Switch]$EnableSymStore,
	[Switch]$Clean,
	[Switch]$Zip,
	[Switch]$MakeDistro,
	[Switch]$Build,

	# Sync options
	[Switch]$NoPDBs,

	# Target platforms
	[Switch]$HostPlatformOnly,
	[Switch]$Win64,
	[Switch]$Win32,
	[Switch]$Mac,
	[Switch]$Android,
	[Switch]$IOS,
	[Switch]$TVOS,
	[Switch]$Linux,
	[Switch]$HTML5,
	[Switch]$Switch,
	[Switch]$PS4,
	[Switch]$XboxOno,
	[Switch]$AllTargets,

	# Misc
	[Switch]$help
)

$currentPwd = $pwd.Path
try
{


function WriteMessage($message, $color)
{
	foreach ($line in $message)
	{
	    write-host $line -foreground $color
	}
}

function WriteHeader($message)
{
	WriteMessage '=============================================================' 'magenta'
	WriteMessage $message 'magenta'
	WriteMessage '=============================================================' 'magenta'
}

function WriteInfo($message)
{
	WriteMessage $message 'darkyellow'
}

function WriteError($message)
{
	WriteMessage $message 'red'
}

function Die($message, $exitCode = 1)
{
	WriteError '============================================================='
	WriteError ('[Failed] {0}' -f $message) 
	WriteError '============================================================='
	Exit $exitCode
}

function exitIfFailed($message)
{
	if($lastexitcode -ne 0)
	{
		Die $message lastexitcode
	}
	else
	{
		WriteMessage '=============================================================' 'green'
		WriteMessage ('[Success] {0}' -f $message)  'green'
		WriteMessage '=============================================================' 'green'
	}
}

function execute($command, $params = " ")
{
	$tempLog = [System.IO.Path]::GetTempFileName()
	$stdOutLog = [System.IO.Path]::GetTempFileName()
	$stdErrLog = [System.IO.Path]::GetTempFileName()

	WriteMessage ('Executing: {0} [{1}], stdout:{2}' -f $command,$params,$stdOutLog) 'Yellow'

	$p = start-process ('.\{0}' -f $command) -windowstyle Hidden -ArgumentList $params -Wait -RedirectStandardOutput $stdOutLog -RedirectStandardError $stdErrLog
	$exitCode = $lastexitcode
	$stdOut = Get-Content $stdOutLog
	$stdErr = Get-Content $stdErrLog

	$outPut = New-Object PSObject	
	$outPut | add-member -type NoteProperty -Name stdOut -Value $stdOut
  	$outPut | add-member -type NoteProperty -Name stdErr -Value $stdErr
  	$outPut | add-member -type NoteProperty -Name exitCode -Value $exitCode

  	$lastexitcode = $exitCode
	return $outPut
}

function copyMatching($source, $target, $match)
{
	Get-ChildItem $source -Recurse -Include $match | Foreach-Object {
        $destDir = Split-Path ($_.FullName -Replace [regex]::Escape($source), $target)
        if (!(Test-Path $destDir))
        {
            New-Item -ItemType directory $destDir | Out-Null
        }
        Copy-Item $_ -Destination $destDir
    }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip($zip, $destination)
{	
	[System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $destination)
}
function Zip($source, $zip)
{
	[System.IO.Compression.ZipFile]::CreateFromDirectory($source, $zip, [System.IO.Compression.CompressionLevel]::Fastest, $false)
}

function SetFlag($value, $name)
{
	if ($value)
	{
		return (" -set:{0}=true" -f $name)
	}
	return (" -set:{0}=false" -f $name)
}

$helpMessage = 
@"
================================================================================
Welcome Rocketeer, a simple script to build your Unreal Engine 4 Rocket distros!
================================================================================

Usage: rocketeer.ps1 -root -output [Options] [Target Platforms]

 root: path to engine root, if noting set we will use the engine this script is in
 output: path to the destination directory to publish the build too (network locations suported)

Options:
 -BuildDDC: Build a full DDC, this may take quite some time
 -SignExecutables: Sign all build executebales
 -EnableSymStore: Enable debug symbols
 -Clean: Make a rebuild cleaning any previous stuff
 -Zip: Zip the final build
 -MakeDistro: Create an installed engine build
 -Build: Build the engine solution first, if -Clean is specified we will rebuild the solution
 -NoPDBs: Do not sync pdb files

Target Platforms:
 -HostPlatformOnly: Only build for the current OS
 -Win64: Build with Win64 support
 -Win32: Build with Win32 support
 -Mac: Build with Mac support
 -Android: Build with Android support
 -IOS: Build with IOS support
 -TVOS: Build with TVOS support
 -Linux: Build with Linux support
 -HTML5: Build with HTML5 support
 -Switch: Build with Switch support
 -PS4: Build with PS4 support
 -XboxOne: Build with XboxOne support
 -AllTargets: Will build with support for all targets
"@

if ($help -or $psboundparameters.count -eq 0)
{
	WriteInfo $helpMessage
	Exit
}

#
# Find AutomationTool
#

echo $root
echo $output

if ($root -eq "" -and $root -eq [String]::Empty)
{
	$root = [System.IO.Path]::GetFullPath((Join-Path ($currentPwd) ..\))
}

$automationTool = [System.IO.Path]::GetFullPath(('{0}\Engine\Binaries\DotNET\AutomationTool.exe' -f $root, $sdk))
if (-not (Test-Path $automationTool))
{
	WriteInfo $helpMessage
	Die ("Automation tool not found at: {0}" -f $automationTool)
}

#
# Build the whole thing
#

if ($Build)
{
	WriteError "Sorry but building the engine and all before is still a TODO!"
}

#
# Make the distro
#

if ($MakeDistro)
{

	$commandline = 'BuildGraph -target="Make Installed Build Win64" -script="Engine/Build/InstalledEngineBuild.xml"'

	#
	# Choose platforms
	#

	if ($AllTargets)
	{
		$commandline += (SetFlag true "WithWin64")
		$commandline += (SetFlag true "WithWin32")
		$commandline += (SetFlag true "WithMac")
		$commandline += (SetFlag true "WithAndroid")
		$commandline += (SetFlag true "WithIOS")
		$commandline += (SetFlag true "WithTVOS")
		$commandline += (SetFlag true "WithLinux")
		$commandline += (SetFlag true "WithHTML5")
		$commandline += (SetFlag true "WithSwitch")
		$commandline += (SetFlag true "WithPS4")
		$commandline += (SetFlag true "WithXboxOne")
	}
	elseif ($HostPlatformOnly)
	{
		$commandline += (SetFlag $HostPlatformOnly "HostPlatformOnly")
	}
	elseif ($HostPlatformOnly -or $Win64 -or $Win32 -or $Mac -or $Android -or $IOS -or $TVOS -or $Linux -or $HTML5 -or $Switch -or $PS4 -or $XboxOne)
	{
		$commandline += (SetFlag $Win64 	"WithWin64")
		$commandline += (SetFlag $Win32 	"WithWin32")
		$commandline += (SetFlag $Mac 		"WithMac")
		$commandline += (SetFlag $Android 	"WithAndroid")
		$commandline += (SetFlag $IOS 		"WithIOS")
		$commandline += (SetFlag $TVOS 		"WithTVOS")
		$commandline += (SetFlag $Linux 	"WithLinux")
		$commandline += (SetFlag $HTML5 	"WithHTML5")
		$commandline += (SetFlag $Switch 	"WithSwitch")
		$commandline += (SetFlag $PS4 		"WithPS4")
		$commandline += (SetFlag $XboxOne 	"WithXboxOne")
	}
	else
	{
		WriteInfo $helpMessage
		Die "Please specify your target platform"
	}

	#
	# Options
	#

	$commandline += (SetFlag $BuildDDC "WithDDC")
	$commandline += (SetFlag $SignExecutables "SignExecutables")
	$commandline += (SetFlag $EnableSymStore "EnableSymStore")

	if ($Clean)
	{
		$commandline += " -Clean"
	}

	#
	# Start Rocket builld
	#

	$buildInfo = "Building Unreal Engine Editor Distribution for Win64"

	# Log options
	$buildInfo += 
@"

 Options:
"@
	if ($BuildDDC)
	{
		$buildInfo += 
@"

  - Building DDC
"@
	}
	if ($SignExecutables)
	{
		$buildInfo += 
@"

  - Signing executebales
"@
	}
	if ($EnableSymStore)
	{
		$buildInfo += 
@"

  - Enable symbol store
"@
	}
	if ($Clean)
	{
		$buildInfo += 
@"

  - Rebuild
"@
	}
	if ($Zip)
	{
		$buildInfo += 
@"

  - Zip
"@
	}

	# Target platforms

	$buildInfo += 
@"

 Target Platforms:
"@
	if ($Win64 -or $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - Win64
"@
	}
	if ($Win32 -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - Win32
"@
	}
	if ($Mac -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - Mac
"@
	}
	if ($Android -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - Android
"@
	}
	if ($IOS -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - IOS
"@
	}
	if ($TVOS -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - TVOS
"@
	}
	if ($Linux -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - Linux
"@
	}
	if ($HTML5 -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - HTML5
"@
	}
	if ($Switch -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - Switch
"@
	}
	if ($PS4 -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - PS4
"@
	}
	if ($XboxOne -and -not $HostPlatformOnly)
	{
		$buildInfo += 
@"

  - XboxOne
"@
	}


	# Execute automation tool
	WriteHeader $buildInfo
	iex ("{0} {1}" -f $automationTool,$commandline)
}

#
# Post build options
#

if($BuildDDC)
{
	$engineName = "InstalledDDC"
}
else
{
	$engineName = "Engine\Windows"
}
$enginePath = [System.IO.Path]::GetFullPath(('{0}\LocalBuilds\{1}' -f $root, $engineName))
$engineZipPath = [System.IO.Path]::GetFullPath(('{0}\LocalBuilds\UnrealEngine_Win64.zip' -f $root))

if ($Zip)
{
	WriteHeader ("Zipping engine to: {0}" -f $engineZipPath )
	If (Test-Path $engineZipPath){
		Remove-Item $engineZipPath
	}
	Zip $enginePath $engineZipPath
}


#
# Sync engine build output to a given path
#

if ($output -ne "" -and $root -ne [String]::Empty)
{
	if ($NoPDBs)
	{
		robocopy $enginePath (Join-Path ($output) "Builds\UnrealEngine_Win64") /MIR /PURGE /XD Intermediate Source Documentation Saved /XF *.pdb
	}
	else
	{
		robocopy $enginePath (Join-Path ($output) "Builds\UnrealEngine_Win64") /MIR /PURGE /XD Intermediate Source Documentation Saved
	}
	
	if ($Zip)
	{
		robocopy $engineZipPath (Join-Path ($output) "Builds\UnrealEngine_Win64.zip") 
	}
}

}
finally
{
    pushd $currentPwd
}

