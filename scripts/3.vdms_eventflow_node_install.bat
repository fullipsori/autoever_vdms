set VDMS_PATH=../deploy_eventflow/target
set VDMS_TEMP=d:/Projects/vdms/temp
set VDMS_NODE=d:/Projects/vdms/node
set APP_NAME=deploy_eventflow-0.0.1-SNAPSHOT-ep-application.zip
set STREAMBASE_HOME=c:\TIBCO\str\11.0
IF EXIST %VDMS_NODE%/tibco/A.EF-VDMS (
	rmdir /S /Q "%VDMS_NODE%/tibco/A.EF-VDMS"
)
%STREAMBASE_HOME%\distrib\tibco\bin\epadmin install node nodename=A.EF-VDMS application=%VDMS_PATH%/%APP_NAME% nodedirectory=%VDMS_NODE%/tibco
