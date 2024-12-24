set VDMS_PATH=../deploy_liveview/target
set VDMS_TEMP=d:/Projects/vdms/temp
set VDMS_NODE=d:/Projects/vdms/node
set APP_NAME=deploy_liveview-0.0.1-SNAPSHOT-ep-application.zip
set STREAMBASE_HOME=c:\TIBCO\str\11.0

IF EXIST %VDMS_NODE%/tibco (
	rmdir /S /Q "%VDMS_NODE%/tibco" 
)
%STREAMBASE_HOME%\distrib\tibco\bin\epadmin install node nodename=A.LV-VDMS application=%VDMS_PATH%/%APP_NAME% nodedirectory=%VDMS_NODE%/tibco
