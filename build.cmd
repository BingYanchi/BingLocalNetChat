rd/s/q build
rd/s/q dist

pyinstaller BingLocalNetChatClient.py --icon="logo.ico"

copy logo.png dist\BingLocalNetChatClient
copy logo.ico dist\BingLocalNetChatClient
xcopy font .\dist\BingLocalNetChatClient\font /I
xcopy style .\dist\BingLocalNetChatClient\style /I