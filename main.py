import discord
import json
import requests

color = 0xFF6500
err_color = 0xFF0000
key_features = {
  'temp':'Temperature',
  'feels_like':'Feels Like',
  'temp_max':'Maximum Temperature',
  'temp_min':'Minimum Temperature',
}

key_features_forecast = {
  'temp':'Temperature',
  'feels_like':'Feel Like',
  'temp_max':'Max Temp',
  'temp_min':'Min Temp'
}

def check_value_exist(test_dict, value):
    do_exist = False
    for key, val in test_dict.items():
        if str(val).endswith(value):
            do_exist = True
    return do_exist

def next_two_days_data(data):
  dict = []
  list = data['list']
  for d in list:
    if check_value_exist(d, "00:00:00"):
      date = d['dt_txt'].replace(" 00:00:00",'')
      d = d['main']
      del d['grnd_level']
      del d['humidity']
      del d['pressure']
      del d['sea_level']
      del d['temp_kf']
      d['Date'] = date
      dict.append(d)
  return dict

def parse_data(data):
  data = data['main']
  del data['humidity']
  del data['pressure']
  return data

def weather_message(data, location):
  location = location.title()
  message = discord.Embed(title=f"{location} Weather", description=f"Here is the weather data for {location}.",color=color)
  for key in data:
    message.add_field(name=key_features[key],value=str(data[key]),inline=False)
  return message

def forecast_message(dict, location):
  location = location.title()
  message = discord.Embed(title="Next Two Days Weather Forecast", description=f"Here is the weather forecast data of next two days for {location}.",color=color)
  for d in dict:
    message.add_field(name="Date",value=str(d['Date']),inline=False)
    for key in d:
      if key != 'Date':
        message.add_field(name=key_features_forecast[key],value=str(d[key]),inline=True)
  return message

def error_message(location):
  location = location.title()
  return discord.Embed(title='Error', description=f"There was an error retrieving weather data for {location}.",color=err_color)
  

client = discord.Client()

token = "OTk3ODM5NjgzODg5NDE0Mjg1.GtAWa7.JkfYJhbqx7Q8LIlb_QiQ9K1AQvCeLarkm-sa68"
api_key = "23aa513e231ad565af58e636729d8307"
command_prefix = "w."
client = discord.Client()
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{command_prefix}[location]"))

@client.event
async def on_message(message):
  if message.author != client.user and message.content.startswith(command_prefix):
    location = message.content.replace(command_prefix, '').lower()
    if len(location) >= 1:
      url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&cnt=12&appid={api_key}&units=metric"
      try:
        newData = json.loads(requests.get(url).content)
        dict = next_two_days_data(newData)
      except KeyError:
        await message.channel.send(embed=error_message(location))
      url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
      try:
        data = json.loads(requests.get(url).content)
        data = parse_data(data)
        await message.channel.send(embed=weather_message(data, location))
        await message.channel.send(embed=forecast_message(dict, location))
      except KeyError:
        pass


client.run(token)