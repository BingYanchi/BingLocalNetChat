rd/s/q build
rd/s/q dist

pyinstaller BingLocalNetChatClient.py --noconsole --icon="logo.ico"

copy logo.png dist\BingLocalNetChatClient
xcopy font .\dist\BingLocalNetChatClient\font /I
xcopy style .\dist\BingLocalNetChatClient\style /I