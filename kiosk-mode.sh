#!/bin/bash

while true; do
	chromium-browser --kiosk https://github.com --no-first-run --touch-events=enabled --fast --fast-start --disable-popup-blocking --disable-infobars --disable-session-crashed-bubble --disable-tab-switcher --disable-translate --enable-low-res-tiling
	sleep 10s;
done
