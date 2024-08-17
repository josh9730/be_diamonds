## Installer Command

need to add `smartsheet.sheets` and `smartsheet.models` to hidden imports on .spec

- `hiddenimports=['smartsheet.sheets', 'smartsheet.models']`

#### PC

- `pyinstaller diamonds.py --name diamonds1.4 --onefile --add-data="C:/Users/jdick/AppData/Local/pypoetry/Cache/virtualenvs/be-diamonds-TXN2MRGH-py3.12/Lib/site-packages/nicegui;nicegui"`

#### Mac

- `pyinstaller diamonds.py --name diamonds1_4 --onefile --add-data="/Users/jdickman/Library/Caches/pypoetry/virtualenvs/be-diamonds-UpwU9Q9k-py3.10/lib/python3.10/site-packages/nicegui:nicegui"`

OR

- change `name` field in .spec
- `pyinstaller diamonds.spec`
