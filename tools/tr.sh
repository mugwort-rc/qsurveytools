#!/usr/bin/env bash

pylupdate4 qt/viewer/*.py qt/viewer/*.ui qt/viewer/lite/*.py qt/viewer/lite/*.ui -ts qt/viewer/surveytool.ts
pylupdate5 qt/viewer/xlhack/*.py qt/viewer/xlhack/*.ui -ts qt/viewer/xlhack/conditioneditor.ts
