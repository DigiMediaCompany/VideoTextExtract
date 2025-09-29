# Youtube audio extractor

Get the audio of a Youtube video in a desired language. Say you see a Youtube video with potential, 
you wanna clone the idea but in different language/voice for your own channel, this is the tool for you. 
Directly translate from original audio to desired lang/voice audio is a big challenge, 
so I take the work-around path and translate via subtitle.

This together with auto videos from [TODO](https://github.com/username/awesome-tool) (Subway Surfer video generator)
and [TODO](https://github.com/username/awesome-tool) (Roblox video generator) allows you to build/test mass amount
of channels/ideas


## 🚀 Features
- Download Youtube subtitle in the following priority
  - Manual subtitle in the desired language
  - Auto subtitle in the desired language
  - Manual subtitle in a central language (probably en in most cases)
  - Auto subtitle in a central language
  - If no subtitle available, download the audio and transcribe it into central language
- Translate the file via GPT if the subtitle file is not in desired language
- Subtitle to audio


## 📦 Installation

- Install [Get cookies.txt (Chrome Extension)](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (or any safe cookie export tool). 
Export the Youtube cookie, rename to "cookies.txt" and place it in the root folder. 
Skipping this step may get you 429 error. Note that cookie constantly needs to be updated
- Install [FFmpeg](https://ffmpeg.org/)
- Setup desired/central language and target Youtube video
- Setup .env
- Run
```bash
pip install -r requirements.txt
py main.py
```

## Todo

- Auto-fetching cookies
- More options for bot detection
