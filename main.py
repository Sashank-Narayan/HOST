!pip install telebot
!pip install python-telegram-bot
!pip install requests
!pip install beautifulsoup4
!pip install SpeechRecognition
!pip install selenium
!apt-get update
!apt-get install -y chromium-chromedriver
!pip install openai


import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from io import StringIO
import pandas as pd
import requests
import speech_recognition as sr
import os
import subprocess
import openai
from PIL import Image
import io
from google.colab import auth
auth.authenticate_user()
import pandas as pd
from gspread_dataframe import set_with_dataframe
import gspread
from google.auth import default
from datetime import datetime, date
creds, _ = default()

%env OPENAI_API_KEY=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

from openai import OpenAI
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

# Initialize the Telegram bot
bot = telebot.TeleBot("6005955562:AAGIhcte5ztfmp6Vj-FwX-HxnVWWqrsp9p8")

# Function to scrape the product catalog based on the category URL
def scrape_catalog(url):
    with webdriver.Chrome(service=service, options=chrome_options) as driver:
        driver.get(url)
        products = driver.find_elements(By.CSS_SELECTOR, ".ProductCard")
        catalog = []
        for product in products:
            name = product.find_element(By.CSS_SELECTOR, ".ProductCard-link").text.strip()
            link = product.find_element(By.CSS_SELECTOR, ".ProductCard-link").get_attribute("href")
            image = product.find_element(By.CSS_SELECTOR, ".ProductCard-image img").get_attribute("src")
            description = product.find_element(By.CSS_SELECTOR, ".ProductCard-description").text.strip()
            catalog.append({"name": name, "link": link, "image": image, "description": description})
    return catalog

# Read the product data from the provided table
product_data = """
ProductName,Product Link,Category,Price
Wool Blend Funnel Neck Coat - Navy,https://johnlewis.scene7.com/is/image/JohnLewis/006461572?$fashion-ui$,Men's Clothing,195 £
White Stuff Lola Leather Camera Cross Body Bag - Grey Mlt,https://johnlewis.scene7.com/is/image/JohnLewis/006578825?$rsp-pdp-port-640$,Women's Accessories,52 £
Made in Italy Cashmere Crew Neck Jumper - Charcoal,https://johnlewis.scene7.com/is/image/JohnLewis/005431676?$rsp-pdp-port-640$,Men's Clothing,90 £
Unmade Copenhagen Zigga Silk Scarf - Black/Brown,https://johnlewis.scene7.com/is/image/JohnLewis/006652871?$rsp-pdp-port-1080$,Women's Accessories,59 £
Formal Leather Chelsea Boots - Black,https://johnlewis.scene7.com/is/image/JohnLewis/006546163?$rsp-pdp-port-640$, Men's Shoes,99 £
Crew Clothing Lightweight Nylon Quilted Jacket - Navy Blue,https://johnlewis.scene7.com/is/image/JohnLewis/006632729?$rsp-pdp-port-640$, Women's Clothing,49 £
Charles Tyrwhitt Paisley Silk Tie - Indigo Blue,https://johnlewis.scene7.com/is/image/JohnLewis/006798317?$rsp-pdp-port-640$,Men's Accessories,49 £
CREED Aventus For Her Eau de Parfum Spray - 75ml,https://johnlewis.scene7.com/is/image/JohnLewis/236047146?$rsp-pdp-port-640$,Women's Accessories,260 £
Dot Silk Tie - Burgundy,https://johnlewis.scene7.com/is/image/JohnLewis/004167574?$rsp-pdp-port-640$,Men's Clothing,26 £
"""

# product_df = pd.read_csv(StringIO(product_data))
gc = gspread.authorize(creds)
worksheet = gc.open("Copy of Purchase history").sheet1
complete_product_df = pd.DataFrame(data=worksheet.get_all_records())
product_df = pd.DataFrame(data=worksheet.get_all_records())
# product_df = pd.read_csv()
product_df = product_df.drop_duplicates('ProductName', keep = 'first')
product_name_global = ""
product_global_array = []
total_value_array = []
quantity = 0
total_value = 0

def convert_audio_to_wav(audio_file):
    wav_file = "audio.wav"
    subprocess.run(["ffmpeg", "-i", audio_file, "-ar", "16000", "-ac", "1", "-bits_per_raw_sample", "16", "-c:a", "pcm_s16le", wav_file], capture_output=True)
    return wav_file

# Function to convert speech to text
def convert_speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            return None

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    audio_file = requests.get(file_url)
    with open("audio.ogg", "wb") as file:
        file.write(audio_file.content)
    wav_file = convert_audio_to_wav("audio.ogg")
    text = convert_speech_to_text(wav_file)
    os.remove("audio.ogg")
    os.remove(wav_file)
    print(text)
    if text:
        bot.reply_to(message, f"You said: {text}")
        if "catalog" in text:
            send_catalog(message)
        elif "recommend" in text:
            recommend(message)
        elif "search" in text:
            search(message)
        elif "cart" in text:
            cart(message)
        else:
            # bot.reply_to(message, "Sorry, I couldn't convert your speech to text.")
            val = handle_message(text)
            if(val):
              bot.reply_to(message, val)
        # else:
        #     bot.reply_to(message, "Try Again")
    else:
        bot.reply_to(message, "Sorry, I couldn't convert your speech to text.")
        # handle_message(text)

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    # Get the file ID of the received image
    file_id = message.photo[-1].file_id

    # Get the file details and download the image
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    # Save the image to disk
    with open('image.jpg', 'wb') as f:
        f.write(downloaded_file)

    # Process the image as needed
    # Example: Perform image recognition, analysis, or any other desired operation
    # ...

    for index, row in product_df.iterrows():
      if("White" in row["Category"]):
        message_array = f"Product: {row['ProductName']}\n" + f"Price: {row['Price']} £\n\n"

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            telebot.types.InlineKeyboardButton("Buy", callback_data=f"addtocart_{row['ProductName']}"),
            telebot.types.InlineKeyboardButton("Keep browsing", callback_data="keep_browsing")
        )
        bot.send_photo(message.chat.id, photo=requests.get(row['Product Link']).content, caption=message_array, reply_markup = markup)
    # Reply to the user
    # bot.reply_to(message, "Image received and processed!")

# Handler for the "Show Catalog" button
@bot.message_handler(func=lambda message: message.text == "Show Catalog")
def send_catalog(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(telebot.types.InlineKeyboardButton("Men", callback_data="men"), telebot.types.InlineKeyboardButton("Women", callback_data="women"))
    bot.reply_to(message, "Please select a category:", reply_markup=markup)

# Handler for the "/start" command
@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(telebot.types.KeyboardButton("Catalog"), telebot.types.KeyboardButton("Search"))
    markup.add(telebot.types.KeyboardButton("Recommend"), telebot.types.KeyboardButton("Cart"))
    # markup.add(telebot.types.KeyboardButton("History"))
    bot.reply_to(message, "Welcome! How can I assist you today?", reply_markup=markup)

# @bot.callback_query_handler(func=lambda call: call.data == "end")
def end(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(telebot.types.KeyboardButton("Catalog"), telebot.types.KeyboardButton("Search"))
    markup.add(telebot.types.KeyboardButton("Recommend"), telebot.types.KeyboardButton("Cart"))
    # markup.add(telebot.types.KeyboardButton("History"))
    global product_global_array
    product_global_array = []
    total_value_array = []
    bot.reply_to(message, "Thank You for Purchasing With Us", reply_markup=markup)

def restart(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(telebot.types.KeyboardButton("Catalog"), telebot.types.KeyboardButton("Search"))
    markup.add(telebot.types.KeyboardButton("Recommend"), telebot.types.KeyboardButton("Cart"))
    # markup.add(telebot.types.KeyboardButton("History"))
    bot.reply_to(message, "Lets Continue Shopping ..", reply_markup=markup)

#On BUY PRODUCT
@bot.callback_query_handler(func=lambda call: call.data == "buy_small_lola_bag")
def buy_small_lola_bag(call):
    bot.reply_to(call.message, "You have successfully bought the Small Lola Bag!")

@bot.message_handler(func=lambda message: message.text == "Catalog")
def catalog(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("Women", callback_data="women"),
        telebot.types.InlineKeyboardButton("Men", callback_data="men")
    )
    bot.reply_to(message, "Please select a category:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Cart")
def cart(message):
    global product_name_global, quantity, total_value
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        telebot.types.InlineKeyboardButton("Checkout", callback_data="buy_product"),
    )
    message_array = ""
    print(product_name_global)
    if(product_name_global):
      count = 0
      for prod in product_global_array:
        message_array = message_array +  f"Cart Items : Product '{prod}' added to cart.\nQuantity: {quantity}\nTotal Value: {total_value_array[count]}£\n\n"
        count = count + 1
    else:
      message_array = f"Cart Items : Empty Cart"
    bot.reply_to(message, message_array , reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Search")
def search(message):
    bot.reply_to(message, "Speak Or Type Something to Search")

@bot.message_handler(func=lambda message: message.text == "Recommend")
def recommend(message):
    # image_url = 'https://assets.burberry.com/is/image/Burberryltd/B5E69F41-6CB5-463D-9762-A23FE338BC4E?$BBY_V2_SL_1x1$&wid=2500&hei=2500'
    # image = requests.get(image_url).content
    # recommendation_message = "Based on your previous buying history, we would like to recommend you the 'Jacquard Silk Tie' at a discount of 5% for the original price of 150 £."
    # markup = telebot.types.InlineKeyboardMarkup()
    # markup.row_width = 2
    # markup.add(
    #     # telebot.types.InlineKeyboardButton("Add to Cart", )
    #     telebot.types.InlineKeyboardButton("Buy", callback_data= f"addtocart_EKD Jacquard Silk Tie"),
    #     telebot.types.InlineKeyboardButton("Keep browsing", callback_data="keep_browsing")
    # )
    # bot.send_photo(message.chat.id, photo=image, caption=recommendation_message, reply_markup=markup)
    # bot.reply_to(message, photo = image, recommendation_message, reply_markup=markup)

    image_url = []
    image = []
    recommendation_message = []
    for index, row in complete_product_df.iterrows():
      print(row)
      if(row['Difference'] >= 100):
            # image_url[index] = row['Product Link']
            # image[index] = requests.get(image_url[index]).content
            # recommendation_message[index] = f"\nBased on your previous buying history, we would like to recommend you the {row['ProductName']} at a discount of 7% for the original price of 350 £."
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(
                telebot.types.InlineKeyboardButton("Buy", callback_data=f"addtocart_{row['ProductName']}"),
                telebot.types.InlineKeyboardButton("Keep browsing", callback_data="keep_browsing")
            )
            bot.send_photo(message.chat.id, photo=requests.get(row['Product Link']).content, caption=f"\nBased on your previous buying history, we would like to recommend you the {row['ProductName']} at a discount of {row['Discount']} for the original price of {row['Price']}£."
            , reply_markup=markup)


            # Recommend "Jacquard Silk Tie"
    # image_url_2 = 'https://assets.burberry.com/is/image/Burberryltd/C154C398-6162-4432-9F71-09659793AB45?$BBY_V2_SL_1x1$&wid=1023&hei=102'
    # image_2 = requests.get(image_url_2).content
    # recommendation_message_2 = f"\nBased on your previous buying history, we would like to recommend you the 'Small Lola Bag' at a discount of 7% for the original price of 350 £."
    # markup_2 = telebot.types.InlineKeyboardMarkup()
    # markup_2.row_width = 2
    # markup_2.add(
    #     telebot.types.InlineKeyboardButton("Buy", callback_data="addtocart_Small Lola Bag"),
    #     telebot.types.InlineKeyboardButton("Keep browsing", callback_data="keep_browsing")
    # )
    # bot.send_photo(message.chat.id, photo=image_2, caption=recommendation_message_2, reply_markup=markup_2)
    # bot.reply_to(message, recommendation_message_2, reply_markup=markup_2)


# Handler for the "Buy" button for the Small Lola Bag
@bot.callback_query_handler(func=lambda call: call.data == "buy_product")
def buy_product(call):
        delivery_message = bot.reply_to(call.message, f"How would you like to receive the products?\n\n"
                                                   f"1. Home Delivery (+£2)\n"
                                                   f"2. Store Pickup")
        bot.register_next_step_handler(delivery_message, process_delivery_option, product_name_global, quantity, total_value)    # Add the necessary logic to process the purchase

# Handler for the "Buy" button for the Jacquard Silk Tie
@bot.callback_query_handler(func=lambda call: call.data == "buy_jacquard_silk_tie")
def buy_jacquard_silk_tie(call):
    bot.reply_to(call.message, "You have successfully bought the Jacquard Silk Tie!")
    # Add the necessary logic to process the purchase

@bot.callback_query_handler(func=lambda call: call.data == "keep_browsing")
def keep_browsing(call):
    restart(call.message)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("Women", callback_data="women"),
        telebot.types.InlineKeyboardButton("Men", callback_data="men")
    )
    bot.reply_to(call.message, "Select The Products", reply_markup=markup)

products_men = product_df[product_df['Category'].str.contains("Men")]
total_products = len(products_men)
current_product_index = 0

products_women = product_df[product_df['Category'].str.contains("Women")]
total_products_women = len(products_women)
current_product_index_women = 0

def get_product_info(product):
    product_info = product.split(',')
    return {
        'name': product_info[0],
        'link': product_info[1],
        'category': product_info[2],
        'price': product_info[3]
    }

def get_current_product():
    return products_men.iloc[current_product_index]

# Handler for the "Men" button
@bot.callback_query_handler(func=lambda call: call.data == "men")
def men_category_list(call):
    men_category(call.message.chat.id)
    bot.answer_callback_query(call.id)

def men_category(chat_id, message_id = None):
    men_catalog = product_df[product_df['Category'].str.contains("Men")]
    response = "Products for Men:\n\n"
    product = get_current_product()
    product_message = f"Product Name: {product['ProductName']}\n" \
                      f"Category: {product['Category']}\n" \
                      f"Price: {product['Price']} £\n" \
                      f"Product Link: {product['Product Link']}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    if current_product_index > 0:
        back_button = telebot.types.InlineKeyboardButton("<< Back", callback_data='back')
        markup.add(back_button)
    if current_product_index < total_products - 1:
        next_button = telebot.types.InlineKeyboardButton("Next >>", callback_data='next')
        markup.add(next_button)
    markup.add(telebot.types.InlineKeyboardButton("Add to Cart", callback_data=f"addtocart_{product['ProductName']}"))
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=product_message, reply_markup=markup)
    else:
        bot.send_message(chat_id, product_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'next')
def next_product(call):
    global current_product_index
    if current_product_index < total_products - 1:
        current_product_index += 1
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    men_category(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def previous_product(call):
    global current_product_index
    if current_product_index > 0:
        current_product_index -= 1
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    men_category(call.message.chat.id)

def get_current_product_women():
    return products_women.iloc[current_product_index_women]

# Handler for the "Men" button
@bot.callback_query_handler(func=lambda call: call.data == "women")
def women_category_list(call):
    women_category(call.message.chat.id)
    bot.answer_callback_query(call.id)

def women_category(chat_id, message_id = None):
    men_catalog = product_df[product_df['Category'].str.contains("Women")]
    response = "Products for Women:\n\n"
    product = get_current_product_women()
    product_message = f"Product Name: {product['ProductName']}\n" \
                      f"Category: {product['Category']}\n" \
                      f"Price: {product['Price']} £\n" \
                      f"Product Link: {product['Product Link']}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    if current_product_index_women > 0:
        back_button = telebot.types.InlineKeyboardButton("<< Back", callback_data='back_women')
        markup.add(back_button)
    if current_product_index_women < total_products - 1:
        next_button = telebot.types.InlineKeyboardButton("Next >>", callback_data='next_women')
        markup.add(next_button)
    markup.add(telebot.types.InlineKeyboardButton("Add to Cart", callback_data=f"addtocart_{product['ProductName']}"))
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=product_message, reply_markup=markup)
    else:
        bot.send_message(chat_id, product_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'next_women')
def next_product(call):
    global current_product_index_women
    if current_product_index_women < total_products_women - 1:
        current_product_index_women += 1
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    women_category(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_women')
def previous_product(call):
    global current_product_index_women
    if current_product_index_women > 0:
        current_product_index_women -= 1
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    women_category(call.message.chat.id)

# Handler for the "Women" button
# @bot.callback_query_handler(func=lambda call: call.data == "women")
# def women_category(call):
#     women_catalog = product_df[product_df['Category'].str.contains("Women")]
#     response = "Products for Women:\n\n"
#     for _, product in women_catalog.iterrows():
#         response = ""
#         response += f"Name: {product['ProductName']}\n"
#         # response += f"Description: {product['Category']}\n"
#         response += f"Price: {product['Price']}\n"
#         # Send the image as a photo to the bot
#         image_url = product['Product Link']
#         image = requests.get(image_url).content
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.row_width = 1
#         markup.add(telebot.types.InlineKeyboardButton("Add to Cart", callback_data=f"addtocart_{product['ProductName']}"))
#         bot.send_photo(call.message.chat.id, photo=image, caption=response, reply_markup=markup)
#     bot.answer_callback_query(call.id)

size_message = ""

@bot.callback_query_handler(func=lambda call: call.data.startswith("addtocart_"))
def add_to_cart(call):
    product_name = call.data.split("_")[1]
    quantity_message = bot.reply_to(call.message, f"How many '{product_name}' do you want to add to your cart?")
    # size_message = bot.reply_to(call.message, f"What size of '{product_name}' do you want to add to your cart?")
    # print(size_message)
    bot.register_next_step_handler(quantity_message, process_size, product_name)

def process_size(message, product_name):
    quantity = message.text
    if("Tie" in product_name):
      size_message = bot.reply_to(message, f"What size of '{product_name}' do you want to add to your cart?\n\n1.7cm/2.8in wide")
    elif("BootsPrice" in product_name):
      size_message = bot.reply_to(message, f"What size of '{product_name}' do you want to add to your cart?\n\n1.35\n2.35.5\n3.36")
    elif("Parfum" in product_name):
      size_message = bot.reply_to(message, f"What size of '{product_name}' do you want to add to your cart?\n\n1.150ml\n2.100ml\n3.50ml")
    else:
      size_message = bot.reply_to(message, f"What size of '{product_name}' do you want to add to your cart?\n\n1.S\n2.M\n3.L")
    bot.register_next_step_handler(size_message, process_quantity, product_name, quantity)

# Function to process the quantity and calculate the total value
def process_quantity(message, product_name, quantity_count):
    try:
        global quantity, total_value, product_name_global, product_global_array, total_value_array
        product_name_global = product_name
        product_global_array.append(product_name)
        # quantity = message.text
        quantity = int(quantity_count)
        if quantity <= 0:
            bot.reply_to(message, "Quantity should be a positive number.")
            return
        product = product_df.loc[product_df['ProductName'] == product_name]
        price = product['Price'].iloc[0]
        total_value = price * quantity
        total_value_array.append(total_value)
        # bot.reply_to(message, f"Product '{product_name}' added to cart.\nQuantity: {quantity}\nTotal Value: {total_value}")
        markup_buy = telebot.types.InlineKeyboardMarkup()
        markup_buy.row_width = 1
        markup_buy.add(
            telebot.types.InlineKeyboardButton("Buy", callback_data="buy_product")
        )
        bot.reply_to(message, f"Product '{product_name}' added to cart.\nQuantity: {quantity}\nTotal Value: {total_value} £", reply_markup=markup_buy)
        if(product_name_global != 'Black Check Hoodie'):
          # bot.register_next_step_handler(message, buy_product, product_name, quantity, total_value)
          image_data = requests.get('https://cdna.lystit.com/520/650/n/photos/gilt/fbec82de/burberry-Black-Check-Hoodie.jpeg').content
          image = Image.open(io.BytesIO(image_data))
          image = image.resize((200, 200))
          recommendation_message = "We would like to suggest you the Black Check Hoodie at a discount of 3% for the original price of 350 £."
          markup = telebot.types.InlineKeyboardMarkup()
          markup.row_width = 2
          markup.add(
              telebot.types.InlineKeyboardButton("Add To Cart", callback_data= f"addtocart_Black Check Hoodie"),
              telebot.types.InlineKeyboardButton("Deny", callback_data="deny_small_lola_bag")
          )
          # bot.reply_to(message, recommendation_message, reply_markup=markup)
          bot.send_photo(message.chat.id, photo= image, caption=recommendation_message, reply_markup=markup)

        # bot.reply_to(recommendation_message, reply_markup=markup)

    except ValueError:
        bot.reply_to(message, "Invalid quantity. Please enter a number.")

def get_user_location(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="Share Location", request_location=True)
    # markup = telebot.types.InlineKeyboardMarkup()
    # button_cancel = telebot.types.InlineKeyboardButton(text="Cancel", callback_data="end")
    keyboard.add(button)
    # markup.add(button_cancel)
    bot.send_message(message.chat.id, "Please share your location:", reply_markup=keyboard)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("Confirm Order", callback_data="confirmed_order"),
        telebot.types.InlineKeyboardButton("Continue Shopping", callback_data="keep_browsing")
    )
    message_array = ""
    count = 0
    for prod in product_global_array:
        message_array = message_array +  f"Product '{prod}' added to cart.\n" + f"Quantity: {quantity}\n" + f"Delivery Option: Home Delivery\n" + f"Total Value: {total_value_array[count]} £\n\n"
        count = count + 1
    bot.reply_to(message, message_array,  reply_markup=markup)

# Handler for location updates
# @bot.message_handler(func=lambda message: message.location is not None)
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    # Process the user's location data here
    bot.send_message(message.chat.id, f"Your location: Latitude: {latitude}, Longitude: {longitude}")

#On BUY PRODUCT
@bot.callback_query_handler(func=lambda call: call.data == "confirmed_order")
def buy_small_lola_bag(call):
    bot.reply_to(call.message, "You have successfully placed the Order!\n Your Order ID is\n 6005955562:AAGIhcte5ztfmp6Vj-FwX-HxnVWWqrsp9p8")
    end(call.message)

def process_delivery_option(message, product_name, quantity, total_value):
    delivery_option = message.text.lower()
    if delivery_option == "1" or delivery_option == "home delivery":
        # total_value = int(total) + 2  # Add £2 for home delivery
        location = get_user_location(message)
        print(location)
    elif delivery_option == "2" or delivery_option == "store pickup":
        markup_store = telebot.types.InlineKeyboardMarkup()
        markup_store.row_width = 2
        markup_store.add(
            telebot.types.InlineKeyboardButton("Confirm Order", callback_data="confirmed_order"),
            telebot.types.InlineKeyboardButton("Continue Shopping", callback_data="keep_browsing")
        )
        bot.reply_to(message, f"Product '{product_name}' added to cart.\n"
                              f"Quantity: {quantity}\n"
                              f"Delivery Option: Store Pickup\n"
                              f"Total Value: {total_value} £", reply_markup = markup_store)
    else:
        bot.reply_to(message, "Invalid delivery option. Please choose either '1' or '2'.")

def generate_response(message):
	# Send the user message to ChatGPT and receive the AI-generated response
	# Make an API request to the OpenAI GPT-3.5 API using your OpenAI API key
  openai.api_key = os.getenv("OPENAI_API_KEY")
  content = message + "'of John Lewis and Partners'"
  # message_text = message + "Of Burberry"
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role":"user", "content": content}],
    	max_tokens=100,
    	temperature=0.7,
    	n=1,
    	stop=None,
      # size = "256x256"
	)
  return response.choices[0].message.content
  # image_url = response['data'][0]['url']
  # return image_url

# @bot.message_handler(func=lambda message: True)
def handle_message(message):
  print(message)

  # Get the user's message
  if(message):
    user_message = message + 'of John Lewis and Partners'

    # Generate an AI response using ChatGPT
    ai_response = generate_response(user_message)

    # Send the AI response back to the user
    # bot.reply_to(message, ai_response)
    print(ai_response)
    return ai_response


@bot.message_handler(func=lambda message: True)
def handle_message_query(message):
	# Get the user's message
  # print(message.text)
  user_message = message.text + 'of of John Lewis and Partners'

	# Generate an AI response using ChatGPT
  ai_response = generate_response(user_message)

	# Send the AI response back to the user
  bot.reply_to(message, ai_response)

# Start the bot
bot.polling()

#trending products
#available locations near me in uk
#discount products
#top children's products
#best seller products with price
#stores with big offers in london and discount percentage

