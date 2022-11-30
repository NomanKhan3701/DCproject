:load
start cmd /k python database_server.py y

start cmd /k python Cinemaserver.py 8000
start cmd /k python Cinemaserver.py 8001
start cmd /k python Cinemaserver.py 8002

start cmd /k python Cinemaserver.py 9000
start cmd /k python Cinemaserver.py 9001
start cmd /k python Cinemaserver.py 9002

start cmd /k python Cinemaserver.py 10000
start cmd /k python Cinemaserver.py 10001
start cmd /k python Cinemaserver.py 10002


:while
set /p close_server=Close/Reload all servers [y/n/r]?:
IF %close_server%==y ( echo Closing all servers...) & ( TASKKILL /IM cmd.exe ) ELSE ( IF %close_server%==r ( TASKKILL /IM cmd.exe) & (goto :load ) ELSE ( echo Servers still running...) & goto :while )

