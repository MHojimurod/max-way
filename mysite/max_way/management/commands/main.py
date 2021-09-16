import os.path
from django.core.management.base import BaseCommand
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, messagequeue as mq)
from telegram.utils.request import Request
from ... import servise
from . import command
from datetime import datetime
import json


def check_user_data(func):
    def inner(update, context):
        chat_id = update.message.from_user.id
        user = servise.get_user_id(chat_id)
        state = context.user_data.get("state", 0)
        if state == 0 or state == 5:
            if user:
                if not user['first_name']:
                    update.message.reply_text(
                        text='Ismingizni kiriting',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    context.user_data['state'] = 1
                    return False
                elif not user['last_name']:
                    update.message.reply_text(
                        text='Familyangizni kiriting',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    context.user_data['state'] = 2
                    return False
                elif not user['phone']:
                    buttons = [[KeyboardButton(text='Contact', request_contact=True)]]
                    update.message.reply_text(
                        text='Raqamni kiriting:',
                        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    )
                    context.user_data['state'] = 3
                    return False
                else:
                    context.user_data['state'] = 4
                    return func(update, context)

            else:
                update.message.reply_text(text='Assalom alekum Max Way ning rasmiy botiga hush kelibsz iltimos ismingizni kiriting')
                servise.create_user(chat_id,datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
                context.user_data['state'] = 1
                return False
        else:
            return func(update, context)

    return inner


def check_user_state(update, context):
    try:
        chat_id = update.message.from_user.id
    except:
        chat_id = update.callback_query.message.chat_id
    user = servise.get_user_id(chat_id)
    if user:
        if not user['first_name']:
            update.message.reply_text(text='Ismingizni kiriting',reply_markup=ReplyKeyboardRemove())
            context.user_data['state'] = 1
        elif not user['last_name']:
            update.message.reply_text(
                text='Familyangizni kiriting',
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data['state'] = 2
        elif not user['phone']:
            buttons = [[KeyboardButton(text='Contact', request_contact=True)]]
            update.message.reply_text(
                text='Raqamni kiriting:',
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
            context.user_data['state'] = 3

        else:
            buttons = [[KeyboardButton('Buyurtma berish'),KeyboardButton('Sozlamalar')],
            [KeyboardButton('Savatcha'),KeyboardButton("Buyurtmalarim")]]
            try:
                update.message.reply_text(text='Menu',
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,one_time_keyboard=True))
            except:
                update.callback_query.message.reply_text(text='Menu',
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,one_time_keyboard=True))
           

    else:
        servise.create_user(chat_id,datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        update.message.reply_text(text='Assalom alekum Max Way ning rasmiy botiga hush kelibsz iltimos ismingizni kiriting')
        context.user_data['state'] = 1


@check_user_data
def start_handler(update, context):
    chat_id = update.message.from_user.id
    buttons = [[KeyboardButton('Buyurtma berish'),KeyboardButton('Sozlamalar')],
            [KeyboardButton('Savatcha'),KeyboardButton('Buyurtmalarim')]]
    update.message.reply_text(text='Menu',
                              reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,one_time_keyboard=True))

@check_user_data
def message_handler(update, context):
    chat_id = update.message.from_user.id
    msg = update.message.text
    message_id = update.message.message_id
    state = context.user_data.get("state", 0)
    cart = context.user_data.get("cart", {})
    if msg == 'Buyurtma berish':
        categories = servise.get_category()
        command.inline_category(categories,update,context)
        chat_id = update.message.from_user.id
    elif msg == 'Sozlamalar':
        user = servise.get_user_id(chat_id)
        buttons = [[InlineKeyboardButton(user['first_name'],callback_data='first_name'),InlineKeyboardButton(user['last_name'],callback_data='last_name')],
        [InlineKeyboardButton(user['phone'],callback_data='phone_number')]]
        update.message.reply_text(
            text=f"Ismingiz: {user['first_name']}\nFamilyangiz: {user['last_name']}\nTelefon raqamingiz: {user['phone']}",
            reply_markup=InlineKeyboardMarkup(buttons))
    elif msg == 'Savatcha':
        print(cart)
        if cart != {}:

            buttons = []
            text=""
            for key in cart.items():
                product = servise.get_product_by_id(key[0])

                text += f"{product['name']}: <b>{int(product['price']*int(key[1]))}</b> so'm\n"

                buttons.append([InlineKeyboardButton(f"{product['name']} ❌",callback_data=f'delete_{key[0]}_bbb')])

            buttons.append([InlineKeyboardButton('Savatchani tozalash',callback_data='delete_clear_cart'),
                InlineKeyboardButton('Buyurtma berish',callback_data='order_product_blabla')])
                
            context.bot.send_message(
            text=text,
            chat_id=chat_id,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='HTML'
            )
        else:
            update.message.reply_text(text='Afsus savatchada hech narsa yo\'q')
    elif msg == 'Buyurtmalarim':
        user_id = servise.get_user_id(chat_id)['id']
        print(user_id)
        orders =servise.product_of_order(user_id)
        text=''
        
        for i in orders:
            total_price = 0
            if i['status'] == 1:
                
                for key,val in eval(i['products']).items():
                    product = servise.get_product_by_id(int(key))
                    text += f"{product['name'] } ✖ {val} = {i['total_price']} so'm\n"
                    # total_price += i['total_price']
                text+= f"Buyurtma berildi ⏰\n\n"
                
            elif i['status'] == 2:
                for key,val in eval(i['products']).items():
                    product = servise.get_product_by_id(int(key))
                    text += f"{product['name'] } ✖ {val} = {i['total_price']} so'm\n"
                    # total_price += i['total_price']
                text+= f"Yetkazib berildi ✅\n\n"
                
            elif i['status'] == 3:
                for key,val in eval(i['products']).items():
                    product = servise.get_product_by_id(int(key))
                    text += f"{product['name'] } ✖ {val} = {i['total_price']} so'm\n"
                    # total_price += i['total_price']
                text+= f"Buyurtma bekor qilindi ❌\n\n"
               

        update.message.reply_text(text=text)



    elif state == 1:
        servise.update_user(state, chat_id, msg)
        check_user_state(update, context)

    elif state == 2:
        servise.update_user(state, chat_id, msg)
        check_user_state(update, context)

    elif state == 3:
        servise.update_user(state, chat_id, msg)
        check_user_state(update, context)
    elif state == 4:
        servise.update_user(state,chat_id, msg)
        user = servise.get_user_id(chat_id)
        total_price=0
        cart = context.user_data["cart"]
        for key in cart.items():
            product = servise.get_product_by_id(key[0])
            total_price+= int(product['price'])*int(key[1])
        servise.create_order(user['id'],json.dumps(cart),1,total_price,datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        context.user_data["cart"] ={}
        check_user_state(update,context)

    else:
        start_handler(update,context)

def inline_handler(update,context):
    query = update.callback_query
    chat_id = update.callback_query.message.chat_id
    message_id = query.message.message_id
    data_split = query.data.split("_")
    # state = context.user_data.get("state", 0)
    if data_split[0] == 'category':
        products = servise.get_product_by_category_id(data_split[1])
        command.inline_product(products,update,context,chat_id,message_id)

    elif data_split[0] == 'back':
        command.back(data_split,update,context,chat_id,message_id)

    elif data_split[0] == 'product':
       command.one_product(data_split,update,context,chat_id,message_id)

    elif data_split[1] == "-":
        count = int(data_split[2])
        if count > 1:
            count -= 1
            command.product_amount(data_split,update, context, chat_id, message_id, count)
        elif count>=1:
            command.product_amount(data_split,update, context, chat_id, message_id, 1)

    elif data_split[1] == "+":
        # print(data_split[1])
        count = int(data_split[2])
        count += 1
        command.product_amount(data_split,update, context, chat_id, message_id, count)

    elif data_split[0] == 'add':

        cart = context.user_data.get("cart", {})
        cart[f"{data_split[2]}"] = cart.get(f"{data_split[2]}", 0) + int(data_split[1])
        context.user_data["cart"] = cart
        buttons = []
        text=""
        for key in cart.items():
            product = servise.get_product_by_id(key[0])

            text += f"{product['name']}: <b>{int(product['price']*int(key[1]))}</b> so'm\n"

            buttons.append([InlineKeyboardButton(f"{product['name']} ❌",callback_data=f'delete_{key[0]}_bbb')])

        buttons.append([InlineKeyboardButton('Back',callback_data='back_category_list'),
            InlineKeyboardButton('Buyurtma berish',callback_data='order_product_blabla')])
            
        context.bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
        )


    elif data_split[0] == 'delete':
        cart = context.user_data.get("cart", {})
        if data_split[1] == 'clear':
            context.user_data["cart"] = {}
            query.message.delete()
            query.message.reply_text(text='Savatcha bo\'shatildi')
        else:
            cart.pop(data_split[1])
            context.user_data["cart"] = cart
            print(context.user_data["cart"])
            text =''
            buttons = []
            try:
                for key in cart.items():
                    product = servise.get_product_by_id(key[0])

                    text += f"{product['name']}: <b>{int(product['price']*int(key[1]))}</b> so'm\n"

                    buttons.append([InlineKeyboardButton(f"{product['name']} ❌",callback_data=f'delete_{key[0]}_bbb')])
                buttons.append([InlineKeyboardButton('Back',callback_data='back_category_list'),InlineKeyboardButton('Zakaz',callback_data='order_product_blabla')])
                
            except:
                text = "Savatcha bo'sh ",
                buttons.append([InlineKeyboardButton('Back',callback_data='back_category_list')])
        
        try:
            context.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode='HTML'
                )
        except:
            query.message.delete()
            print(text)
            print(buttons)
            context.bot.send_message(
                text=text,
                chat_id=chat_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode='HTML')


    elif data_split[0] == 'order':
        query.message.delete()
        button = [[KeyboardButton('Location',request_location=True)]]
        query.message.reply_text(
            text="qayerga yetkazib berish kerak lokatsiyani jo'nating yoki joylashgan joyingizni yozib yuboring",
            reply_markup=ReplyKeyboardMarkup(button,resize_keyboard=True))
        context.user_data['state'] = 4
        
    elif data_split[0] in ['first','last','phone']:
        query.message.delete()
        if data_split[0] == 'first':
            query.message.reply_text(text='Ismingizni kiriting')
            context.user_data['state'] = 1
        elif data_split[0] == 'last':
            query.message.reply_text(text='Familyangizni kiriting')
            context.user_data['state'] = 2
        elif data_split[0]  == 'phone':
            button = [[KeyboardButton('Contact',request_contact=True)]]
            query.message.reply_text(text='raqamingizni yuboring',reply_markup=ReplyKeyboardMarkup(button,resize_keyboard=True)
                )
            context.user_data['state'] =3

        
        
def contact_handler(update,context):
    chat_id = update.message.from_user.id
    contact = update.message.contact.phone_number
    state = context.user_data.get('state', 0)
    if state == 3:
        servise.update_user(state, chat_id, contact)
    check_user_state(update, context)


def location_handler(update,context):
    chat_id = update.message.from_user.id
    location = update.message.location
    state = context.user_data.get('state', 0)
    if state == 4:
        servise.update_user(state, chat_id, str(location))
        user = servise.get_user_id(chat_id)
        total_price=0
        cart = context.user_data["cart"]
        for key in cart.items():
            product = servise.get_product_by_id(key[0])
            total_price+= int(product['price'])*int(key[1])
        servise.create_order(user['id'],json.dumps(cart),1,total_price,datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        context.user_data["cart"] ={}
    check_user_state(update, context)


class Command(BaseCommand):


    def handle(self, *args, **kwargs):

        updater = Updater("1586864492:AAG7nucH0ydgsEG5v80xp1EZ1y9GQ0-umJE")

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start_handler))
        dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
        dispatcher.add_handler(CallbackQueryHandler(inline_handler))
        dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
        dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
        # dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))
        # dispatcher.add_handler(MessageHandler(Filters.document.mime_type("image/jpeg"), image_handler))

        updater.start_polling()
        updater.idle()