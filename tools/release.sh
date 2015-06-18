#!/usr/bin/env bash

lrelease condition_ja.ts
lrelease lite_ja.ts

mv condition_ja.qm i18n/
mv lite_ja.ts i18n/

pyrcc4 condition.qrc -o condition_rc.py
pyrcc4 lite.qrc -o lite_rc.py
