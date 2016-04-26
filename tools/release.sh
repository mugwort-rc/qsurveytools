#!/usr/bin/env bash

lrelease checker_ja.ts
lrelease condition_ja.ts
lrelease lite_ja.ts
lrelease generator_ja.ts

mv checker_ja.qm i18n/
mv condition_ja.qm i18n/
mv lite_ja.qm i18n/
mv generator_ja.qm i18n/

pyrcc4 checker.qrc -o checker_rc.py
pyrcc4 condition.qrc -o condition_rc.py
pyrcc4 lite.qrc -o lite_rc.py
pyrcc4 generator.qrc -o generator_rc.py
