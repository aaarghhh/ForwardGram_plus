# FORWARDGRAM PLUS (on STEROIDS)  


> This is a fully refactored and updated version of the original forwardgram, startingfrom the ground up. 
> It is a fork of the original forwardgram, and is not intended to replace it. 
> The workflow is the same as the original forwardgram, but it is base un multiple threads, one dedicated to the Discord bot.


# Telegram to Discord Message Bot — Forward Telegram Messages to Discord
### For other development or support, please contact me via discord  [@Aaarghhh](aaarghhh).


## Description
__Forwardgram Plus (on Steroids)__ is a free and open source, telegram to discord message bot. It was creating starting from the idea of [Forwardgram](https://github.com/kkapuria3/Telegram-To-Discord-Forward-Bot) and fully refactored. It enables one to forward messages from Multiple Telegram channels to one (or more) Telegram/Discord channels of your own. This python bot monitors multiple telegram channels. When a new message/entity is sent, it will parse the response and forward it to a discord channel using your own personalized bot. This steroid version support a native translation and presents a label indicating the source of the message.



### Dependencies

1. Python 3.6+ 
2. [Anaconda Python Console](https://www.anaconda.com/products/individual) (Optional, makes pip install debugging go away)
3. Create your own discord bot, add it to your server and retrive token. Follow Steps [here](https://www.writebots.com/discord-bot-token/).
4. Have a Telegram account with valid phone number


### Installing and Setup
1. Clone this repository
2. Open your choice of console (or Anaconda console) and navigate to cloned folder 
3. Run Command: `python3 -m pip install -r requirements.txt`.
4. Fill out a configuration file. An example file can be found at `config.yml-sample`. 


### First Run and Usage

1. Change the name of `config.yml-sample` to `config.yml` , setting up the following parameters:
```
- session_name: "forwardgram"
- telegram_api_id: 123456
- telegram_api_hash: "1234567890abcdef1234567890abcdef"
- the forward settings specifing the input and output channels and its details, follow the comments in the config.yml-sample file
```

#### Filling `config.yml` file

* Add your Telegram `api_id` and `api_hash` to config.yml | Read more [here](https://core.telegram.org/api/obtaining_api_id)
* Add your `discord_bot_token` to config.yml | Read more [here](https://www.writebots.com/discord-bot-token/)
* Edit the `config.yam` channel id. Remember when you remove extra discord channels you have to update code in `discord_messager.py` under comment `DISCORD SERVER START EVENT` and `MESSAGE SCREENER`

#### Editing `ForwardGram.py`

* No need to edit `ForwardGram.py` unless you want to change the way messages are sent to telegram channels.
* Multiple send/recieve telegram channels in `config.yml` can added without any code change.

2. Read the Version History and Changelog and below before running the script.

3. Run the command `python3 ForwardGram.py config.yaml`

```
***PLEASE NOTE:  In the first time initializing the script, you will be requried to validate your phone number using telegram API. This happens only at the first time (per session name).
```

## Authors who inspired me to create this project

* Karan Kapuria
* voidbar
* Sqble

## Author

* Aaarghhh


## Version History and Changelog

* December 2023 - 0.0.1 Initial Release 
	* ForwardGram encountered its steroid phase ( Full refactoring ). 

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
