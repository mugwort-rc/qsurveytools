#!/usr/bin/env bash

lrelease qsurveytools_ja.ts

mv qsurveytools_ja.qm i18n/

pyrcc4 qsurveytools.qrc -o qsurveytools_rc.py
